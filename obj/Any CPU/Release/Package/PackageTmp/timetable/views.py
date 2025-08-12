
from django.shortcuts import render, get_object_or_404
from master.models import Semester, Employee, Subject, Course, CourseType
from .models import TimetableEntry, TimeSlot
from .forms import TimeSlotForm, TimetableEntryForm
from datetime import datetime
import sys

def timetable_dashboard(request):
    # Active Programs: all CourseTypes
    program_qs = CourseType.objects.all()
    active_programs_count = program_qs.count()
    active_programs_names = ", ".join(program_qs.values_list('name', flat=True))

    # Current time and weekday (server timezone, adjust if needed)
    now = datetime.now()
    today_weekday = now.strftime('%A')  # e.g., "Friday"
    # Cross-platform hour formatting (no leading zero)
    current_time = now.strftime('%I:%M %p').lstrip('0')
    # Total Classes Today (all TimetableEntries scheduled for today)
    total_classes_today = TimetableEntry.objects.filter(day=today_weekday).count()

    # Weekly Classes (all entries in a week)
    weekly_classes = TimetableEntry.objects.count()

    # Total subjects (for your summary, if needed)
    total_subjects = Subject.objects.count()

    context = {
        'total_classes_today': total_classes_today,
        'active_programs_count': active_programs_count,
        'active_programs_names': active_programs_names,
        'current_time': current_time,
        'today_weekday': today_weekday,
        'weekly_classes': weekly_classes,
        'total_subjects': total_subjects,
    }
    return render(request, 'timetable/timetable_dashboard.html', context)


   





from django.shortcuts import render
from django.utils import timezone
from .models import TimetableEntry, TimeSlot
from master.models import Semester, Course, CourseType
from django.shortcuts import render
from django.utils import timezone


from django.shortcuts import render
from django.utils import timezone
from timetable.models import TimetableEntry
from master.models import Course, CourseType, Semester

from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import date, datetime
from .models import TimetableEntry, TimeSlot
from master.models import Semester, Course, CourseType
from attendence.models import attendance
from master.models import Employee  # Adjust the import as per your model location



def get_date_for_weekday(reference_date, weekday_name):
    weekday_map = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2,
        'Thursday': 3, 'Friday': 4
    }
    target_weekday = weekday_map.get(weekday_name)
    if target_weekday is None:
        return reference_date
    return reference_date - timezone.timedelta(days=(reference_date.weekday() - target_weekday) % 7)
from datetime import timedelta
from django.utils import timezone
from .models import DailySubstitution  # Ensure this import is present

from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import TimetableEntry, DailySubstitution
from master.models import Course, CourseType
from attendence.models import attendance

def get_date_for_weekday(base_date, target_weekday):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    if target_weekday not in days:
        return base_date
    current_weekday = base_date.weekday()  # 0 = Monday
    target_weekday_index = days.index(target_weekday)
    delta = target_weekday_index - current_weekday
    return base_date + timedelta(days=delta)


from django.utils import timezone
from django.shortcuts import render
from .models import TimetableEntry, Semester, TimeSlot
from master.models import Course

def daily_timetable(request):
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    today_day = timezone.now().strftime('%A')
    if today_day not in week_days:
        today_day = 'Monday'

    # Get from GET params or use defaults
    selected_day = request.GET.get('day') or today_day
    course_id = request.GET.get('course')
    semester_number = request.GET.get('semester')

    # 🔁 Default to first course if not selected
    if not course_id:
        first_course = Course.objects.filter(is_active=True).first()
        if first_course:
            course_id = str(first_course.id)

    # 🔁 Default to first semester if not selected
    if not semester_number:
        first_semester = Semester.objects.first()
        if first_semester:
            semester_number = str(first_semester.number)

    # Apply filters
    filters = {'day__iexact': selected_day}
    if course_id:
        filters['course_id'] = course_id
    if semester_number:
        filters['semester_number'] = semester_number

    time_slots = TimeSlot.objects.all().order_by('start_time')
    entries = TimetableEntry.objects.filter(**filters).select_related('faculty', 'subject', 'time_slot')

    timetable = {slot: None for slot in time_slots}
    for slot in time_slots:
        timetable[slot] = entries.filter(time_slot=slot).first()

    return render(request, 'timetable/daily.html', {
        'courses': Course.objects.filter(is_active=True),
        'semesters': Semester.objects.all(),
        'time_slots': time_slots,
        'timetable': timetable,
        'selected_course_id': course_id,
        'selected_semester_number': semester_number,
        'selected_day': selected_day,
        'today_day': today_day,
        'week_days': week_days,
        'entries': entries,
    })



from django.shortcuts import render, get_object_or_404, redirect
from .models import TimetableEntry, Employee, DailySubstitution, Subject
from datetime import datetime
from master.models import Subject
from django.utils.dateparse import parse_date
from datetime import datetime
from attendence.models import attendance  
from core.utils import get_logged_in_user,log_activity

from django.contrib import messages  # ✅ Add this import at the top if not already

def timetable_form_edit(request, entry_id):
    entry = get_object_or_404(TimetableEntry, id=entry_id)
    
    # Get the date
    raw_date = request.GET.get('date')
    date = parse_date(raw_date) if raw_date else datetime.today().date()

    day = entry.day
    timeslot = entry.time_slot
    entry_start = timeslot.start_time
    entry_end = timeslot.end_time

    # Eligible faculties
    eligible_faculties = Employee.objects.filter(role__in=['Primary', 'Secondary'])

    # Busy faculties
    busy_faculties = TimetableEntry.objects.filter(
        day=day,
        time_slot__start_time__lt=entry_end,
        time_slot__end_time__gt=entry_start,
    ).values_list('faculty_id', flat=True)

    free_faculties = eligible_faculties.exclude(id__in=busy_faculties)

    # Present faculties
    present_faculty_ids = attendance.objects.filter(
        date=date,
        status__in=['Present', 'Late']
    ).values_list('employee_id', flat=True)

    available_faculties = free_faculties.filter(id__in=present_faculty_ids)

    if request.method == 'POST':
        faculty_id = request.POST.get('faculty')
        subject_id = request.POST.get('subject')

        faculty = get_object_or_404(Employee, id=faculty_id)
        subject = get_object_or_404(Subject, id=subject_id)

        substitution_obj, created = DailySubstitution.objects.update_or_create(
            timetable_entry=entry,
            date=date,
            defaults={
                'substitute_faculty': faculty,
                'updated_subject': subject
            }
        )

        user = get_logged_in_user(request)
        log_activity(user, 'assigned', substitution_obj)

        # ✅ Snackbar success message
        messages.success(
            request,
            f"Substitution assigned to {faculty.name} for {subject.name} on {date.strftime('%d-%b-%Y')}."
        )

        return redirect('daily_timetable')

    context = {
        'entry': entry,
        'free_faculties': available_faculties,
        'subjects': Subject.objects.all(),
        'date': date,
    }
    return render(request, 'timetable/substitute_timetable_entry.html', context)

from django.shortcuts import get_object_or_404, redirect, render
from .models import DailySubstitution

def timetable_form_delete(request, substitution_id):
    substitution = get_object_or_404(DailySubstitution, id=substitution_id)
    substitution.delete()

    # Redirect to the timetable page (you can add ?date=... later if needed)
    return redirect('daily_timetable')

from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_date
from datetime import datetime

def timetable_form_view(request, entry_id):
    entry = get_object_or_404(TimetableEntry, id=entry_id)

    raw_date = request.GET.get('date')
    date = parse_date(raw_date) if raw_date else datetime.today().date()

    substitution = DailySubstitution.objects.filter(timetable_entry=entry, date=date).first()

    free_faculties = [substitution.substitute_faculty] if substitution else []
    subjects = [substitution.updated_subject or entry.subject] if substitution else []

    context = {
        'entry': entry,
        'free_faculties': free_faculties,
        'subjects': subjects,
        'date': date,
        'readonly': True,
        'substitution': substitution,
    }
    return render(request, 'timetable/substitute_timetable_entry.html', context)



from django.http import JsonResponse
from master.models import Course

def get_semesters_by_course(request):
    if request.method == "POST":
        course_id = request.POST.get("course_id")

        # Ensure course_id is not None and is a digit
        if not course_id or not course_id.isdigit():
            return JsonResponse({'error': 'Invalid course ID'}, status=400)

        try:
            course = Course.objects.get(id=int(course_id))
            semester_list = []

            course_type_name = course.course_type.name.strip().lower()

            if course_type_name == "puc regular":
                total = course.duration_years or 0
                for i in range(1, total + 1):
                    semester_list.append({
                        'number': i,
                        'name': f"{course.name} {i}"
                    })
            else:
                total = course.total_semesters or 0
                for i in range(1, total + 1):
                    semester_list.append({
                        'number': i,
                        'name': f"{course.name} {i}"
                    })

            if not semester_list:
                semester_list.append({
                    'number': 0,
                    'name': "NOT APPLICABLE"
                })

            return JsonResponse({'semesters': semester_list})

        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=400)





from django.shortcuts import render
from datetime import date, timedelta
from .models import TimetableEntry, TimeSlot
from master.models import Course
from attendence.models import attendance

def get_date_for_weekday(base_date, target_weekday):
    week_day_map = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    base_weekday = base_date.weekday()  # 0 = Monday
    target_index = week_day_map.index(target_weekday)
    delta = target_index - base_weekday
    return base_date + timedelta(days=delta)

from django.shortcuts import render
from datetime import date
from .models import TimetableEntry
from master.models import Course, Semester
from attendence.models import attendance


def weekly_timetable_view(request, course_id, semester_number):
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    today = date.today()

    # Get course/semester from request or use defaults
    selected_course_id = request.GET.get('course')
    selected_semester_number = request.GET.get('semester')

    # Default course
    if not selected_course_id:
        first_course = Course.objects.filter(is_active=True).first()
        if first_course:
            selected_course_id = str(first_course.id)

    # Default semester based on selected course
    semesters = Semester.objects.filter(course_id=selected_course_id) if selected_course_id else Semester.objects.none()
    if not selected_semester_number and semesters.exists():
        selected_semester_number = str(semesters.first().number)

    # Fetch timetable
    timetable = {}
    time_slots_set = set()

    if selected_course_id and selected_semester_number:
        for day in week_days:
            entries = list(TimetableEntry.objects.filter(
                course_id=selected_course_id,
                semester_number=selected_semester_number,
                day=day
            ).select_related('time_slot', 'subject', 'faculty').order_by('time_slot__start_time'))

            target_date = get_date_for_weekday(today, day)
            for entry in entries:
                if entry.faculty:
                    att = attendance.objects.filter(employee=entry.faculty, date=target_date).first()
                    entry.attendance_status = att.status if att else 'Absent'
                else:
                    entry.attendance_status = 'Absent'

            timetable[day] = entries
            for entry in entries:
                time_slots_set.add(entry.time_slot)

    time_slots = sorted(time_slots_set, key=lambda ts: ts.start_time)

    return render(request, 'timetable/weekly.html', {
        'courses': Course.objects.filter(is_active=True),
        'semesters': semesters,
        'selected_course_id': str(selected_course_id) if selected_course_id else '',
        'selected_semester_number': str(selected_semester_number) if selected_semester_number else '',
        'week_days': week_days,
        'timetable': timetable,
        'time_slots': time_slots,
    })



# def weekly_timetable_view(request, course_id, semester_number):
#     semester = get_object_or_404(Semester, course__id=course_id, number=semester_number)
#     week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
#     timetable = {
#         day: TimetableEntry.objects.filter(semester=semester, day=day).order_by('time_slot')
#         for day in week_days
#     }
#     return render(request, 'timetable/weekly.html', {
#         'timetable': timetable, 'semester': semester
#     })


def faculty_timetable_view(request, faculty_id):
    faculty = get_object_or_404(Employee, id=faculty_id)
    entries = TimetableEntry.objects.filter(faculty=faculty).order_by('day', 'time_slot')
    return render(request, 'timetable/faculty.html', {
        'faculty': faculty, 'entries': entries
    })




from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import TimetableEntryForm
from .models import TimetableEntry
from master.models import Semester, Course,Subject, Employee
from core.utils import get_logged_in_user, log_activity

def timetable_form_add(request):
    if request.method == 'POST':
        form = TimetableEntryForm(request.POST)

        # --- Dynamically populate semester choices ---
        course_id = request.POST.get('course')
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                course_type_name = course.course_type.name.strip().lower()
                semester_list = []

                if course_type_name == "puc regular":
                    total = course.duration_years or 0
                    for i in range(1, total + 1):
                        semester_list.append((str(i), f"{course.name} {i}"))
                else:
                    total = course.total_semesters or 0
                    for i in range(1, total + 1):
                        semester_list.append((str(i), f"{course.name} {i}"))

                if not semester_list:
                    semester_list = [('0', "NOT APPLICABLE")]

                form.fields['semester_number'].choices = semester_list

            except Course.DoesNotExist:
                pass

        # --- Filter subjects based on selected course and semester ---
        semester_number = request.POST.get('semester_number')
        subject_id = request.POST.get('subject')
        if course_id and semester_number:
            subjects = Subject.objects.filter(
                course_id=course_id,
                semester=semester_number
            ).order_by('name')
            form.fields['subject'].queryset = subjects

        # --- Filter faculty based on subject assignment ---
        if course_id and semester_number and subject_id:
            assigned_faculty_qs = EmployeeSubjectAssignment.objects.filter(
                course_id=course_id,
                semester=semester_number,
                subject_id=subject_id
            ).select_related('employee')

            faculty_ids = [a.employee.id for a in assigned_faculty_qs]
            faculty_queryset = Employee.objects.filter(id__in=faculty_ids)

            form.fields['faculty'].queryset = faculty_queryset

            # ✅ Preselect the first faculty if none selected
            if not request.POST.get('faculty') and faculty_queryset.exists():
                form.initial['faculty'] = faculty_queryset.first().id

        # --- Save logic ---
        if form.is_valid():
            cleaned_data = form.cleaned_data
            day = cleaned_data['day']
            time_slot = cleaned_data['time_slot']
            course = cleaned_data['course']
            semester_number = cleaned_data['semester_number']

            existing_entry = TimetableEntry.objects.filter(
                day=day,
                time_slot=time_slot,
                course=course,
                semester_number=semester_number
            ).first()

            if existing_entry:
                existing_entry.subject = cleaned_data['subject']
                existing_entry.faculty = cleaned_data['faculty']
                existing_entry.room = cleaned_data['room']
                existing_entry.save()

                user = get_logged_in_user(request)
                log_activity(user, 'edited', existing_entry)

                messages.success(request, "Existing timetable entry updated successfully.")
            else:
                saved_entry = form.save(commit=False)
                user = get_logged_in_user(request)
                saved_entry.save()
                log_activity(user, 'created', saved_entry)

                messages.success(request, "Timetable entry saved successfully.")

            return redirect('weekly_timetable', course_id=course.id, semester_number=semester_number)
        else:
            messages.error(request, "Form submission failed. Please correct the highlighted errors.")

    else:
        form = TimetableEntryForm()

    return render(request, 'timetable/add_entry.html', {'form': form})


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_subjects_by_course_and_semester(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        semester = str(request.POST.get('semester')).strip()  # 🔁 Ensure string comparison

        print(f"🔵 View called\nCourse ID: {course_id}\nSemester: {semester} (type: {type(semester)})")

        subjects = Subject.objects.filter(course_id=course_id, semester=semester)

        print(f"Subjects found: {subjects}")
        print(f"SQL Query: {subjects.query}")

        subject_data = [{'id': subject.id, 'name': subject.name} for subject in subjects]
        return JsonResponse({'subjects': subject_data})


# from django.http import JsonResponse
# from .models import Subject


from django.http import JsonResponse
from master.models import Subject, EmployeeSubjectAssignment

def get_faculty_by_subject(request):
    if request.method != "GET":
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    subject_id = request.GET.get('subject_id')
    if not subject_id:
        return JsonResponse({'error': 'Subject ID is required'}, status=400)

    try:
        assignments = EmployeeSubjectAssignment.objects.filter(subject_id=subject_id).select_related('employee')

        faculty_list = []
        for assignment in assignments:
            employee = assignment.employee
            name_with_role = f"{employee.name} ({employee.role})" if employee.role else employee.name
            faculty_list.append({
                'id': employee.id,
                'name': name_with_role
            })

        default_faculty = assignments.first().employee.id if assignments.exists() else None

        return JsonResponse({
            'faculty': faculty_list,
            'default': default_faculty
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from django.shortcuts import render
from django.db.models import Count
from timetable.models import TimetableEntry
from master.models import Course

def faculty_classes_table(request):
    courses = Course.objects.all()

    course_param = request.GET.get('course')
    selected_course_id = None

    if course_param:
        try:
            selected_course_id = int(course_param)
        except ValueError:
            pass  # Leave selected_course_id as None

    print("Selected Course ID:", selected_course_id)  # Debug

    # Base query
    faculty_subject_class_counts = TimetableEntry.objects.filter(faculty__isnull=False)

    # Filter by course if selected
    if selected_course_id:
        faculty_subject_class_counts = faculty_subject_class_counts.filter(subject__course__id=selected_course_id)

    # Group by faculty and subject to avoid overcounting
    faculty_subject_class_counts = faculty_subject_class_counts.values(
        'faculty__id',
        'faculty__name',
        'subject__id',
        'subject__name',
        'subject__course__name'
    ).annotate(class_count=Count('id')).order_by('faculty__name', 'subject__name')

    return render(request, 'timetable/faculty_classes_table.html', {
        'faculty_subject_class_counts': faculty_subject_class_counts,
        'courses': courses,
        'selected_course_id': selected_course_id
    })


