from django import forms
from .models import Assignment 
from master.models import Course, Subject, CourseType, Employee
from timetable.models import TimeSlot

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        exclude = ['program_type', 'academic_year', 'course', 'semester_number', 'subject']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        faculty_queryset = kwargs.pop('faculty_queryset', None)
        super().__init__(*args, **kwargs)

        self.fields['time_slot'].queryset = TimeSlot.objects.all()

        if faculty_queryset is not None:
            self.fields['faculty'].queryset = Employee.objects.filter(id__in=[emp.id for emp in faculty_queryset])
        else:
            self.fields['faculty'].queryset = Employee.objects.none()


#lib
from django import forms
from .models import Book
from master.models import BookCategory
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'authors', 'category', 'publication_date',
            'edition', 'available_copies', 'summary', 'publisher',
            'isbn', 'tags', 'cover_image', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'authors': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'publication_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'edition': forms.TextInput(attrs={'class': 'form-control'}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.RadioSelect(choices=Book.STATUS_CHOICES),
        }

from django import forms

from .models import BorrowRecord, Book

from master.models import StudentDatabase
 
class BorrowRecordForm(forms.ModelForm):

    class Meta:

        model = BorrowRecord

        fields = ['book', 'student', 'return_due_date']

        widgets = {

            'return_due_date': forms.DateInput(attrs={'type': 'date'}),

        }
 
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
 
        # Set default book queryset

        self.fields['book'].queryset = Book.objects.filter(

            available_copies__gt=0,

            status='active'

        )
 
        # Set default student queryset

        self.fields['student'].queryset = StudentDatabase.objects.filter(status='Active')
 
        if 'book' in self.data:

            try:

                book_id = int(self.data.get('book'))
 
                # Get all students who have borrowed this book and not returned

                borrowed_students = BorrowRecord.objects.filter(

                    book_id=book_id,

                    returned=False

                ).values_list('student_id', flat=True)
 
                selected_student_id = self.data.get('student')
 
                if selected_student_id:

                    try:

                        selected_student_id = int(selected_student_id)
 
                        # Get the base filtered queryset

                        base_qs = StudentDatabase.objects.filter(

                            status='Active'

                        ).exclude(id__in=borrowed_students)
 
                        # Manually include selected student if they are already in the borrowed list

                        if selected_student_id in borrowed_students:

                            selected_student = StudentDatabase.objects.filter(id=selected_student_id).first()
 
                            # Combine manually

                            combined_students = list(base_qs)

                            if selected_student:

                                combined_students.append(selected_student)
 
                            self.fields['student'].queryset = StudentDatabase.objects.filter(id__in=[s.id for s in combined_students])

                        else:

                            self.fields['student'].queryset = base_qs
 
                    except ValueError:

                        pass

                else:

                    self.fields['student'].queryset = StudentDatabase.objects.filter(

                        status='Active'

                    ).exclude(id__in=borrowed_students)
 
            except (ValueError, TypeError):

                pass
 
# forms.py
from django import forms
from .models import EmployeeStudyMaterial ,Exam
from master.models import Employee
from timetable.models import TimeSlot

class EmployeeStudyMaterialForm(forms.ModelForm):
    class Meta:
        model = EmployeeStudyMaterial
        exclude = ['program_type', 'academic_year', 'course', 'semester_number', 'subject']
        widgets = {
            'material_type': forms.Select(attrs={'onchange': 'toggleAttachmentField();'}),
        }

    def __init__(self, *args, **kwargs):
        faculty_queryset = kwargs.pop('faculty_queryset', None)
        super().__init__(*args, **kwargs)

        if faculty_queryset is not None:
            self.fields['faculty'].queryset = faculty_queryset
        else:
            self.fields['faculty'].queryset = Employee.objects.none()


#This is exam
from django import forms
from .models import Exam
from master.models import Employee ,ExamType

# class ExamForm(forms.ModelForm):
#     class Meta:
#         model = Exam
#         exclude = ['program_type', 'academic_year', 'course', 'semester_number', 'subject', 'created_at']
#         widgets = {
#             'exam_date': forms.DateInput(attrs={'type': 'date'}),
#             # 'duration': forms.TextInput(attrs={'placeholder': 'hh:mm:ss'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['faculty'].queryset = Employee.objects.all()


# forms.py

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        exclude = ['program_type', 'academic_year', 'course', 'semester_number', 'subject', 'created_at']
        widgets = {
            'exam_date': forms.DateInput(attrs={'type': 'date'}),
            'duration_minutes': forms.NumberInput(attrs={'placeholder': 'Duration (minutes)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['faculty'].queryset = Employee.objects.all()
        self.fields['exam_type'].queryset = ExamType.objects.filter(is_active=True)

        #ke
from django import forms
from .models import AssignmentSubmission

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['submitted_file']
        widgets = {
            'submitted_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can ensure class is applied here too (redundant with widget but safe)
        self.fields['submitted_file'].widget.attrs.update({
            'class': 'form-control'
        })


# forms.py
from django import forms
from lms.models import CalendarEvent
from datetime import datetime, date, time
from django.core.exceptions import ValidationError

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
from lms.models import CalendarEvent, NewEvent

class CalendarEventForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ['title', 'description', 'event_type', 'date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Only include active event types
        self.fields['event_type'].queryset = NewEvent.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        event_date = cleaned_data.get('date')
        event_time = cleaned_data.get('time')

        if event_date and event_time:
            now = timezone.now()
            try:
                event_datetime = timezone.make_aware(datetime.combine(event_date, event_time))
            except Exception:
                event_datetime = datetime.combine(event_date, event_time)

            if event_datetime < now:
                raise ValidationError("The event date and time must be in the future.")


