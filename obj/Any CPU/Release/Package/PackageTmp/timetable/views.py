from django.shortcuts import render,redirect

# Create your views here.
from django.shortcuts import render, get_object_or_404
from master.models import  Semester,  Employee, Subject,Course,CourseType
from .models import   TimetableEntry,  TimeSlot
from .forms import TimeSlotForm,TimetableEntryForm



# def daily_timetable_view(request, course_id, semester_number, day):
#     semester = get_object_or_404(Semester, course__id=course_id, number=semester_number)
#     entries = TimetableEntry.objects.filter(semester=semester, day=day).order_by('time_slot')
#     return render(request, 'timetable/daily.html', {
#         'day': day, 'entries': entries, 'semester': semester
#     })
# views.py

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

# def daily_timetable_view(request):
#     semesters = Semester.objects.all()
#     courses = Course.objects.all()
#     course_types = CourseType.objects.all()
#     week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

#     # Get filters from GET parameters
#     semester_id = request.GET.get('semester')
#     course_id = request.GET.get('course')
#     course_type = request.GET.get('course_type')
#     day = request.GET.get('day')

#     filters = {}
#     if semester_id:
#         filters['semester_id'] = semester_id
#     if course_id:
#         filters['subject__course_id'] = course_id
#     if course_type:
#         filters['subject__type'] = course_type
#     if day:
#         filters['day'] = day

#     entries = TimetableEntry.objects.filter(**filters)

#     # Base context
#     context = {
#         'semesters': semesters,
#         'courses': courses,
#         'course_types': course_types,
#         'week_days': week_days,
#         'entries': entries,
#         'selected_semester': Semester.objects.filter(id=semester_id).first() if semester_id else None,
#         'selected_day': day,
#     }

    # Add selected filter values for template use
    context.update({
        'selected_semester_id': semester_id,
        'selected_course_id': course_id,
        'selected_course_type': course_type,
        'selected_day': day,
    })

    return render(request, 'timetable/daily.html', context)

# def daily_timetable_view(request):
#     semesters = Semester.objects.all()
#     courses = Course.objects.all()
#     course_types = CourseType.objects.all()
#     week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

#     # Get filters from GET parameters
#     semester_id = request.GET.get('semester')
#     course_id = request.GET.get('course')
#     course_type = request.GET.get('course_type')
#     day = request.GET.get('day')

#     filters = {}
#     if semester_id:
#         filters['semester_id'] = semester_id
#     if course_id:
#         filters['subject__course_id'] = course_id
#     if course_type:
#         filters['subject__course__course_type__name'] = course_type  # ✅ FIXED HERE
#     if day:
#         filters['day'] = day

#     entries = TimetableEntry.objects.filter(**filters)

#     context = {
#         'semesters': semesters,
#         'courses': courses,
#         'course_types': course_types,
#         'week_days': week_days,
#         'entries': entries,
#         'selected_semester': Semester.objects.filter(id=semester_id).first() if semester_id else None,
#         'selected_day': day,
#         'selected_semester_id': semester_id,
#         'selected_course_id': course_id,
#         'selected_course_type': course_type,
#     }

#     return render(request, 'timetable/daily.html', context)


# def daily_timetable_view(request):
#     semesters = Semester.objects.all()
#     courses = Course.objects.all()
#     course_types = CourseType.objects.all()
#     week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

#     semester_id = request.GET.get('semester')
#     course_id = request.GET.get('course')
#     course_type = request.GET.get('course_type')
#     day = request.GET.get('day')

#     filters = {}
#     if semester_id:
#         filters['semester_id'] = semester_id
#     if course_id:
#         filters['subject__course_id'] = course_id
#     if course_type:
#         filters['subject__course__course_type__name'] = course_type
#     if day:
#         filters['day'] = day

#     entries = TimetableEntry.objects.filter(**filters)

#     context = {
#         'semesters': semesters,
#         'courses': courses,
#         'course_types': course_types,
#         'week_days': week_days,
#         'entries': entries,
#         'selected_semester_id': semester_id,
#         'selected_course_id': course_id,
#         'selected_course_type': course_type,
#         'selected_day': day,
#     }



#     return render(request, 'timetable/daily.html', context)

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

def daily_timetable_view(request):
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    # Default day
    today_day = timezone.now().strftime('%A')
    if today_day in ['Saturday', 'Sunday']:
        today_day = 'Friday'

    # Defaults
    default_course_type = 'PU'
    default_course = Course.objects.filter(name__iexact='SEBA').first()
    default_semester = Semester.objects.filter(number=1).first()

    # Get filters from request
    course_type = request.GET.get('course_type', default_course_type)
    course_id = request.GET.get('course', str(default_course.id) if default_course else '')
    semester_id = request.GET.get('semester', str(default_semester.id) if default_semester else '')
    day = request.GET.get('day', today_day)

    filters = {}
    if semester_id:
        filters['semester_id'] = semester_id
    if course_id:
        filters['subject__course_id'] = course_id
    if course_type:
        filters['subject__course__course_type__name__iexact'] = course_type
    if day:
        filters['day__iexact'] = day

    print("Filters used:", filters)  # ✅ Debugging info

    entries = TimetableEntry.objects.filter(**filters).select_related(
        'faculty', 'subject', 'subject__course', 'semester'
    )

    # Get dropdown data
    course_types = CourseType.objects.all()
    courses = Course.objects.filter(course_type__name__iexact=course_type) if course_type else Course.objects.all()
    
    # Only list semesters that belong to selected course (based on timetable entries)
    semesters = Semester.objects.filter(
        id__in=TimetableEntry.objects.filter(subject__course_id=course_id).values_list('semester_id', flat=True).distinct()
    ) if course_id else Semester.objects.all()

    context = {
        'semesters': semesters,
        'courses': courses,
        'course_types': course_types,
        'week_days': week_days,
        'entries': entries,
        'selected_semester': Semester.objects.filter(id=semester_id).first() if semester_id else None,
        'selected_day': day,
        'selected_semester_id': semester_id,
        'selected_course_id': course_id,
        'selected_course_type': course_type,
    }

    return render(request, 'timetable/daily.html', context)








from django.shortcuts import render, get_object_or_404
from .models import TimetableEntry, TimeSlot
from master.models import Semester, Course, CourseType

def weekly_timetable_view(request, course_id=None, semester_number=None):
    selected_course_type = request.GET.get('course_type')
    selected_course = request.GET.get('course') or course_id
    selected_semester = request.GET.get('semester') or semester_number

    selected_course_type_id = int(selected_course_type) if selected_course_type else None
    selected_course_id = int(selected_course) if selected_course else None
    selected_semester_number = int(selected_semester) if selected_semester else None

    course_types = CourseType.objects.all()
    courses = Course.objects.filter(course_type_id=selected_course_type_id) if selected_course_type_id else Course.objects.none()
    semesters = Semester.objects.filter(course_id=selected_course_id) if selected_course_id else Semester.objects.none()

    semester = Semester.objects.filter(course_id=selected_course_id, number=selected_semester_number).first()

    # Timetable logic
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    timetable = {}
    time_slots = []

    if semester:
        timetable = {
            day: list(TimetableEntry.objects.filter(semester=semester, day=day).order_by('time_slot__start_time'))
            for day in week_days
        }
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



def add_timetable_entry(request):
    if request.method == 'POST':
        form = TimetableEntryForm(request.POST)
        if form.is_valid():
            entry = form.save()
            return redirect('weekly_timetable', course_id=entry.semester.course.id, semester_number=entry.semester.number)
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


def delete_timetable_entry(request, entry_id):
    entry = get_object_or_404(TimetableEntry, id=entry_id)
    course_id = entry.semester.course.id
    semester_number = entry.semester.number
    entry.delete()
    return redirect('weekly_timetable', course_id=course_id, semester_number=semester_number)

def edit_timetable_entry(request, entry_id):
    entry = get_object_or_404(TimetableEntry, id=entry_id)
    if request.method == 'POST':
        form = TimetableEntryForm(request.POST, instance=entry)
        if form.is_valid():
            updated_entry = form.save()
            return redirect('weekly_timetable', course_id=updated_entry.semester.course.id, semester_number=updated_entry.semester.number)
    else:
        form = TimetableEntryForm(instance=entry)
    return render(request, 'timetable/edit_entry.html', {'form': form, 'entry': entry})

from django.shortcuts import render
from django.db.models import Count
from timetable.models import TimetableEntry
from master.models import Course

def faculty_classes_table(request):
    courses = Course.objects.all()

    # Default SEBA course id
    try:
        seba_course = Course.objects.get(name__iexact='SEBA')
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

