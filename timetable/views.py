from django.shortcuts import render,redirect

# Create your views here.
from django.shortcuts import render, get_object_or_404
from master.models import  Semester,  Employee, Subject,Course,CourseType
from .models import   TimetableEntry,  TimeSlot
from .forms import TimeSlotForm,TimetableEntryForm





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

def get_date_for_weekday(base_date, target_weekday):
    # Get the target date for a given weekday name, relative to base_date
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    if target_weekday not in days:
        return base_date
    current_weekday = base_date.weekday()  # Monday = 0
    target_weekday_index = days.index(target_weekday)
    delta = target_weekday_index - current_weekday
    return base_date + timedelta(days=delta)

def daily_timetable(request):
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    # Get today's weekday name; fallback to Friday if weekend
    today_day = timezone.now().strftime('%A')
    if today_day in ['Saturday', 'Sunday']:
        today_day = 'Friday'

    today_date = timezone.localdate()
    selected_day = request.GET.get('day', today_day)

    # Default values
    DEFAULT_COURSE_TYPE_NAME = "PUC"
    DEFAULT_COURSE_NAME = "SEBA"
    DEFAULT_SEMESTER_NUMBER = 1

    # Resolve defaults
    default_course_type = CourseType.objects.filter(name__icontains=DEFAULT_COURSE_TYPE_NAME).first()
    default_course = Course.objects.filter(name__iexact=DEFAULT_COURSE_NAME).first()
    default_semester = Semester.objects.filter(course=default_course, number=DEFAULT_SEMESTER_NUMBER).first() if default_course else None

    # Get values from request or fallback
    course_type = request.GET.get('course_type', default_course_type.name if default_course_type else '')
    course_id = request.GET.get('course', str(default_course.id) if default_course else '')
    semester_id = request.GET.get('semester', str(default_semester.id) if default_semester else '')

    # Build filters
    filters = {}
    if semester_id:
        filters['semester_id'] = semester_id
    if course_id:
        filters['subject__course_id'] = course_id
    if course_type:
        filters['subject__course__course_type__name__iexact'] = course_type
    if selected_day:
        filters['day__iexact'] = selected_day

    # Get actual date for the selected weekday
    target_date = get_date_for_weekday(today_date, selected_day)

    # Query timetable entries
    entries = TimetableEntry.objects.filter(**filters).select_related(
        'faculty', 'subject', 'subject__course', 'semester'
    ).order_by('time_slot__start_time')

    for entry in entries:
        # Check for substitution for this entry on target_date
        substitution = DailySubstitution.objects.filter(
            timetable_entry=entry,
            date=target_date
        ).select_related('substitute_faculty', 'updated_subject').first()

        if substitution:
            entry.faculty = substitution.substitute_faculty
            entry.subject = substitution.updated_subject or entry.subject
            entry.is_substituted = True
            entry.substitution_id = substitution.id
        else:
            entry.is_substituted = False
            entry.substitution_id = None

        # Fetch attendance
        if entry.faculty:
            att = attendance.objects.filter(employee=entry.faculty, date=target_date).first()
            entry.attendance_status = att.status if att else 'Absent'
        else:
            entry.attendance_status = 'Absent'

    # Dropdown options
    course_types = CourseType.objects.all()
    courses = Course.objects.filter(course_type__name__iexact=course_type) if course_type else Course.objects.all()
    semesters = Semester.objects.filter(
        id__in=TimetableEntry.objects.filter(subject__course_id=course_id).values_list('semester_id', flat=True).distinct()
    ) if course_id else Semester.objects.all()

    return render(request, 'timetable/daily.html', {
        'semesters': semesters,
        'courses': courses,
        'course_types': course_types,
        'week_days': week_days,
        'entries': entries,
        'selected_semester': Semester.objects.filter(id=semester_id).first() if semester_id else None,
        'selected_day': selected_day,
        'selected_semester_id': semester_id,
        'selected_course_id': course_id,
        'selected_course_type': course_type,
        'selected_date': target_date,
    })

from django.shortcuts import render, get_object_or_404, redirect
from .models import TimetableEntry, Employee, DailySubstitution, Subject
from datetime import datetime
from master.models import Subject
from django.utils.dateparse import parse_date
from datetime import datetime
from attendence.models import attendance  
from core.utils import get_logged_in_user,log_activity

def timetable_form_edit(request, entry_id):
    entry = get_object_or_404(TimetableEntry, id=entry_id)
    
    # Get the date (ensure it's in correct format)
    raw_date = request.GET.get('date')
    date = parse_date(raw_date) if raw_date else datetime.today().date()

    day = entry.day
    timeslot = entry.time_slot
    entry_start = timeslot.start_time
    entry_end = timeslot.end_time

    # Get eligible faculties
    eligible_faculties = Employee.objects.filter(role__in=['Primary', 'Secondary'])

    # Get busy faculty IDs who have overlapping timetable entries
    busy_faculties = TimetableEntry.objects.filter(
        day=day,
        time_slot__start_time__lt=entry_end,
        time_slot__end_time__gt=entry_start,
    ).values_list('faculty_id', flat=True)

    # Filter to get free ones
    free_faculties = eligible_faculties.exclude(id__in=busy_faculties)

    # 🔍 Filter by present status on the selected date
 

    present_faculty_ids = attendance.objects.filter(
        date=date,
        status__in=['Present', 'Late']
    ).values_list('employee_id', flat=True)

    # Final filtered faculties: free and present
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









from django.shortcuts import render
from datetime import date, timedelta
from .models import TimetableEntry, TimeSlot
from master.models import Semester, Course, CourseType
from attendence.models import attendance  # import your attendance model

def get_date_for_weekday(base_date, target_weekday):
    week_day_map = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    base_weekday = base_date.weekday()  # 0 = Monday
    target_index = week_day_map.index(target_weekday)
    delta = target_index - base_weekday
    return base_date + timedelta(days=delta)

def weekly_timetable_view(request, course_id=None, semester_number=None):
    # 👇 Default values (customize if needed)
    DEFAULT_COURSE_TYPE_NAME = "PUC"
    DEFAULT_COURSE_NAME = "SEBA"
    DEFAULT_SEMESTER_NUMBER = 1

    # Get values from request or fallback to parameters
    selected_course_type = request.GET.get('course_type')
    selected_course = request.GET.get('course') or course_id
    selected_semester = request.GET.get('semester') or semester_number

    # 👇 Use defaults if none selected
    if not selected_course_type or not selected_course or not selected_semester:
        default_course_type = CourseType.objects.filter(name__icontains=DEFAULT_COURSE_TYPE_NAME).first()
        if default_course_type:
            selected_course_type = str(default_course_type.id)

            default_course = Course.objects.filter(course_type=default_course_type, name__icontains=DEFAULT_COURSE_NAME).first()
            if default_course:
                selected_course = str(default_course.id)

                default_semester = Semester.objects.filter(course=default_course, number=DEFAULT_SEMESTER_NUMBER).first()
                if default_semester:
                    selected_semester = str(default_semester.number)

    # Convert selected values to integers
    selected_course_type_id = int(selected_course_type) if selected_course_type else None
    selected_course_id = int(selected_course) if selected_course else None
    selected_semester_number = int(selected_semester) if selected_semester else None

    # Load data for filters and timetable
    course_types = CourseType.objects.all()
    courses = Course.objects.filter(course_type_id=selected_course_type_id) if selected_course_type_id else Course.objects.none()
    semesters = Semester.objects.filter(course_id=selected_course_id) if selected_course_id else Semester.objects.none()

    semester = Semester.objects.filter(course_id=selected_course_id, number=selected_semester_number).first()

    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    timetable = {}
    time_slots = []
    today = date.today()

    if semester:
        for day in week_days:
            entries = list(TimetableEntry.objects.filter(semester=semester, day=day).order_by('time_slot__start_time'))
            target_date = get_date_for_weekday(today, day)

            for entry in entries:
                att = None
                if entry.faculty:
                    att = attendance.objects.filter(employee=entry.faculty, date=target_date).first()
                    entry.attendance_status = att.status if att else 'Absent'
                else:
                    entry.attendance_status = 'Absent'
            timetable[day] = entries

        time_slot_set = {entry.time_slot for entries in timetable.values() for entry in entries}
        time_slots = sorted(time_slot_set, key=lambda ts: ts.start_time)

    return render(request, 'timetable/weekly.html', {
        'course_types': course_types,
        'courses': courses,
        'semesters': semesters,
        'selected_course_type': selected_course_type,
        'selected_course': selected_course,
        'selected_semester': selected_semester,
        'semester': semester,
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
from .forms import TimetableEntryForm
from .models import TimetableEntry

from django.shortcuts import render, get_object_or_404, redirect
from .models import TimetableEntry
from .forms import TimetableEntryForm

from django.shortcuts import get_object_or_404


def timetable_form_add(request):
    if request.method == 'POST':
        form = TimetableEntryForm(request.POST)
        if form.is_valid():
            semester = form.cleaned_data.get('semester')
            day = form.cleaned_data.get('day')
            time_slot = form.cleaned_data.get('time_slot')

            # Check for existing entry for same day, semester, time_slot
            existing_entry = TimetableEntry.objects.filter(
                semester=semester,
                day=day,
                time_slot=time_slot
            ).first()
            user = get_logged_in_user(request)
            if existing_entry:
                form = TimetableEntryForm(request.POST, instance=existing_entry)
                saved_entry = form.save()
                log_activity(user, 'edited', saved_entry)
            else:
                saved_entry = form.save()
                log_activity(user, 'created', saved_entry)

            return redirect('weekly_timetable', course_id=semester.course.id, semester_number=semester.number)
        else:
            print("Form errors:", form.errors)
    else:
        form = TimetableEntryForm()

    return render(request, 'timetable/add_entry.html', {'form': form})



from django.http import JsonResponse
from .models import Subject

def get_faculty_by_subject(request):
    subject_id = request.GET.get('subject_id')
    if subject_id:
        try:
            subject = Subject.objects.get(id=subject_id)
            faculty = subject.faculty  # assuming `Subject` has a FK to Faculty
            return JsonResponse({'faculty_name': faculty.name, 'faculty_id': faculty.id})
        except Subject.DoesNotExist:
            return JsonResponse({'error': 'Subject not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)




from django.shortcuts import render
from django.db.models import Count
from timetable.models import TimetableEntry
from master.models import Course

def faculty_classes_table(request):
    courses = Course.objects.all()

    # Default SEBA course id
    try:
        seba_course = Course.objects.filter(name__iexact='SEBA').first()
        seba_course_id = seba_course.id
    except Course.DoesNotExist:
        seba_course_id = None

    course_param = request.GET.get('course')
    
    if course_param == "":
        # All selected
        selected_course_id = None
    elif course_param:
        try:
            selected_course_id = int(course_param)
        except ValueError:
            selected_course_id = seba_course_id
    else:
        # No GET param -> default to SEBA
        selected_course_id = seba_course_id

    print("Selected Course ID:", selected_course_id)  # For debug

    # Base query
    faculty_subject_class_counts = TimetableEntry.objects.values(
        'faculty__id',
        'faculty__name',
        'subject__id',
        'subject__name',
        'subject__course__id',
        'subject__course__name'
    ).annotate(class_count=Count('id')).filter(faculty__isnull=False)

    # Filter only if specific course is selected
    if selected_course_id:
        faculty_subject_class_counts = faculty_subject_class_counts.filter(subject__course__id=selected_course_id)

    faculty_subject_class_counts = faculty_subject_class_counts.order_by('faculty__name', 'subject__name')

    return render(request, 'timetable/faculty_classes_table.html', {
        'faculty_subject_class_counts': faculty_subject_class_counts,
        'courses': courses,
        'selected_course_id': selected_course_id
    })

