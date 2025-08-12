from django.shortcuts import render, redirect
from admission.models import ConfirmedAdmission

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from admission.models import ConfirmedAdmission
from django.http import HttpResponseRedirect
from django.urls import reverse

def student_login_view(request):
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        context['selected_user'] = username

        try:
            student = ConfirmedAdmission.objects.get(student_userid=username)

            if student.is_locked:
                context['error'] = "Account is locked due to multiple failed attempts. Contact admin."
                return render(request, 'lms/student_login.html', context)

            if student.student_password != password:
                student.wrong_attempts += 1
                if student.wrong_attempts >= 3:
                    student.is_locked = True
                student.save()
                context['error'] = "Invalid password."
                return render(request, 'lms/student_login.html', context)

            # Reset wrong attempts on success
            student.wrong_attempts = 0
            student.save()

            # Determine redirect URL first
            if not student.password_changed:
                redirect_url = reverse('student_set_password')
            elif not student.passcode_set:
                redirect_url = reverse('student_set_passcode')
            else:
                redirect_url = reverse('student_dashboard')

            # Create response and set cookies
            response = HttpResponseRedirect(redirect_url)
            response.set_cookie('student_id', student.id)
            response.set_cookie('student_userid', student.student_userid)
            response.set_cookie('student_name', student.student_name)

            print(">>> Login successful")
            print("Cookies set:")
            print("student_id:", student.id)
            print("student_userid:", student.student_userid)
            print("student_name:", student.student_name)

            return response

        except ConfirmedAdmission.DoesNotExist:
            context['error'] = "Invalid credentials."

    return render(request, 'lms/student_login.html', context)


def student_logout(request):
    request.session.flush()
    response = redirect('student_login_view')
    response.delete_cookie('student_id')
    response.delete_cookie('student_userid')
    response.delete_cookie('student_name')
    return response


def student_set_password(request):
    student_userid = request.COOKIES.get('student_userid')
    if not student_userid:
        return redirect('student_login_view')

    student = ConfirmedAdmission.objects.get(student_userid=student_userid)
    error = None

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            error = "Passwords do not match."
        elif len(new_password) < 8:
            error = "Password must be at least 8 characters."
        else:
            student.student_password = new_password
            student.password_changed = True
            student.save()
            return redirect('student_set_passcode')

    return render(request, 'lms/student_set_password.html', {
        'error': error,
        'selected_user': student.student_userid  # or student.username or however you call it
    })



def student_set_passcode(request):
    student_userid = request.COOKIES.get('student_userid')
    if not student_userid:
        return redirect('student_login_view')

    student = ConfirmedAdmission.objects.get(student_userid=student_userid)
    error = None

    if request.method == 'POST':
        passcode = request.POST.get('passcode')

        if not passcode.isdigit() or len(passcode) < 4:
            error = "Passcode must be at least 4 digits."
        else:
            student.passcode = passcode
            student.passcode_set = True
            student.save()
            return redirect('student_dashboard')

    return render(request, 'lms/student_set_passcode.html', {'error': error})

from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect
from django.db.models import Count, Q
from .models import Assignment, Exam
from master.models import StudentDatabase

def student_dashboard(request):
    student_userid = request.COOKIES.get('student_userid')
    if not student_userid:
        return redirect('student_login_view')

    try:
        student = StudentDatabase.objects.get(student_userid=student_userid)
    except StudentDatabase.DoesNotExist:
        return redirect('student_login_view')

    today = timezone.now().date()

    # All assignments due in next 3 days
    assignments_due = Assignment.objects.filter(
        academic_year=student.academic_year,
        program_type=student.course_type,
        course=student.course,
        semester_number=student.semester,
        due_date__range=(today, today + timedelta(days=3))
    )
    print("Assignments due in 3 days:", assignments_due.count())
    print("Assignment IDs due:", list(assignments_due.values_list('id', flat=True)))

    # Count submissions by this student with status='submitted' per assignment
    assignments_due = assignments_due.annotate(
        submitted_count=Count(
            'submissions',
            filter=Q(submissions__student_userid=student_userid, submissions__status='submitted')
        )
    )

    # Filter assignments where submitted_count == 0 (i.e. not submitted yet)
    assignment_notifications = assignments_due.filter(submitted_count=0)
    print("Assignments after excluding submitted:", assignment_notifications.count())

    # Debug: List assignments in notification
    for a in assignment_notifications:
        print(f"Pending assignment ID: {a.id}, due date: {a.due_date}")

    exam_notifications = Exam.objects.filter(
        course=student.course,
        exam_date__range=(today, today + timedelta(days=30))
    )

    notifications = []

    for assignment in assignment_notifications:
        notifications.append({
            'type': 'assignment',
            'title': f"Assignment due on {assignment.due_date.strftime('%d %b')}",
            'url': '/student/assignments/',
        })

    for exam in exam_notifications:
        days_until_exam = (exam.exam_date - today).days
        if days_until_exam in [7, 30]:
            label = f"{exam.subject.name} exam on {exam.exam_date.strftime('%d %b')} (in {days_until_exam} days)"
        else:
            label = f"{exam.subject.name} exam on {exam.exam_date.strftime('%d %b')}"
        notifications.append({
            'type': 'exam',
            'title': label,
            'url': '/exam/',
        })

    context = {
        'student': student,
        'pending_assignments': 0,
        'due_this_week': assignment_notifications.count(),
        'current_gpa': 0.0,
        'attendance_rate': 0,
        'notifications': notifications,
        'notification_count': len(notifications),
    }

    return render(request, 'lms/student_dashboard.html', context)






def student_password_reset_view(request):
    context = {}
    username = request.GET.get('username') or request.POST.get('username')
    context['selected_user'] = username
    context['reset'] = True  # Tell the template we're in reset mode

    if request.method == 'POST':
        try:
            student = ConfirmedAdmission.objects.get(student_userid=username)
        except ConfirmedAdmission.DoesNotExist:
            context['error'] = "User does not exist."
            return render(request, 'lms/student_login.html', context)

        # Step 1: Verify passcode
        if 'verify_passcode' in request.POST:
            input_passcode = request.POST.get('passcode', '').strip()
            if not student.passcode_set or student.passcode != input_passcode:
                context['error'] = "Incorrect passcode."
            else:
                context['passcode_verified'] = True  # Show new password fields

        # Step 2: Reset password after passcode verified
        elif 'password_reset_submit' in request.POST:
            new_password = request.POST.get('new_password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()

            import re
            pattern = r'^[A-Z][a-z]*[!@#$%^&*(),.?":{}|<>][a-zA-Z0-9]*[0-9]+$'

            if new_password != confirm_password:
                context['error'] = "Passwords do not match."
                context['passcode_verified'] = True  # keep showing reset form
            elif not re.match(pattern, new_password) or not (8 <= len(new_password) <= 16):
                context['error'] = "Invalid password format."
                context['passcode_verified'] = True
            else:
                student.student_password = new_password
                student.password_changed = True
                student.save()
                context['success_message'] = "Password reset successfully."
                return redirect('student_login_view')

    return render(request, 'lms/student_login.html', context)

from django.shortcuts import render
from django.utils.timezone import localtime
from master.models import StudentDatabase
from attendence.models import StudentAttendance

from django.utils.timezone import localtime

from django.shortcuts import render, redirect
from django.utils.timezone import localtime
from master.models import StudentDatabase
from attendence.models import StudentAttendance
from django.utils.timezone import localtime
from django.shortcuts import render, redirect
from datetime import date
from timetable.models import TimetableEntry
from master.models import AcademicYear  # Assuming this exists
from django.utils.timezone import localtime
from django.shortcuts import render, redirect
from datetime import date

def my_attendance_view(request):
    student_userid = request.COOKIES.get('student_userid')
   

    if not student_userid:
        
        return redirect('student_login_view')

    try:
        confirmed_student = ConfirmedAdmission.objects.get(student_userid=student_userid)
        student = StudentDatabase.objects.get(student_userid=student_userid)
        
    except (ConfirmedAdmission.DoesNotExist, StudentDatabase.DoesNotExist):
        
        return redirect('student_login_view')

    today_date = localtime().date()
    today_day = today_date.strftime('%A')  # e.g. 'Thursday'
   

    # Student course details
    course = student.course
    course_type = student.course_type
    

    # Convert academic_year string to FK object
    try:
        academic_year_obj = AcademicYear.objects.get(year=student.academic_year)
        
    except AcademicYear.DoesNotExist:
       
        academic_year_obj = None

    # Choose semester or year
    if course_type and course_type.name.lower() == 'puc':
        semester_or_year = student.current_year
        
    else:
        semester_or_year = student.semester
       

    # Fetch today's scheduled classes from timetable
    today_schedule = TimetableEntry.objects.filter(
        day=today_day,
        course=course,
        course_type=course_type,
        semester_number=semester_or_year,
        academic_year=academic_year_obj
    )



    total_records = today_schedule.count()

    # Attendance records for today
    today_attendance = StudentAttendance.objects.filter(
        student=student,
        attendance_date=today_date
    ).select_related('subject', 'faculty', 'course')

   

    present_today = today_attendance.filter(status='present').count()
    late_today = today_attendance.filter(status='late').count()
    absent_today = today_attendance.filter(status='absent').count()
    attended_today = present_today + late_today

   

    attendance_rate = round((attended_today / total_records) * 100, 2) if total_records > 0 else 0
  

    context = {
        'total_records': total_records,
        'present_today': present_today,
        'late_today': late_today,
        'absent_today': absent_today,
        'attendance_rate': attendance_rate,
        'today_records': today_attendance,
    }
    return render(request, 'lms/my_attendance.html', context)



from django.shortcuts import render, redirect
from datetime import date
from fees.models import StudentFeeCollection
from django.db import models
# Import your models here
from django.utils.timezone import localtime

from django.shortcuts import render, redirect
from datetime import date

from django.db.models import Sum, Case, When, Value, CharField

from django.db.models import Max, Subquery, OuterRef

from django.shortcuts import render, redirect
from datetime import date
from django.db import models
from django.db.models import OuterRef, Subquery, Max
from fees.models import StudentFeeCollection


from collections import defaultdict
from decimal import Decimal





def my_fees_view(request):
    student_userid = request.COOKIES.get('student_userid')

    if not student_userid:
        return redirect('student_login_view')

    try:
        confirmed_student = ConfirmedAdmission.objects.get(student_userid=student_userid)
        student = StudentDatabase.objects.get(student_userid=student_userid)
    except (ConfirmedAdmission.DoesNotExist, StudentDatabase.DoesNotExist):
        return redirect('student_login_view')

    # Fetch all fee records for the student
    all_fees = StudentFeeCollection.objects.filter(student_userid=student_userid)

    grouped_fees = defaultdict(list)
    for fee in all_fees:
        key = (fee.fee_type_id, fee.due_date)
        grouped_fees[key].append(fee)

    fee_display_list = []
    total_fees = Decimal('0')
    total_collected = Decimal('0')
    total_pending = Decimal('0')
    total_overdue = Decimal('0')
    overdue_fee_types = set()
    today = date.today()

    for (fee_type_id, due_date), records in grouped_fees.items():
        latest_record = max(records, key=lambda x: x.id)
        amount = latest_record.amount  # assumed same for all grouped records
        total_paid = sum(r.paid_amount for r in records)
        total_discount = sum(getattr(r, 'applied_discount', Decimal('0')) for r in records)
        balance = amount - total_paid - total_discount

        if balance <= 0:
            status = 'Paid'
            balance = Decimal('0')
        elif total_paid > 0:
            status = 'Partial'
        else:
            status = 'Pending'

        if balance > 0 and due_date < today:
            total_overdue += balance
            overdue_fee_types.add(latest_record.fee_type.name)  # Collect overdue fee type names

        total_fees += amount
        total_collected += total_paid
        total_pending += balance

        fee_display_list.append({
            'id': latest_record.id,
            'fee_type': latest_record.fee_type,
            'due_date': latest_record.due_date,
            'amount': amount,
            'paid_amount': total_paid,
            'balance_amount': balance,
            'status': status,
            'applied_discount': total_discount,
            'total_paid': total_paid + total_discount,
        })

    fee_display_list.sort(key=lambda x: x['due_date'])

    context = {
        'fee_collections': fee_display_list,
        'total_fees': total_fees,
        'collected': total_collected,
        'pending': total_pending,
        'overdue': total_overdue,
        'overdue_fee_types': sorted(overdue_fee_types),  # pass sorted list to template
    }

    return render(request, 'lms/my_fee.html', context)




from django.shortcuts import render, redirect

def student_profile_view(request):
    student_userid = request.COOKIES.get('student_userid')

    if not student_userid:
        return redirect('student_login_view')

    try:
        # Get ConfirmedAdmission record
        confirmed_student = ConfirmedAdmission.objects.get(student_userid=student_userid)
        student_entry = StudentDatabase.objects.get(student_userid=student_userid)
      
    except (ConfirmedAdmission.DoesNotExist, StudentDatabase.DoesNotExist):
        return redirect('student_login_view')

    # Determine linked admission (PU or Degree)
    if student_entry.pu_admission:
        admission = student_entry.pu_admission
    elif student_entry.degree_admission:
        admission = student_entry.degree_admission
    else:
        # No linked admission found, redirect or handle as needed
        return redirect('student_login_view')

    context = {
        'confirmed_student': confirmed_student,
        'admission': admission,
        'student': student_entry,  # For template consistency
    }

    return render(request, 'lms/my_profile.html', context)



from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Avg
from .models import Assignment, AssignmentSubmission
from master.models import StudentDatabase

def my_assignments_view(request):
    student_userid = request.COOKIES.get('student_userid')
    if not student_userid:
        return redirect('student_login_view')

    try:
        student = StudentDatabase.objects.get(student_userid=student_userid)
    except StudentDatabase.DoesNotExist:
        return redirect('student_login_view')

    academic_year = student.academic_year
    course_type = student.course_type
    course = student.course
    semester = student.semester or student.current_year

    assignments = Assignment.objects.filter(
        academic_year=academic_year,
        program_type=course_type,
        course=course,
        semester_number=semester
    ).order_by('-due_date')

    submissions = AssignmentSubmission.objects.filter(
        student_userid=student_userid,
        assignment__in=assignments
    )

    submissions_dict = {sub.assignment_id: sub for sub in submissions}
    submitted_assignment_ids = submissions_dict.keys()

    pending = sum(1 for a in assignments if a.id not in submitted_assignment_ids)
    submitted = sum(1 for a in assignments if submissions_dict.get(a.id) and submissions_dict[a.id].status == 'submitted')
    graded = sum(1 for a in assignments if submissions_dict.get(a.id) and submissions_dict[a.id].status == 'graded')
    avg_score = submissions.filter(status='graded').aggregate(Avg('score'))['score__avg'] or 0

    context = {
        'assignments': assignments,
        'submitted_assignment_ids': submitted_assignment_ids,
        'submissions_dict': submissions_dict,
        'pending': pending,
        'submitted': submitted,
        'graded': graded,
        'avg_score': round(avg_score, 2),
        'today': timezone.now().date(),
    }

    return render(request, 'lms/my_assignments.html', context)



# View to handle assignment submission (upload + update)
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseForbidden
from .forms import AssignmentSubmissionForm  # We'll create this form next

@require_http_methods(["GET", "POST"])
def submit_assignment_view(request, assignment_id):
    student_userid = request.COOKIES.get('student_userid')
    if not student_userid:
        return redirect('student_login_view')

    assignment = get_object_or_404(Assignment, id=assignment_id)
    try:
        student = StudentDatabase.objects.get(student_userid=student_userid)
    except StudentDatabase.DoesNotExist:
        return redirect('student_login_view')

    # Prevent submission after due date
    if assignment.due_date < timezone.now().date():
        return HttpResponseForbidden("Submission closed for this assignment.")

    # Check if submission exists already for update
    submission, created = AssignmentSubmission.objects.get_or_create(
        student_userid=student_userid,
        assignment=assignment,
        defaults={'status': 'submitted'}
    )

    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.status = 'submitted'  # Mark as submitted on form submit
            submission.submitted_at = timezone.now()
            submission.save()
            return redirect('my_assignments_view')
    else:
        form = AssignmentSubmissionForm(instance=submission)

    return render(request, 'lms/submit_assignment.html', {
        'form': form,
        'assignment': assignment,
    })





#

from django.shortcuts import render, redirect
from .forms import AssignmentForm
from .models import Assignment
from master.models import Course, Subject, CourseType, StudentDatabase
from master.models import Employee, EmployeeSubjectAssignment



def assignment_list(request):
    assignments = Assignment.objects.all().order_by('-due_date')

    # Filter params
    program_type = request.GET.get('program_type')
    academic_year = request.GET.get('academic_year')
    course = request.GET.get('course')
    semester = request.GET.get('semester')
    subject = request.GET.get('subject')

    if program_type:
        assignments = assignments.filter(program_type_id=program_type)
    if academic_year:
        assignments = assignments.filter(academic_year=academic_year)
    if course:
        assignments = assignments.filter(course_id=course)
    if semester:
        assignments = assignments.filter(semester_number=semester)
    if subject:
        assignments = assignments.filter(subject_id=subject)

    context = {
        'assignments': assignments,
        'program_types': CourseType.objects.all(),
        'courses': Course.objects.all(),
        'subjects': Subject.objects.all(),
        'years': Assignment.objects.values_list('academic_year', flat=True).distinct(),
        'selected': {
            'program_type': program_type,
            'academic_year': academic_year,
            'course': course,
            'semester': semester,
            'subject': subject
        }
    }
    return render(request, 'lms/employee_assignments_list.html', context)

#create 


def create_assignment(request):
    selected_program_type_id = request.GET.get('program_type')
    selected_academic_year = request.GET.get('academic_year')
    selected_course_id = request.GET.get('course')
    selected_semester_id = request.GET.get('semester')
    selected_subject_id = request.GET.get('subject')

    filtered_courses = Course.objects.none()
    filtered_subjects = Subject.objects.none()
    semester_display = []
    faculty_members = []  # ? Will hold valid faculty queryset

    if selected_program_type_id:
        filtered_courses = Course.objects.filter(course_type_id=selected_program_type_id)

    if selected_course_id:
        try:
            selected_course = Course.objects.get(id=selected_course_id)
            is_pu = selected_course.course_type.name.strip().lower() == "puc regular"
            total = selected_course.duration_years if is_pu else selected_course.total_semesters or 0
            semester_display = [{'id': i, 'label': f"{selected_course.name} {i}"} for i in range(1, total + 1)]
            filtered_subjects = Subject.objects.filter(course_id=selected_course_id).order_by('name')
        except Course.DoesNotExist:
            pass

    academic_years = []
    if selected_program_type_id:
        academic_years = (
            StudentDatabase.objects
            .filter(course__course_type_id=selected_program_type_id)
            .values_list('academic_year', flat=True)
            .distinct()
            .order_by('-academic_year')
        )

    # ? Get faculty assigned to the selected course/semester/subject
    if selected_course_id and selected_semester_id and selected_subject_id:
        faculty_assignments = EmployeeSubjectAssignment.objects.filter(
            course_id=selected_course_id,
            semester=selected_semester_id,
            subject_id=selected_subject_id
        ).select_related('employee')

        faculty_members = Employee.objects.filter(id__in=faculty_members)  # convert list to queryset

    # ? Form processing with faculty queryset
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, faculty_queryset=faculty_members)

        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.program_type_id = selected_program_type_id
            assignment.academic_year = selected_academic_year
            assignment.course_id = selected_course_id
            assignment.semester_number = selected_semester_id
            assignment.subject_id = selected_subject_id
            assignment.save()
            return redirect('assignment_list')
        else:
            print("? Form is invalid")
            print(form.errors)
    else:
        form = AssignmentForm(faculty_queryset=faculty_members)

    context = {
        'form': form,
        'program_types': CourseType.objects.all().order_by('name'),
        'academic_years': academic_years,
        'courses': filtered_courses,
        'semesters': semester_display,
        'subjects': filtered_subjects,
        'faculty_members': faculty_members,  # Used only if rendering manually
        'selected': {
            'program_type': selected_program_type_id,
            'academic_year': selected_academic_year,
            'course': selected_course_id,
            'semester': selected_semester_id,
            'subject': selected_subject_id,
        }
    }

    return render(request, 'lms/employee_assignments_form.html', context)


from django.shortcuts import get_object_or_404

def edit_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    # Recalculate dropdowns based on assignment
    selected_program_type_id = assignment.program_type_id
    selected_academic_year = assignment.academic_year
    selected_course_id = assignment.course_id
    selected_semester_id = assignment.semester_number
    selected_subject_id = assignment.subject_id

    filtered_courses = Course.objects.filter(course_type_id=selected_program_type_id)
    filtered_subjects = Subject.objects.filter(course_id=selected_course_id).order_by('name')

    selected_course = Course.objects.get(id=selected_course_id)
    is_pu = selected_course.course_type.name.strip().lower() == "puc regular"
    total = selected_course.duration_years if is_pu else selected_course.total_semesters or 0
    semester_display = [{'id': i, 'label': f"{selected_course.name} {i}"} for i in range(1, total + 1)]

    academic_years = (
        StudentDatabase.objects
        .filter(course__course_type_id=selected_program_type_id)
        .values_list('academic_year', flat=True)
        .distinct()
        .order_by('-academic_year')
    )

    faculty_assignments = EmployeeSubjectAssignment.objects.filter(
        course_id=selected_course_id,
        semester=selected_semester_id,
        subject_id=selected_subject_id
    ).select_related('employee')

    faculty_members = [assignment.employee for assignment in faculty_assignments]

    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment, faculty_queryset=faculty_members)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated successfully.")
            return redirect('assignment_list')
        else:
            print("Form errors:", form.errors)
    else:
        form = AssignmentForm(instance=assignment, faculty_queryset=faculty_members)

    context = {
        'form': form,
        'program_types': CourseType.objects.all().order_by('name'),
        'academic_years': academic_years,
        'courses': filtered_courses,
        'semesters': semester_display,
        'subjects': filtered_subjects,
        'faculty_members': faculty_members,
        'selected': {
            'program_type': selected_program_type_id,
            'academic_year': selected_academic_year,
            'course': selected_course_id,
            'semester': selected_semester_id,
            'subject': selected_subject_id,
        },
        'edit_mode': True
    }

    return render(request, 'lms/employee_assignments_form.html', context)

from django.shortcuts import render, get_object_or_404
from .models import Assignment
from .forms import AssignmentForm

def view_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    selected_program_type_id = assignment.program_type_id
    selected_academic_year = assignment.academic_year
    selected_course_id = assignment.course_id
    selected_semester_id = assignment.semester_number
    selected_subject_id = assignment.subject_id

    filtered_courses = Course.objects.filter(course_type_id=selected_program_type_id)
    filtered_subjects = Subject.objects.filter(course_id=selected_course_id).order_by('name')

    selected_course = Course.objects.get(id=selected_course_id)
    is_pu = selected_course.course_type.name.strip().lower() == "puc regular"
    total = selected_course.duration_years if is_pu else selected_course.total_semesters or 0
    semester_display = [{'id': i, 'label': f"{selected_course.name} {i}"} for i in range(1, total + 1)]

    academic_years = (
        StudentDatabase.objects
        .filter(course__course_type_id=selected_program_type_id)
        .values_list('academic_year', flat=True)
        .distinct()
        .order_by('-academic_year')
    )

    faculty_assignments = EmployeeSubjectAssignment.objects.filter(
        course_id=selected_course_id,
        semester=selected_semester_id,
        subject_id=selected_subject_id
    ).select_related('employee')

    faculty_members = [a.employee for a in faculty_assignments]

    # Initialize form in read-only mode
    form = AssignmentForm(instance=assignment, faculty_queryset=faculty_members)
    for field in form.fields.values():
        field.disabled = True  # Disable all form fields

    context = {
        'form': form,
        'program_types': CourseType.objects.all().order_by('name'),
        'academic_years': academic_years,
        'courses': filtered_courses,
        'semesters': semester_display,
        'subjects': filtered_subjects,
        'faculty_members': faculty_members,
        'selected': {
            'program_type': selected_program_type_id,
            'academic_year': selected_academic_year,
            'course': selected_course_id,
            'semester': selected_semester_id,
            'subject': selected_subject_id,
        },
        'view_mode': True,  # Flag to show in template
    }

    return render(request, 'lms/employee_assignments_form.html', context)


import os
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404

def delete_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    # Store file path before deleting
    file_path = assignment.attachment.path if assignment.attachment else None
    folder_path = os.path.dirname(file_path) if file_path else None

    # Delete the Assignment object (this will not delete the file automatically)
    assignment.delete()

    # Delete the file if it exists
    if file_path and os.path.isfile(file_path):
        os.remove(file_path)

    # Delete folder if empty
    if folder_path and os.path.isdir(folder_path) and not os.listdir(folder_path):
        try:
            os.rmdir(folder_path)
        except OSError:
            pass  # Ignore errors (e.g., folder not empty)

    messages.success(request, "Assignment deleted successfully.")
    return redirect('assignment_list')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import BookForm
from .models import Book

def book_list(request):
    books = Book.objects.all().order_by('-id')
    return render(request, 'lms/books_list.html', {'books': books})

def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, f"'{book.title}' was successfully added.")
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'lms/books_form.html', {'form': form})

def book_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(instance=book)

    # Disable all fields
    for field in form.fields.values():
        field.widget.attrs['disabled'] = 'disabled'

    return render(request, 'lms/books_form.html', {'form': form, 'is_view': True})


def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{book.title}' was successfully updated.")
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'lms/books_form.html', {'form': form})

def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    title = book.title
    book.delete()
    messages.success(request, f"'{title}' was successfully deleted.")
    return redirect('book_list')


from django.shortcuts import render, get_object_or_404
from .models import Book, BorrowRecord  # Adjust model names as per your app

def book_borrow_details(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    borrow_records = BorrowRecord.objects.filter(book=book)  # Replace with actual model name
    
    return render(request, 'lms/book_borrow_details.html', {
        'book': book,
        'borrow_records': borrow_records
    })

from django.shortcuts import render, redirect
from .forms import BorrowRecordForm
from .models import BorrowRecord
from datetime import date  # ⬅️ Add this import

def borrow_book_view(request):
    if request.method == 'POST':
        form = BorrowRecordForm(request.POST)
        if form.is_valid():
            borrow_record = form.save()
            messages.success(request, f"Book '{borrow_record.book.title}' successfully borrowed by {borrow_record.student}.")
            return redirect('book_borrow_details', book_id=borrow_record.book.id)
        else:
            messages.error(request, "")
    else:
        form = BorrowRecordForm()
    borrowed_data = {}
    borrow_records = BorrowRecord.objects.filter(returned=False).values('book_id', 'student_id')
    for record in borrow_records:
        borrowed_data.setdefault(record['book_id'], []).append(record['student_id'])

    return render(request, 'lms/borrow_book_form.html', {
        'form': form,
        'borrowed_data': borrowed_data  # For JS to check
    })




# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from .models import BorrowRecord

def borrow_record_details(request, record_id):
    borrow_record = get_object_or_404(BorrowRecord, id=record_id)

    # If form is submitted (book returned)
    if request.method == 'POST' and not borrow_record.returned:
        borrow_record.returned = True
        borrow_record.return_date = now().date()  # record the current date as return date
        borrow_record.save()

        # Increase the available copies of the book
        book = borrow_record.book
        book.available_copies += 1
        book.save()

        return redirect('book_list')  # or any other redirect

    return render(request, 'lms/borrow_record_details.html', {
        'borrow_record': borrow_record
    })

from .forms import EmployeeStudyMaterialForm
from .models import EmployeeStudyMaterial
from master.models import Course, Subject, CourseType, Employee, StudentDatabase, EmployeeSubjectAssignment

def create_study_material(request):
    selected_program_type_id = request.GET.get('program_type')
    selected_academic_year = request.GET.get('academic_year')
    selected_course_id = request.GET.get('course')
    selected_semester_id = request.GET.get('semester')
    selected_subject_id = request.GET.get('subject')
    selected_faculty_id = request.GET.get('faculty')

    filtered_courses = Course.objects.none()
    filtered_subjects = Subject.objects.none()
    semester_display = []
    faculty_members = Employee.objects.none()

    if selected_course_id and selected_semester_id and selected_subject_id:
        faculty_assignments = EmployeeSubjectAssignment.objects.filter(
            course_id=selected_course_id,
            semester=selected_semester_id,
            subject_id=selected_subject_id
        ).select_related('employee')
        faculty_members = Employee.objects.filter(id__in=[fa.employee.id for fa in faculty_assignments])

    if selected_program_type_id:
        filtered_courses = Course.objects.filter(course_type_id=selected_program_type_id)

    if selected_course_id:
        try:
            selected_course = Course.objects.get(id=selected_course_id)
            is_pu = selected_course.course_type.name.strip().lower() == "puc regular"
            total = selected_course.duration_years if is_pu else selected_course.total_semesters or 0
            semester_display = [{'id': i, 'label': f"{selected_course.name} {i}"} for i in range(1, total + 1)]
            filtered_subjects = Subject.objects.filter(course_id=selected_course_id).order_by('name')
        except Course.DoesNotExist:
            pass

    academic_years = []
    if selected_program_type_id:
        academic_years = (
            StudentDatabase.objects
            .filter(course__course_type_id=selected_program_type_id)
            .values_list('academic_year', flat=True)
            .distinct()
            .order_by('-academic_year')
        )

    if request.method == 'POST':
        form = EmployeeStudyMaterialForm(request.POST, request.FILES, faculty_queryset=faculty_members)
        if form.is_valid():
            material = form.save(commit=False)
            material.program_type_id = selected_program_type_id
            material.academic_year = selected_academic_year
            material.course_id = selected_course_id
            material.semester_number = selected_semester_id
            material.subject_id = selected_subject_id
            material.save()
            return redirect('employee_study_material_list')
    else:
        form = EmployeeStudyMaterialForm(faculty_queryset=faculty_members)

    return render(request, 'lms/employee_study_material_form.html', {
        'form': form,
        'program_types': CourseType.objects.all().order_by('name'),
        'academic_years': academic_years,
        'courses': filtered_courses,
        'semesters': semester_display,
        'subjects': filtered_subjects,
        'faculty_members': faculty_members,
        'selected': {
            'program_type': selected_program_type_id,
            'academic_year': selected_academic_year,
            'course': selected_course_id,
            'semester': selected_semester_id,
            'subject': selected_subject_id,
            'faculty': selected_faculty_id,
        },
        'is_edit': False
    })

from .forms import EmployeeStudyMaterialForm
from .models import EmployeeStudyMaterial
from master.models import Course, Subject, CourseType, Employee, StudentDatabase, EmployeeSubjectAssignment

def edit_study_material(request, pk):
    instance = get_object_or_404(EmployeeStudyMaterial, pk=pk)

    selected_program_type_id = instance.program_type_id
    selected_academic_year = instance.academic_year
    selected_course_id = instance.course_id
    selected_semester_id = instance.semester_number
    selected_subject_id = instance.subject_id
    selected_faculty_id = instance.faculty_id if hasattr(instance, 'faculty_id') else None

    filtered_courses = Course.objects.filter(course_type_id=selected_program_type_id)
    filtered_subjects = Subject.objects.filter(course_id=selected_course_id).order_by('name')
    semester_display = []
    faculty_members = Employee.objects.none()

    try:
        selected_course = Course.objects.get(id=selected_course_id)
        is_pu = selected_course.course_type.name.strip().lower() == "puc regular"
        total = selected_course.duration_years if is_pu else selected_course.total_semesters or 0
        semester_display = [{'id': i, 'label': f"{selected_course.name} {i}"} for i in range(1, total + 1)]
    except Course.DoesNotExist:
        pass

    if selected_course_id and selected_semester_id and selected_subject_id:
        faculty_assignments = EmployeeSubjectAssignment.objects.filter(
            course_id=selected_course_id,
            semester=selected_semester_id,
            subject_id=selected_subject_id
        ).select_related('employee')
        faculty_members = Employee.objects.filter(id__in=[fa.employee.id for fa in faculty_assignments])

    academic_years = (
        StudentDatabase.objects
        .filter(course__course_type_id=selected_program_type_id)
        .values_list('academic_year', flat=True)
        .distinct()
        .order_by('-academic_year')
    )

    if request.method == 'POST':
        form = EmployeeStudyMaterialForm(request.POST, request.FILES, instance=instance, faculty_queryset=faculty_members)
        if form.is_valid():
            material = form.save(commit=False)
            material.program_type_id = selected_program_type_id
            material.academic_year = selected_academic_year
            material.course_id = selected_course_id
            material.semester_number = selected_semester_id
            material.subject_id = selected_subject_id
            material.save()
            return redirect('employee_study_material_list')
    else:
        form = EmployeeStudyMaterialForm(instance=instance, faculty_queryset=faculty_members)

    return render(request, 'lms/employee_study_material_form.html', {
        'form': form,
        'program_types': CourseType.objects.all().order_by('name'),
        'academic_years': academic_years,
        'courses': filtered_courses,
        'semesters': semester_display,
        'subjects': filtered_subjects,
        'faculty_members': faculty_members,
        'selected': {
            'program_type': selected_program_type_id,
            'academic_year': selected_academic_year,
            'course': selected_course_id,
            'semester': selected_semester_id,
            'subject': selected_subject_id,
            'faculty': selected_faculty_id,
        },
        'is_edit': True
    })


def employee_study_material_list(request):
    study_materials = EmployeeStudyMaterial.objects.all().order_by('-created_at')
    return render(request, 'lms/employee_study_material_list.html', {
        'study_materials': study_materials
    })

def delete_employee_study_material(request, pk):
    material = get_object_or_404(EmployeeStudyMaterial, pk=pk)
    material.delete()
    return redirect('employee_study_material_list')



#This is exam

from django.shortcuts import render, redirect, get_object_or_404
from .models import Exam
from .forms import ExamForm
from master.models import Course, Subject, CourseType, StudentDatabase, Employee

def exam_list(request):
    exams = Exam.objects.all().select_related('subject', 'course', 'faculty')
    return render(request, 'lms/employee_exam_create_list.html', {'exams': exams})

def create_exam(request):
    selected_program_type_id = request.GET.get('program_type')
    selected_academic_year = request.GET.get('academic_year')
    selected_course_id = request.GET.get('course')
    selected_semester_id = request.GET.get('semester')
    selected_subject_id = request.GET.get('subject')

    filtered_courses = Course.objects.none()
    filtered_subjects = Subject.objects.none()
    semester_display = []

    if selected_program_type_id:
        filtered_courses = Course.objects.filter(course_type_id=selected_program_type_id)

    if selected_course_id:
        try:
            selected_course = Course.objects.get(id=selected_course_id)
            is_pu = selected_course.course_type.name.strip().lower() == "puc regular"
            total = selected_course.duration_years if is_pu else selected_course.total_semesters or 0
            semester_display = [{'id': i, 'label': f"{selected_course.name} {i}"} for i in range(1, total + 1)]
            filtered_subjects = Subject.objects.filter(course_id=selected_course_id).order_by('name')
        except Course.DoesNotExist:
            pass

    academic_years = []
    if selected_program_type_id:
        academic_years = (
            StudentDatabase.objects
            .filter(course__course_type_id=selected_program_type_id)
            .values_list('academic_year', flat=True)
            .distinct()
            .order_by('-academic_year')
        )

    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.program_type_id = selected_program_type_id
            exam.academic_year = selected_academic_year
            exam.course_id = selected_course_id
            exam.semester_number = selected_semester_id
            exam.subject_id = selected_subject_id
            exam.save()
            return redirect('exam_list')
    else:
        form = ExamForm()

    context = {
        'form': form,
        'program_types': CourseType.objects.all(),
        'academic_years': academic_years,
        'courses': filtered_courses,
        'semesters': semester_display,
        'subjects': filtered_subjects,
        'faculties': Employee.objects.all(),
        'selected': {
            'program_type': selected_program_type_id,
            'academic_year': selected_academic_year,
            'course': selected_course_id,
            'semester': selected_semester_id,
            'subject': selected_subject_id,
        }
    }

    return render(request, 'lms/employee_exam_create_form.html', context)

def edit_exam(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            return redirect('exam_list')
    else:
        form = ExamForm(instance=exam)
    return render(request, 'lms/employee_exam_create_form.html', {'form': form, 'edit_mode': True, 'exam': exam})

def view_exam(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    return render(request, 'lms/employee_exam_create_form.html', {'view_mode': True, 'exam': exam})

def delete_exam(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    exam.delete()
    return redirect('exam_list')


from datetime import date
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render, redirect
from lms.models import CalendarEvent, Assignment, AssignmentSubmission, BorrowRecord
from master.models import StudentDatabase
from fees.models import StudentFeeCollection
import calendar
import json
import holidays
from hijridate import Hijri
from pathlib import Path


def hijri_to_gregorian(year, month, day):
    for offset in [-1, 0, 1]:
        try:
            g = Hijri(year + offset, month, day).to_gregorian()
            if g.year == year:
                return g
        except Exception:
            continue
    return None


def student_calendar_form(request):
    today = timezone.localdate()
    now = timezone.now()

    year = int(request.GET.get('year') or today.year)
    month = int(request.GET.get('month') or today.month)
    month = month if 1 <= month <= 12 else today.month

    prev_month, prev_year = (12, year - 1) if month == 1 else (month - 1, year)
    next_month, next_year = (1, year + 1) if month == 12 else (month + 1, year)

    cal = calendar.Calendar(firstweekday=6)
    month_days = list(cal.monthdayscalendar(year, month))
    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    student_userid = request.COOKIES.get('student_userid')
    if not student_userid:
        return redirect('student_login_view')

    try:
        student = StudentDatabase.objects.get(student_userid=student_userid)
    except StudentDatabase.DoesNotExist:
        return redirect('student_login_view')

    # Calendar events
    future_events_qs = CalendarEvent.objects.filter(
        Q(date__gt=today) | Q(date=today, time__gte=now.time())
    ).select_related('event_type')

    future_events = [{
        'id': e.id,
        'title': e.title,
        'description': e.description or '',
        'date': e.date.isoformat(),
        'time': e.time.strftime('%H:%M') if e.time else '',
        'event_type': e.event_type.name if e.event_type else '',
    } for e in future_events_qs]

    extra_events = []

    # ✅ Fix: Get submitted assignment IDs using student foreign key (not student_userid)
    # Filter out assignments that have been submitted or graded by this student
    submitted_ids = AssignmentSubmission.objects.filter(
        student_userid=student_userid,
        status__in=['submitted', 'graded']
    ).values_list('assignment_id', flat=True)

    # Get only assignments that are pending submission
    pending_assignments = Assignment.objects.filter(
        academic_year=student.academic_year,
        program_type=student.course_type,
        course=student.course,
        semester_number=student.semester or student.current_year,
        due_date__gte=today
    ).exclude(id__in=submitted_ids)


    for a in pending_assignments:
        if a.due_date >= today:
            extra_events.append({
                "title": f"Assignment Due: {a.title}",
                "date": a.due_date.isoformat(),
                "event_type": "AssignmentDue",
                "description": "",
            })

    # Library Return
    borrow_records = BorrowRecord.objects.filter(student__student_userid=student_userid, returned=False)
    for br in borrow_records:
        if br.return_due_date:
            title = "Library Return Due" if br.return_due_date >= today else "Library Return Overdue!"
            extra_events.append({
                "title": title,
                "date": br.return_due_date.isoformat(),
                "event_type": "LibraryReturn",
                "description": ""
            })

    # Fee Due
    fees = StudentFeeCollection.objects.filter(student_userid=student_userid)
    for fee in fees:
        balance = (fee.amount or 0) - (fee.paid_amount or 0) - getattr(fee, 'applied_discount', 0)
        if balance > 0 and fee.due_date:
            title = "Fee Due" if fee.due_date >= today else "Fee Overdue!"
            extra_events.append({
                "title": title,
                "date": fee.due_date.isoformat(),
                "event_type": "FeeDue",
                "description": ""
            })

    # National Holidays - India
    india_holidays = holidays.India(years=year)
    all_holidays = [{"date": d, "name": n} for d, n in india_holidays.items() if d.year == year]

    # Fixed holidays
    fixed = {
        (1, 14): "Makara Sankranti", (4, 10): "Mahavir Jayanti", (4, 14): "Dr. Ambedkar Jayanti",
        (4, 18): "Good Friday", (4, 30): "Basava Jayanti", (5, 1): "May Day",
        (8, 15): "Independence Day", (10, 2): "Gandhi Jayanti",
        (11, 1): "Kannada Rajyotsava", (12, 25): "Christmas"
    }
    for (m, d), name in fixed.items():
        dt = date(year, m, d)
        if dt not in india_holidays:
            all_holidays.append({"date": dt, "name": name})

    # Islamic holidays
    islamic_dates = [
        (10, 1, "Eid al‑Fitr"),
        (12, 10, "Bakrid (Eid al‑Adha)"),
        (3, 12, "Eid Milad")
    ]
    for hijri_month, hijri_day, name in islamic_dates:
        g_date = hijri_to_gregorian(year, hijri_month, hijri_day)
        if g_date:
            all_holidays.append({"date": g_date, "name": name})

    # Hindu festivals from JSON
    try:
        json_path = Path(__file__).parent / "hindu_festivals.json"
        with open(json_path, 'r') as f:
            festival_data = json.load(f)
            for fest in festival_data.get(str(year), []):
                try:
                    dt = date(year, fest["month"], fest["day"])
                    all_holidays.append({"date": dt, "name": fest["name"]})
                except ValueError:
                    continue
    except Exception as e:
        print(f"Error loading Hindu festivals: {e}")

    # Filter holidays by current month
    month_holidays = [h for h in all_holidays if h["date"].month == month]

    # Combine all event types
    combined_events = future_events + extra_events

    context = {
        'today': today,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'month_days': month_days,
        'weekdays': weekdays,
        'events_json': json.dumps(combined_events, default=str),
        'gov_holidays_json': json.dumps([
            {"date": h["date"].isoformat(), "name": h["name"]} for h in all_holidays
        ]),
        'month_holidays': month_holidays,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'due_assignments_count': sum(1 for e in extra_events if e["event_type"] == "AssignmentDue"),
        'fee_due_count': sum(1 for e in extra_events if e["event_type"] == "FeeDue"),
        'upcoming_exams_count': 0,
        'total_events_count': len(combined_events),
        'due_date_types': ['AssignmentDue', 'LibraryReturn', 'FeeDue'],
    }

    return render(request, 'lms/student_calendar.html', context)

    

from django.http import JsonResponse
from lms.models import CalendarEvent

def academic_events(request):
    events = []

    for event in CalendarEvent.objects.all():
        events.append({
            'title': f"{event.title} ({event.event_type.name})",
            'start': event.date.isoformat(),
        })

    return JsonResponse(events, safe=False)

