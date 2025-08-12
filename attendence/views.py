from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import calendar
from .models import attendance, Employee, StudentDatabase, StudentAttendance
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import calendar
from .models import attendance, Employee, StudentDatabase, StudentAttendance

from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
import calendar
from .models import attendance, Employee, StudentDatabase, StudentAttendance
from master.decorators import custom_login_required

@custom_login_required
def attendance_dashboard(request):
    today = timezone.localdate()
    filter_type = request.GET.get('filter', 'today')  # default 'today'

    if filter_type == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif filter_type == 'month':
        start_date = today.replace(day=1)
        end_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    else:
        # today
        start_date = end_date = today

    # Staff attendance queryset
    staff_qs = attendance.objects.all()
    if start_date and end_date:
        staff_qs = staff_qs.filter(date__range=(start_date, end_date))

    staff_present = staff_qs.filter(status='Present').count()
    staff_late = staff_qs.filter(status='Late').count()
    staff_absent = staff_qs.filter(status='Absent').count()
    total_staff = Employee.objects.count()
    staff_attendance_rate = (staff_present + staff_late) / total_staff * 100 if total_staff else 0

    # Student attendance queryset
    stu_qs = StudentAttendance.objects.all()
    if start_date and end_date:
        stu_qs = stu_qs.filter(attendance_date__range=(start_date, end_date))

    present_ids = set(stu_qs.filter(status__iexact='present').values_list('student_id', flat=True))
    absent_ids = set(stu_qs.filter(status__iexact='absent').values_list('student_id', flat=True))
    late_ids = set(stu_qs.filter(status__iexact='late').values_list('student_id', flat=True))
    present_or_late_ids = present_ids.union(late_ids)
    total_students = StudentDatabase.objects.count()
    student_attendance_rate = len(present_or_late_ids) / total_students * 100 if total_students else 0

    total_people = total_staff + total_students
    total_late = staff_late
    total_present_or_late = staff_present + staff_late + len(present_or_late_ids)
    overall_attendance_rate = total_present_or_late / total_people * 100 if total_people else 0

    # Low attendance list
    low_attendance_students = []
    for stu in StudentDatabase.objects.all():
        all_count = StudentAttendance.objects.filter(student=stu).count()
        pres_count = StudentAttendance.objects.filter(student=stu, status__in=['present','late']).count()
        if all_count and (pres_count / all_count * 100) < 75:
            low_attendance_students.append({
                'name': stu.student_name,
                'roll_no': stu.get_admission_no(),
                'percentage': round((pres_count / all_count) * 100, 2),
            })

    context = {
        'filter_type': filter_type,
        'total_staff': total_staff,
        'staff_present': staff_present,
        'staff_late': staff_late,
        'staff_absent': staff_absent,
        'staff_attendance_rate': round(staff_attendance_rate, 1),
        'total_students': total_students,
        'student_present': len(present_ids),
        'student_absent': len(absent_ids),
        'student_late': len(late_ids),
        'student_attendance_rate': round(student_attendance_rate, 1),
        'total_late': total_late,
        'overall_attendance_rate': round(overall_attendance_rate, 1),
        'low_attendance_students': low_attendance_students,
        'active_filter': filter_type,
    }
    return render(request, 'attendence/attendance_dashboard.html', context)
# def attendance_dashboard(request):
#     today = timezone.localdate()
#     filter_type = request.GET.get('filter', 'all')

#     # === Date Range Filtering ===
#     start_date = today
#     end_date = today

#     if filter_type == 'week':
#         start_date = today - timedelta(days=today.weekday())
#         end_date = start_date + timedelta(days=6)
#     elif filter_type == 'month':
#         start_date = today.replace(day=1)
#         end_day = calendar.monthrange(today.year, today.month)[1]
#         end_date = today.replace(day=end_day)
#     elif filter_type == 'all':
#         start_date = None
#         end_date = None

#     # ================== Faculty Attendance ==================
#     total_staff = Employee.objects.count()
#     staff_attendance_today = attendance.objects.all()

#     if start_date and end_date:
#         staff_attendance_today = staff_attendance_today.filter(date__range=(start_date, end_date))
#     elif start_date:
#         staff_attendance_today = staff_attendance_today.filter(date=start_date)

#     staff_present = staff_attendance_today.filter(status='Present').count()
#     staff_late = staff_attendance_today.filter(status='Late').count()
#     staff_present_or_late = staff_present + staff_late

#     staff_attendance_rate = (staff_present_or_late / total_staff * 100) if total_staff else 0

#     # ================== Student Attendance ==================
#     student_attendance_today = StudentAttendance.objects.all()
#     if start_date and end_date:
#         student_attendance_today = student_attendance_today.filter(attendance_date__range=(start_date, end_date))
#     elif start_date:
#         student_attendance_today = student_attendance_today.filter(attendance_date=start_date)

#     total_students = StudentDatabase.objects.count()

#     # Gather valid admission numbers from StudentDatabase safely
#     valid_admission_nos = []

#     for student in StudentDatabase.objects.all():
#         try:
#             admission_no = student.get_admission_no()
#         except Exception:
#             admission_no = "Unlinked"

#         if admission_no != "Unlinked":
#             valid_admission_nos.append(admission_no)

#     # Filter attendance only for valid admission numbers
#     distinct_admission_nos = student_attendance_today.filter(
#         admission_no__in=valid_admission_nos
#     ).values_list('admission_no', flat=True).distinct()

#     student_present = set()
#     student_late = set()

#     for admission_no in distinct_admission_nos:
#         statuses = list(
#             student_attendance_today.filter(admission_no=admission_no).values_list('status', flat=True)
#         )
#         statuses = [s.lower() for s in statuses]

#         if 'present' in statuses:
#             student_present.add(admission_no)
#         if 'late' in statuses:
#             student_late.add(admission_no)

#     student_present_or_late = student_present.union(student_late)
#     student_attendance_rate = (len(student_present_or_late) / total_students * 100) if total_students else 0

#     # ================== Combined Totals ==================
#     total_people = total_staff + total_students
#     total_present = staff_present + len(student_present - student_late)
#     total_late = staff_late + len(student_late)
#     total_present_or_late = staff_present_or_late + len(student_present_or_late)
#     overall_attendance_rate = (total_present_or_late / total_people * 100) if total_people else 0

#     # ========== Low Attendance Alert (All Time) ==========
#     low_attendance_students = []

#     for student in StudentDatabase.objects.all():
#         try:
#             admission_no = student.get_admission_no()
#         except Exception:
#             admission_no = "Unlinked"

#         if admission_no == "Unlinked":
#             continue

#         total_classes = StudentAttendance.objects.filter(admission_no=admission_no).count()
#         present_count = StudentAttendance.objects.filter(
#             admission_no=admission_no,
#             status__in=['present', 'late']
#         ).count()

#         if total_classes > 0:
#             percentage = (present_count / total_classes) * 100
#             if percentage < 75:
#                 low_attendance_students.append({
#                     'name': student.student_name,
#                     'roll_no': admission_no,
#                     'percentage': round(percentage, 2)
#                 })

#     context = {
#         'student_present': len(student_present),
#         'student_late': len(student_late),
#         'student_attendance_rate': round(student_attendance_rate, 1),
#         'total_students': total_students,
#         'total_staff': total_staff,
#         'staff_present': staff_present,
#         'staff_late': staff_late,
#         'staff_attendance_rate': round(staff_attendance_rate, 1),
#         'total_people': total_people,
#         'total_present': total_present,
#         'total_late': total_late,
#         'overall_attendance_rate': round(overall_attendance_rate, 1),
#         'low_attendance_students': low_attendance_students,
#         'active_filter': filter_type
#     }

#     return render(request, 'attendence/attendance_dashboard.html', context)



 
   




from django.http import JsonResponse
from master.models import Employee
from django.shortcuts import render, redirect
from .models import attendance, attendancesettings
from .forms import AttendanceForm, AttendanceSettingsForm
from .utils import calculate_status
from django.http import JsonResponse
from master.models import Employee  # Make sure the import path is correct

@custom_login_required
def employee_detail_api(request, pk):
    try:
        emp = Employee.objects.get(pk=pk)
        return JsonResponse({
            'emp_code': emp.emp_code,
        })
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)



from django.contrib import messages  # Optional: for success or error alerts
from django.shortcuts import get_object_or_404

from django.contrib import messages
from .models import attendance, attendancesettings
from .forms import AttendanceForm

@custom_login_required
def employee_attendance_form_add(request):
    settings = attendancesettings.objects.first()
    if not settings:
        messages.error(request, "Attendance settings not configured.")
        return redirect('employee_attendance_list')

    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            att = form.save(commit=False)
            att.status = calculate_status(att.check_in, settings)
            att.save()
            user = get_logged_in_user(request)
            log_activity(user, 'created', att)
            messages.success(request, "Attendance added successfully.")
            return redirect('employee_attendance_list')
        else:   
            messages.error(request, "Please correct the errors below.")
    else:
        form = AttendanceForm()

    return render(request, 'attendence/attendance_form.html', {
        'form': form,
        'mode': 'add',
    })

@custom_login_required
def employee_attendance_form_edit(request, pk):
    record = get_object_or_404(attendance, pk=pk)
    settings = attendancesettings.objects.first()

    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=record)
        if form.is_valid():
            att = form.save(commit=False)
            if settings:
                att.status = calculate_status(att.check_in, settings)
            att.save()
            user = get_logged_in_user(request)
            log_activity(user, 'updated', att)
            messages.success(request, 'Attendance record updated successfully.')
            return redirect('employee_attendance_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AttendanceForm(instance=record)

    return render(request, 'attendence/attendance_form.html', {
        'form': form,
        'mode': 'edit',
        'attendance': record,
    })




@custom_login_required
def employee_attendance_form_view(request, pk):
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








from django.db.models import Q
from master.models import Employee  # Make sure it's imported
from django.core.paginator import Paginator
@custom_login_required
def employee_attendance_list(request):
    records = attendance.objects.select_related('employee').all().order_by('-date')

    # Filters
    filter_date = request.GET.get('date')
    if filter_date:
        records = records.filter(date=filter_date)

    filter_category = request.GET.get('category')
    if filter_category:
        records = records.filter(employee__category=filter_category)

    filter_employment_type = request.GET.get('employment_type')
    if filter_employment_type:
        records = records.filter(employee__employment_type=filter_employment_type)

    filter_designation = request.GET.get('designation')
    if filter_designation:
        records = records.filter(employee__designation=filter_designation)

    # Dropdown values
    categories = Employee.objects.values_list('category', flat=True).distinct()
    employment_types = Employee.objects.values_list('employment_type', flat=True).distinct()
    designations = Employee.objects.values_list('designation', flat=True).distinct()

    # Pagination
    paginator = Paginator(records, 100)  # 100 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = AttendanceForm()

    return render(request, 'attendence/attendance_list.html', {
        'records': page_obj,
        'page_obj': page_obj,
        'form': form,
        'categories': categories,
        'employment_types': employment_types,
        'designations': designations,
        'filter_date': filter_date,
        'filter_category': filter_category,
        'filter_employment_type': filter_employment_type,
        'filter_designation': filter_designation,
    })


from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from .models import attendance  # Replace with your model

@custom_login_required
def employee_attendance_form_delete(request, pk):
    attendance_obj = get_object_or_404(attendance, pk=pk)
    employee_name = attendance_obj.employee.name
    attendance_obj.delete()
    
    user = get_logged_in_user(request)
    log_activity(user, 'deleted', attendance_obj)

    # Add Django message for snackbar
    messages.success(request, f"Attendance for {employee_name} was successfully deleted.")
    
    return redirect('employee_attendance_list')





from django.contrib import messages

@custom_login_required
def attendance_settings_view(request):
    settings, created = attendancesettings.objects.get_or_create(pk=1)
    if request.method == "POST":
        form = AttendanceSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            updated_settings = form.save()
            check_in_time = form.cleaned_data.get('check_in_time')

            # Format the time (e.g., 09:00 AM)
            formatted_time = check_in_time.strftime('%I:%M %p')

            messages.success(
                request,
                f"Attendacne time updated successfully to {formatted_time}."
            )
            return redirect('attendance_settings_view')
    else:
        form = AttendanceSettingsForm(instance=settings)
    return render(request, 'attendence/attendance_settings.html', {'form': form})


from django.shortcuts import render
from django.db.models import Count, Q
from .models import attendance, StudentAttendance
from datetime import date, timedelta

@custom_login_required
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

            results['Average Staff Attendance'] = f"{round(avg_staff_attendance, 2)} per staff"

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
from master.models import Course, Subject ,StudentDatabase,CourseType
from .models import StudentAttendance
from core.utils import get_logged_in_user,log_activity


@custom_login_required
def student_attendance_list(request):
    attendance_records = StudentAttendance.objects.all().order_by('-attendance_date')

    # GET parameters from the filter form
    selected_program_type_id = request.GET.get('program_type')
    selected_academic_year = request.GET.get('academic_year')
    selected_course_id = request.GET.get('course')
    selected_semester_number = request.GET.get('semester')
    selected_subject_id = request.GET.get('subject')
    attendance_date = request.GET.get('date')
    search_query = request.GET.get('search')

    # Filter Step-by-Step (Hierarchical)
    if selected_program_type_id:
        attendance_records = attendance_records.filter(program_type_id=selected_program_type_id)

    if selected_academic_year:
        attendance_records = attendance_records.filter(academic_year=selected_academic_year)

    if selected_course_id:
        attendance_records = attendance_records.filter(course_id=selected_course_id)

    if selected_semester_number:
        attendance_records = attendance_records.filter(semester_number=selected_semester_number)

    if selected_subject_id:
        try:
            attendance_records = attendance_records.filter(subject_id=int(selected_subject_id))
        except ValueError:
            messages.error(request, f"Invalid subject ID: {selected_subject_id}")

    if attendance_date:
        try:
            attendance_records = attendance_records.filter(attendance_date=attendance_date)
        except ValueError:
            messages.error(request, "Invalid date format")

    if search_query:
        attendance_records = attendance_records.filter(
            Q(student_name__icontains=search_query) |
            Q(admission_number__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(attendance_records, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Dropdown Population
    filtered_courses = Course.objects.none()
    filtered_subjects = Subject.objects.none()
    semester_display = []
    is_pu = False

    # Populate Courses based on selected Program Type
    if selected_program_type_id:
        filtered_courses = Course.objects.filter(course_type_id=selected_program_type_id)

    # Populate Semesters and Subjects if Course is selected
    if selected_course_id:
        try:
            selected_course = Course.objects.get(id=selected_course_id)
            course_type_name = selected_course.course_type.name.strip().lower()
            is_pu = course_type_name == "puc regular"

            total = selected_course.duration_years if is_pu else selected_course.total_semesters or 0
            semester_display = [
                {'id': i, 'label': f"{selected_course.name} {i}"}
                for i in range(1, total + 1)
            ]

            filtered_subjects = Subject.objects.filter(course_id=selected_course_id).order_by('name')

        except Course.DoesNotExist:
            pass

    # Populate academic years (batch)
    academic_years = []
    if selected_program_type_id:
        academic_years = (
            StudentDatabase.objects
            .filter(course__course_type_id=selected_program_type_id)
            .values_list('academic_year', flat=True)
            .distinct()
            .order_by('-academic_year')
        )

    # Final context for template
    context = {
        'page_obj': page_obj,
        'program_types': CourseType.objects.all().order_by('name'),
        'academic_years': academic_years,
        'courses': filtered_courses,
        'semesters': semester_display,
        'subjects': filtered_subjects,

        # Selected values for maintaining filter state
        'selected_program_type_id': selected_program_type_id,
        'selected_academic_year': selected_academic_year,
        'selected_course_id': selected_course_id,
        'selected_semester_id': selected_semester_number,
        'selected_subject_id': selected_subject_id,
        'attendance_date': attendance_date,
        'search_query': search_query,
        'today': date.today(),
    }

    return render(request, 'attendence/student_attendance_list.html', context)
import logging
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from timetable.models import TimeSlot, TimetableEntry
from master.models import CourseType, Course, Subject, StudentDatabase, Employee
from attendence.models import StudentAttendance
from django.db.models import Q
import datetime

logger = logging.getLogger(__name__)

@custom_login_required
def student_attendance_form_add(request):
    logger.info("Accessed student_attendance_form_add view")

    program_types = CourseType.objects.all().order_by('name')
    selected_program_type_id = request.POST.get('program_type') or request.GET.get('program_type')
    academic_years = []

    if selected_program_type_id:
        academic_years = (
            StudentDatabase.objects
            .filter(course__course_type_id=selected_program_type_id)
            .values_list('academic_year', flat=True)
            .distinct()
            .order_by('-academic_year')
        )
        logger.debug(f"Selected program type ID: {selected_program_type_id}")

    selected_academic_year = request.POST.get('academic_year') or request.GET.get('academic_year')
    selected_course_id = request.POST.get('course') or request.GET.get('course')
    selected_semester_id = request.POST.get('semester') or request.GET.get('semester')
    selected_subject_id = request.POST.get('subject') or request.GET.get('subject')
    selected_timeslot_id = request.POST.get("timeslot") or request.GET.get("timeslot")
    attendance_date = request.POST.get("attendance_date")
    form_action = request.POST.get("form_action")

    courses, subjects, students = [], [], []
    student_subject_pairs = []
    semesters = []
    selected_course = None
    selected_subject = None
    selected_timeslot = None
    error_message = None
    time_slots = []
    faculty = None
    today = timezone.now().date()
    selected_day_name = None
    is_pu = False
    attendance_date_obj = None

    if selected_program_type_id:
        courses = Course.objects.filter(course_type_id=selected_program_type_id).order_by('name')

    if selected_course_id:
        selected_course = get_object_or_404(Course, id=selected_course_id)
        logger.debug(f"Selected course: {selected_course.name} (ID: {selected_course_id})")

        course_type_name = selected_course.course_type.name.strip().lower()
        is_pu = course_type_name == "puc regular"
        total = selected_course.duration_years if is_pu else selected_course.total_semesters or 0
        semesters = [{'id': i, 'name': f"{selected_course.name} {i}"} for i in range(1, total + 1)]

        if not semesters:
            semesters.append({'id': 0, 'name': "NOT APPLICABLE"})
            logger.warning("No semesters found, defaulting to NOT APPLICABLE.")

    if selected_course_id and selected_semester_id:
        if attendance_date:
            try:
                attendance_date_obj = datetime.datetime.strptime(attendance_date, '%Y-%m-%d').date()
                logger.debug(f"Parsed attendance date: {attendance_date_obj}")

                if attendance_date_obj <= today:
                    selected_day_name = attendance_date_obj.strftime('%A')
                    logger.debug(f"Selected day for timetable: {selected_day_name}")

                    timetable_entries = TimetableEntry.objects.filter(
                        course_id=selected_course_id,
                        semester_number=selected_semester_id,
                        day=selected_day_name
                    )
                    subject_ids = timetable_entries.values_list('subject_id', flat=True).distinct()
                    subjects = Subject.objects.filter(id__in=subject_ids).order_by('name')
                else:
                    logger.warning("Attempted to fetch subjects for a future date.")
                    subjects = []
            except ValueError:
                logger.error("Invalid attendance date format provided.")
                subjects = []
        else:
            subjects = Subject.objects.filter(course_id=selected_course_id, semester=selected_semester_id).order_by('name')

    if selected_course_id and selected_semester_id and selected_subject_id:
        selected_subject = get_object_or_404(Subject, id=selected_subject_id)
        logger.debug(f"Selected subject: {selected_subject.name} (ID: {selected_subject_id})")

        if attendance_date:
            try:
                attendance_date_obj = datetime.datetime.strptime(attendance_date, '%Y-%m-%d').date()
                if attendance_date_obj > today:
                    error_message = "You cannot mark attendance for a future date."
                    logger.warning("Attendance attempted for future date.")
                else:
                    selected_day_name = attendance_date_obj.strftime('%A')
                    timetable_entries = TimetableEntry.objects.filter(
                        course_id=selected_course_id,
                        semester_number=selected_semester_id,
                        subject_id=selected_subject_id,
                        day=selected_day_name
                    )
                    time_slots = list({entry.time_slot for entry in timetable_entries})

                    if selected_timeslot_id:
                        selected_timeslot = get_object_or_404(TimeSlot, id=selected_timeslot_id)
                        logger.debug(f"Selected timeslot ID: {selected_timeslot_id}")

                        faculty_entry = timetable_entries.filter(time_slot_id=selected_timeslot_id).first()
                        faculty = faculty_entry.faculty if faculty_entry else None
                        logger.debug(f"Identified faculty: {faculty}")

                    students = StudentDatabase.objects.filter(
                        course_id=selected_course.id,
                        current_year=selected_semester_id if is_pu else None,
                        semester=selected_semester_id if not is_pu else None
                    )

                    for student in students:
                        total_classes = StudentAttendance.objects.filter(
                            student=student,
                            subject=selected_subject
                        ).count()
                        present_count = StudentAttendance.objects.filter(
                            student=student,
                            subject=selected_subject,
                            status__in=['present', 'late']
                        ).count()
                        percentage = (present_count / total_classes * 100) if total_classes > 0 else 0

                        student_subject_pairs.append({
                            'student': student,
                            'subject': selected_subject,
                            'attendance_percentage': round(percentage, 2),
                            'current_year': student.current_year,
                            'semester': student.semester,
                        })

                    if form_action == "submit_attendance" and selected_timeslot:
                        logger.info("Submitting attendance records...")

                        student_ids = request.POST.getlist('student_ids[]')
                        updated_count = 0

                        for sid in student_ids:
                            try:
                                student = StudentDatabase.objects.get(id=sid)
                            except StudentDatabase.DoesNotExist:
                                logger.warning(f"Student with ID {sid} not found, skipping.")
                                continue

                            status = request.POST.get(f"status_{sid}")
                            remarks = request.POST.get(f"remarks_{sid}")
                            if not status:
                                logger.debug(f"No status for student ID {sid}, skipping.")
                                continue

                            attendance, created = StudentAttendance.objects.update_or_create(
                                student=student,
                                subject=selected_subject,
                                attendance_date=attendance_date_obj,
                                time_slot=selected_timeslot,
                                defaults={
                                    'status': status,
                                    'remarks': remarks,
                                    'faculty': faculty,
                                    'course': selected_course,
                                    'semester_number': selected_semester_id,
                                    'student_name': student.student_name,
                                    'student_userid': student.student_userid,
                                    'time_slot': selected_timeslot,
                                    'academic_year': student.academic_year,
                                    'program_type': selected_course.course_type,
                                }
                            )

                            total = StudentAttendance.objects.filter(student=student, subject=selected_subject).count()
                            present = StudentAttendance.objects.filter(student=student, subject=selected_subject, status__in=['present', 'late']).count()
                            attendance.attendance_percentage = round((present / total * 100), 2) if total else 0
                            attendance.save()

                            logger.info(f"{'Created' if created else 'Updated'} attendance for {student.student_name} (ID: {student.id}).")
                            updated_count += 1

                        if updated_count:
                            messages.success(request, f"Attendance submitted for {updated_count} student(s) on {attendance_date_obj.strftime('%d-%b-%Y')}.")

                        return redirect('student_attendance_list')

            except ValueError:
                error_message = "Invalid date format."
                logger.error("Date parsing error during attendance processing.")

    context = {
        'form_mode': 'add',  # ✅ Include this!
        'program_types': program_types,
        'academic_years': academic_years,
        'selected_program_type_id': selected_program_type_id,
        'selected_academic_year': selected_academic_year,
        'courses': courses,
        'semesters': semesters,
        'subjects': subjects,
        'student_subject_pairs': student_subject_pairs,
        'selected_course_id': int(selected_course_id) if selected_course_id else None,
        'selected_semester_id': int(selected_semester_id) if selected_semester_id else None,
        'selected_subject_id': int(selected_subject_id) if selected_subject_id else None,
        'selected_subject': selected_subject,
        'selected_timeslot_id': int(selected_timeslot_id) if selected_timeslot_id else None,
        'selected_timeslot': selected_timeslot,
        'time_slots': time_slots,
        'time_slot': selected_timeslot,
        'faculty': faculty,
        'today': today,
        'error_message': error_message,
        'attendance_date': attendance_date_obj or today,
    }

    return render(request, 'attendence/student_attendance_form.html', context)




#Edit student_attendance
from django.contrib import messages

@custom_login_required
def student_attendance_form_edit(request, record_id):
    record = get_object_or_404(StudentAttendance, id=record_id)
    student = record.student
    subject = record.subject
    course = record.course

    if not all([student, subject, course]):
        messages.error(request, "Some data is missing or not linked.")
        return redirect('student_attendance_list')

    if request.method == 'POST':
        status = request.POST.get(f"status_{student.id}")
        remarks = request.POST.get(f"remarks_{student.id}")

        if status:
            record.status = status
            record.remarks = remarks
            record.save()

            total_classes = StudentAttendance.objects.filter(
                student=student,
                subject=subject
            ).count()

            present_count = StudentAttendance.objects.filter(
                student=student,
                subject=subject,
                status__in=['present', 'late']
            ).count()

            record.attendance_percentage = round((present_count / total_classes * 100), 2) if total_classes > 0 else 0
            record.save()

            messages.success(request, f"Attendance record for {student.student_name} updated successfully.")
            return redirect('student_attendance_list')

    # Extra context for dropdowns
    program_types = CourseType.objects.all().order_by('name')
    selected_program_type_id = course.course_type.id

    academic_years = (
        StudentDatabase.objects
        .filter(course=course)
        .values_list('academic_year', flat=True)
        .distinct()
        .order_by('-academic_year')
    )


    is_pu = course.course_type.name.strip().lower() == "puc regular"
    total = course.duration_years if is_pu else course.total_semesters or 0
    semesters = [{'id': i, 'name': f"{course.name} {i}"} for i in range(1, total + 1)]

    student_subject_pairs = [{
        'student': student,
        'subject': subject,
        'student_userid': student.student_userid,
        'attendance_percentage': record.attendance_percentage or 0,
        'existing_status': record.status,
        'existing_remarks': record.remarks,

    }]

    return render(request, 'attendence/student_attendance_form.html', {
        'program_types': program_types,
        'academic_years': academic_years,
        'selected_program_type_id': selected_program_type_id,
        'selected_academic_year': student.academic_year,
        'courses': Course.objects.all(),
        'subjects': Subject.objects.filter(course=course),
        'semesters': semesters,
        'time_slots': [record.time_slot] if record.time_slot else [],
        'selected_course_id': course.id,
        'selected_subject_id': subject.id,
        'selected_semester_id': record.semester_number,
        'selected_timeslot_id': record.time_slot.id if record.time_slot else None,
        'student_subject_pairs': student_subject_pairs,
        'selected_subject': subject,
        'today': record.attendance_date,
        'faculty': record.faculty,
        'form_mode': 'edit',
    })



#view student_attendance
@custom_login_required
def student_attendance_form_view(request, record_id):
    record = get_object_or_404(StudentAttendance, id=record_id)
    student = record.student
    subject = record.subject
    course = record.course

    program_types = CourseType.objects.all().order_by('name')
    selected_program_type_id = course.course_type.id

    academic_years = (
        StudentDatabase.objects
        .filter(course=course)
        .values_list('academic_year', flat=True)
        .distinct()
        .order_by('-academic_year')
    )


    is_pu = course.course_type.name.strip().lower() == "puc regular"
    total = course.duration_years if is_pu else course.total_semesters or 0
    semesters = [{'id': i, 'name': f"{course.name} {i}"} for i in range(1, total + 1)]

    student_subject_pairs = [{
        'student': student,
        'subject': subject,
        'student_userid': student.student_userid,
        'attendance_percentage': record.attendance_percentage or 0,
        'existing_status': record.status,
        'existing_remarks': record.remarks,
    }]

    return render(request, 'attendence/student_attendance_form.html', {
        'program_types': program_types,
        'academic_years': academic_years,
        'selected_program_type_id': selected_program_type_id,
        'selected_academic_year': student.academic_year,
        'courses': Course.objects.all(),
        'subjects': Subject.objects.filter(course=course),
        'semesters': semesters,
        'time_slots': [record.time_slot] if record.time_slot else [],
        'selected_course_id': course.id,
        'selected_subject_id': subject.id,
        'selected_semester_id': record.semester_number,
        'selected_timeslot_id': record.time_slot.id if record.time_slot else None,
        'student_subject_pairs': student_subject_pairs,
        'selected_subject': subject,
        'today': record.attendance_date,
        'faculty': record.faculty,
        'form_mode': 'view',
    })



#delete student_attendance
@custom_login_required
def student_attendance_form_delete(request, record_id):
    record = get_object_or_404(StudentAttendance, id=record_id)
    student_name = record.student_name  # Capture before deleting
    record.delete()
    
    user = get_logged_in_user(request)
    log_activity(user, 'deleted', record)
    
    messages.success(request, f"Attendance record for student '{student_name}' deleted successfully.")
    return redirect('student_attendance_list')




