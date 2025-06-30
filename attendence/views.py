from django.shortcuts import render, redirect
from .forms import PeriodForm
from .models import Period
from django.utils import timezone
from django.shortcuts import render
from django.db.models import Q
from .models import attendance, Employee, StudentDatabase, StudentAttendance
 
def attendance_dashboard(request):
    today = timezone.localdate()
 
    # ================== Faculty Attendance ==================
    total_staff = Employee.objects.count()
    staff_attendance_today = attendance.objects.filter(date=today)
 
    staff_present = staff_attendance_today.filter(status='Present').count()
    staff_late = staff_attendance_today.filter(status='Late').count()
    staff_present_or_late = staff_present + staff_late
 
    staff_attendance_rate = (staff_present_or_late / total_staff * 100) if total_staff else 0
 
    # ================== Student Attendance ==================
    total_students = StudentDatabase.objects.count()
    student_attendance_today = StudentAttendance.objects.filter(attendance_date=today)
 
    # Get unique students who have at least one attendance record today
    distinct_students = student_attendance_today.values('admission_no').distinct()
 
    student_present = set()
    student_late = set()
 
    for entry in distinct_students:
        admission_no = entry['admission_no']
        statuses = list(
            student_attendance_today.filter(admission_no=admission_no).values_list('status', flat=True)
        )
 
        if 'present' in statuses:
            student_present.add(admission_no)
 
        if 'late' in statuses:
            student_late.add(admission_no)
 
    # Combine both sets to avoid double-counting students
    student_present_or_late = student_present.union(student_late)
 
    student_attendance_rate = (len(student_present_or_late) / total_students * 100) if total_students else 0
 
    # ================== Combined Totals ==================
    total_people = total_staff + total_students
    total_present = staff_present + len(student_present - student_late)  # avoid double count
    total_late = staff_late + len(student_late)
    total_present_or_late = staff_present_or_late + len(student_present_or_late)
 
    overall_attendance_rate = (total_present_or_late / total_people * 100) if total_people else 0
 
 
   # ========== Low Attendance Alert (all students) ==========
    all_students = StudentDatabase.objects.all()
    low_attendance_students = []
 
    for student in all_students:
        total_classes = StudentAttendance.objects.filter(admission_no=student.admission_no).count()
        present_count = StudentAttendance.objects.filter(
            admission_no=student.admission_no,
            status__in=['present', 'late']
        ).count()
 
        if total_classes > 0:
            percentage = (present_count / total_classes) * 100
            if percentage < 75:
                low_attendance_students.append({
                    'name': student.student_name,
                    'roll_no': student.admission_no,
                    'percentage': round(percentage, 2)
                })
 
    context = {
        # Existing dashboard context...
        'student_present': len(student_present),
        'student_late': len(student_late),
        'student_attendance_rate': round(student_attendance_rate, 1),
        'total_students': total_students,
        'total_staff': total_staff,
        'staff_present': staff_present,
        'staff_late': staff_late,
        'staff_attendance_rate': round(staff_attendance_rate, 1),
        'total_people': total_people,
        'total_present': total_present,
        'total_late': total_late,
        'overall_attendance_rate': round(overall_attendance_rate, 1),
 
        # Add this:
        'low_attendance_students': low_attendance_students,
    }
 
    return render(request, 'attendence/attendance_dashboard.html', context)
 
   



def period_list(request):
    """
    Display all periods with an option to add a new one via a '+' button.
    """
    periods = Period.objects.all()
    return render(request, 'attendence/period_list.html', {'periods': periods})


from django.shortcuts import render, redirect
from .models import Period
# from master.models import Subject


def add_period(request):
    # subjects = Subject.objects.all()  # get all subjects for dropdown

    if request.method == 'POST':
        name = request.POST.get('name')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        is_extra = request.POST.get('is_extra') == 'on'

        # Basic validation (you can expand as needed)
        if name and start_time and end_time:
            period = Period(
                name=name,
                start_time=start_time,
                end_time=end_time,
                is_extra=is_extra
            )
            period.save()
            return redirect('period_list')  # replace with your URL name

    return render(request, 'attendence/add_period.html', {
        'subjects': subjects,
    })

from django.http import JsonResponse
from master.models import Employee
from django.shortcuts import render, redirect
from .models import attendance, attendancesettings
from .forms import AttendanceForm, AttendanceSettingsForm
from .utils import calculate_status

def employee_detail_api(request, pk):
    emp = Employee.objects.get(pk=pk)
    return JsonResponse({
        'department': emp.department,
        'emp_code': emp.emp_code,
    })

from django.contrib import messages  # Optional: for success or error alerts
from django.shortcuts import get_object_or_404

def attendance_entry(request):
    settings = attendancesettings.objects.first()

    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            att = form.save(commit=False)
            att.status = calculate_status(att.check_in, settings)
            att.save()
            messages.success(request, "Attendance recorded successfully.")  # Optional UI feedback
            return redirect('attendance_list')
        else:
            # Form has errors (e.g., duplicate employee for today) — they'll be shown in template
            pass
    else:
        form = AttendanceForm()

    return render(request, 'attendence/attendance_form.html', {'form': form})

def attendance_edit(request, pk):
    record = get_object_or_404(attendance, pk=pk)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('attendance_list')
    else:
        form = AttendanceForm(instance=record)
    return render(request, 'attendence/attendance_form.html', {'form': form, 'mode': 'edit'})

from django.shortcuts import render, get_object_or_404


def attendance_view(request, pk):
    record = get_object_or_404(attendance, pk=pk)
    form = AttendanceForm(instance=record)

    # Disable all fields in view mode
    for field in form.fields.values():
        field.widget.attrs['disabled'] = True

    return render(request, 'attendence/attendance_form.html', {
        'form': form,
        'mode': 'view',
        'attendance': record  # 🔄 Fixed variable name
    })




# def attendance_delete(request, pk):
#     record = get_object_or_404(attendance, pk=pk)
#     record.delete()
#     messages.success(request, "Attendance record deleted successfully.")
#     return redirect('attendance_list')




from django.db.models import Q
from master.models import Employee  # Make sure it's imported

def attendance_list(request):
    records = attendance.objects.select_related('employee').all().order_by('-date')

    # Filtering by date (from GET params)
    filter_date = request.GET.get('date')
    if filter_date:
        records = records.filter(date=filter_date)

    # Filtering by department (from GET params)
    filter_dept = request.GET.get('department')
    if filter_dept:
        records = records.filter(employee__department=filter_dept)

    # Get all unique departments for the dropdown
    departments = Employee.objects.values_list('department', flat=True).distinct()

    form = AttendanceForm()

    return render(request, 'attendence/attendance_list.html', {
        'records': records,
        'form': form,
        'departments': departments,  # for dropdown in template
    })

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from .models import attendance  # Replace with your model

def attendance_delete(request, pk):
    attendance_obj = get_object_or_404(attendance, pk=pk)
    attendance_obj.delete()
    return redirect('attendance_list')





def attendance_settings_view(request):
    settings, created = attendancesettings.objects.get_or_create(pk=1)
    if request.method == "POST":
        form = AttendanceSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            return redirect('attendance_settings_view')
    else:
        form = AttendanceSettingsForm(instance=settings)
    return render(request, 'attendence/attendance_settings.html', {'form': form})

from django.shortcuts import render
from django.db.models import Count, Q
from .models import attendance, StudentAttendance
from datetime import date, timedelta
 
def attendance_report(request):
    report_type = request.GET.get('report_type')
    category = request.GET.get('category')
    results = {}
 
    today = date.today()
    start_date = today
 
    if report_type == 'weekly':
        start_date = today - timedelta(days=7)
    elif report_type == 'monthly':
        start_date = today.replace(day=1)
    elif report_type == 'semester':
        start_date = today - timedelta(days=180)
    elif report_type == 'daily':
        start_date = today
 
    if report_type and category:
        if category in ['staff', 'both']:
            staff_qs = attendance.objects.filter(date__range=(start_date, today))
 
            total = staff_qs.count()
            unique_employees = staff_qs.values('employee').distinct().count()
            avg_staff_attendance = total / unique_employees if unique_employees else 0
 
            best_department = (
                staff_qs.values('employee__department')
                .annotate(count=Count('id'))
                .order_by('-count')
                .first()
            )
 
            results['Average Staff Attendance'] = f"{round(avg_staff_attendance, 2)} per staff"
            results['Most Punctual Department'] = best_department['employee__department'] if best_department else "N/A"
 
        if category in ['student', 'both']:
            student_qs = StudentAttendance.objects.filter(attendance_date__range=(start_date, today))
 
            total_sessions = student_qs.count()
            attended_sessions = student_qs.filter(Q(status='present') | Q(status='late')).count()
 
            avg_student_attendance = (attended_sessions / total_sessions) * 100 if total_sessions else 0
 
            # Most punctual class
            most_punctual_class = (
                student_qs
                .filter(Q(status='present') | Q(status='late'))
                .values('course')
                .annotate(punctual_count=Count('id'))
                .order_by('-punctual_count')
                .first()
            )
 
            results['average_student_attendance'] = round(avg_student_attendance, 1)
            results['most_punctual_class'] = most_punctual_class['course'] if most_punctual_class else "N/A"
 
 
    return render(request, 'attendence/attendance_report.html', {
        'report_type': report_type,
        'category': category,
        'results': results,
    })
 



from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q  # ✅ required for complex filters
from datetime import date  # ✅ THIS is required for date.today()

from master.models import Course, Subject ,StudentDatabase
from .models import StudentAttendance




def student_attendance_list(request):
    attendance_records = StudentAttendance.objects.all().order_by('-attendance_date')

    # Filters
    course_filter = request.GET.get('course')
    subject_filter = request.GET.get('subject')
    date_filter = request.GET.get('date')
    search_query = request.GET.get('search')

    if course_filter:
        attendance_records = attendance_records.filter(course=course_filter)
    if subject_filter:
        attendance_records = attendance_records.filter(subject=subject_filter)
    if date_filter:
        attendance_records = attendance_records.filter(attendance_date=date_filter)
    if search_query:
        attendance_records = attendance_records.filter(
            Q(student_name__icontains=search_query) |
            Q(admission_no__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(attendance_records, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'attendence/student_attendance_list.html', {
        'page_obj': page_obj,
        'courses': Course.objects.all(),
        'subjects': Subject.objects.all(),
        'course_filter': course_filter,
        'subject_filter': subject_filter,
        'date_filter': date_filter,
        'search_query': search_query
    })


def student_attendance_form_view(request):
    courses = Course.objects.all().order_by('name')
    subjects = []
    student_subject_pairs = []
    selected_subject = None
    students = []
    selected_course = None
    selected_course_id = None
    selected_subject_id = None
    error_message = None

    if request.method == "POST":
        selected_course_id = request.POST.get('course')
        selected_subject_id = request.POST.get('subject')
        attendance_date = request.POST.get("attendance_date")
        form_action = request.POST.get("form_action")

        if selected_course_id:
            selected_course = Course.objects.get(id=selected_course_id)
            subjects = Subject.objects.filter(course=selected_course).order_by('semester_number')

        if selected_course_id and selected_subject_id:
            selected_subject = Subject.objects.get(id=selected_subject_id)
            students = StudentDatabase.objects.filter(course=selected_course.name)

            for student in students:
                subject_name = selected_subject.name
                total_classes = StudentAttendance.objects.filter(
                    admission_no=student.admission_no,
                    subject=subject_name
                ).count()
                present_count = StudentAttendance.objects.filter(
                    admission_no=student.admission_no,
                    subject=subject_name
                ).filter(Q(status='present') | Q(status='late')).count()
                percentage = (present_count / total_classes * 100) if total_classes > 0 else 0

                student_subject_pairs.append({
                    'student': student,
                    'student_userid': student.student_userid,
                    'subject': selected_subject,
                    'attendance_percentage': round(percentage, 2)
                })

            # Handle Save Logic
            if form_action == "submit_attendance":
                if not attendance_date:
                    error_message = "Attendance date is required."
                else:
                    subject_name = selected_subject.name
                    faculty_name = str(selected_subject.faculty)
                    course_name = selected_course.name

                    for student in students:
                        admission_no = student.admission_no
                        student_name = student.student_name
                        student_userid = student.student_userid

                        status = request.POST.get(f"status_{admission_no}")
                        remarks = request.POST.get(f"remarks_{admission_no}")

                        if status:
                            record, created = StudentAttendance.objects.update_or_create(
                                admission_no=admission_no,
                                subject=subject_name,
                                attendance_date=attendance_date,
                                defaults={
                                    'course': course_name,
                                    'faculty_name': faculty_name,
                                    'student_name': student_name,
                                    'student_userid': student_userid,
                                    'status': status,
                                    'remarks': remarks or '',
                                }
                            )

                            total_classes = StudentAttendance.objects.filter(
                                admission_no=admission_no,
                                subject=subject_name
                            ).count()
                            present_count = StudentAttendance.objects.filter(
                                admission_no=admission_no,
                                subject=subject_name
                            ).filter(Q(status='present') | Q(status='late')).count()

                            overall_attendance = (present_count / total_classes * 100) if total_classes > 0 else 0
                            record.overall_attendance = overall_attendance
                            record.save()

                    return redirect('student_attendance_list')

    else:
        selected_course_id = request.GET.get('course')
        selected_subject_id = request.GET.get('subject')

    return render(request, 'attendence/student_attendance_form.html', {
        'courses': courses,
        'subjects': subjects,
        'selected_course_id': int(selected_course_id) if selected_course_id else None,
        'selected_subject_id': int(selected_subject_id) if selected_subject_id else None,
        'student_subject_pairs': student_subject_pairs,
        'selected_subject': selected_subject,
        'today': date.today(),
        'error': error_message
    })


