from django import forms
from .models import Employee, ExcelUpload

class ExcelUploadForm(forms.ModelForm):
    class Meta:
        model = ExcelUpload
        fields = ['file']

from django import forms
from .models import Employee

from .models import Employee


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'courses_taught': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'emp_code': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.fields['emp_code'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        designation = cleaned_data.get("designation")

        if category == "Teaching Staff" and not designation:
            raise forms.ValidationError("Designation is required for Teaching Staff.")

        if category == "Non-Teaching Staff" and designation:
            cleaned_data["designation"] = None  # Clear it out

        return cleaned_data


from django import forms
from .models import Subject, Semester, Course, CourseType
from master.models import Course as MasterCourse, Employee


# ---------- Subject Form ----------
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = [
            'name',
            'subject_code',
            'credit',
            'course',
            'semester_number',
            'faculty',
            'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'subject_code': forms.TextInput(attrs={'class': 'form-control'}),
            'credit': forms.NumberInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'semester_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.RadioSelect(choices=[
                (True, 'Active'),
                (False, 'Inactive')
            ]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Show only active courses
        self.fields['course'].queryset = MasterCourse.objects.filter(is_active=True)
        # ✅ Optionally filter only faculty roles
        self.fields['faculty'].queryset = Employee.objects.filter(role="Faculty")


# ---------- Semester Form ----------
class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Only show active courses
        self.fields['course'].queryset = MasterCourse.objects.filter(is_active=True)


# ---------- Course Form ----------
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'course_type', 'duration_years', 'total_semesters']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'course_type': forms.Select(attrs={'class': 'form-control'}),
            'duration_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_semesters': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class CourseTypeForm(forms.ModelForm):
    class Meta:
        model = CourseType
        fields = ['name']

from .models import Transport

class TransportForm(forms.ModelForm):
    class Meta:
        model = Transport
        fields = [
            'route_name',         # <-- NEW FIELD
            'route',
            'bus_no',
            'driver_name',
            'driver_contact_no'
        ]
        widgets = {
            'route_name': forms.TextInput(attrs={'class': 'form-control'}),
            'route': forms.TextInput(attrs={'class': 'form-control'}),
            'bus_no': forms.TextInput(attrs={'class': 'form-control'}),
            'driver_name': forms.TextInput(attrs={'class': 'form-control'}),
            'driver_contact_no': forms.TextInput(attrs={'class': 'form-control'}),
        }



from django import forms
from .models import StudentDatabase

from django import forms
from master.models import StudentDatabase, CourseType  # Ensure CourseType is imported

class StudentDatabaseForm(forms.ModelForm):
    """
    Form for StudentDatabase, including CourseType as a dropdown (ForeignKey).
    """
    class Meta:
        model = StudentDatabase
        fields = [
            'admission_no',
            'student_name',
            'course',
            'course_type',
            'quota_type',
            'status',
            'student_userid',
            'student_phone_no',
            'parent_name',
        ]
        widgets = {
            'admission_no': forms.TextInput(attrs={'class': 'form-control'}),
            'student_name': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.TextInput(attrs={'class': 'form-control'}),
            'course_type': forms.Select(attrs={'class': 'form-control'}),  # ✅ Correct widget
            'quota_type': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.TextInput(attrs={'class': 'form-control'}),
            'student_userid': forms.TextInput(attrs={'class': 'form-control'}),
            'student_phone_no': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'admission_no': 'Admission Number',
            'student_name': 'Student Name',
            'course': 'Course',
            'course_type': 'Course Type',
            'quota_type': 'Quota Type',
            'status': 'Status',
            'student_userid': 'Student User ID',
            'student_phone_no': 'Student Phone Number',
            'parent_name': 'Parent Name',
        }


# forms.py
from django import forms
from .models import AcademicEvent
from datetime import datetime, date, time
from django.core.exceptions import ValidationError

class AcademicEventForm(forms.ModelForm):
    class Meta:
        model = AcademicEvent
        fields = ['title', 'description', 'event_type', 'date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        event_date = cleaned_data.get('date')
        event_time = cleaned_data.get('time')

        if event_date and event_time:
            now = datetime.now()

            # Combine selected date and time to one datetime
            event_datetime = datetime.combine(event_date, event_time)

            if event_datetime < now:
                raise ValidationError("The event date and time must be in the future.")


