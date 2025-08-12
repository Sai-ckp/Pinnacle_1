from django import forms
from .models import Employee, ExcelUpload

class ExcelUploadForm(forms.ModelForm):
    class Meta:
        model = ExcelUpload
        fields = ['file']

from django import forms
from .models import Employee

from .models import Employee



from .models import Employee,CourseType

from .models import Employee, Subject

from django import forms
from .models import Employee, EmployeeSubjectAssignment, Subject
from django.forms import inlineformset_factory


from django import forms
from django.core.exceptions import ValidationError
from .models import Employee

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, readonly=False, **kwargs):
        super().__init__(*args, **kwargs)

        # Always make emp_code readonly
        self.fields['emp_code'].widget.attrs.update({
            'readonly': 'readonly',
            'class': 'form-control'
        })

        if readonly:
            for field_name, field in self.fields.items():
                field.widget.attrs.update({
                    'readonly': 'readonly',
                    'disabled': 'disabled',
                    'class': 'form-control'
                })



    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')
        emp_code = cleaned_data.get('emp_code')
        instance_id = self.instance.id if self.instance else None

        if email and Employee.objects.exclude(id=instance_id).filter(email=email).exists():
            self.add_error('email', "Email must be unique.")

        # 🔴 REMOVE this block (phone uniqueness check)
        # if phone and Employee.objects.exclude(id=instance_id).filter(phone=phone).exists():
        #     self.add_error('phone', "Contact Number must be unique.")

        if emp_code and Employee.objects.exclude(id=instance_id).filter(emp_code=emp_code).exists():
            self.add_error('emp_code', "Employee Code must be unique.")

        category = cleaned_data.get("category")
        designation = cleaned_data.get("designation")

        if category == "Teaching Staff" and not designation:
            self.add_error('designation', "Designation is required for Teaching Staff.")

        if category == "Non-Teaching Staff":
            cleaned_data["designation"] = None

        return cleaned_data


class EmployeeSubjectAssignmentForm(forms.ModelForm):
    class Meta:
        model = EmployeeSubjectAssignment
        fields = ['course', 'semester', 'subject']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
        }

EmployeeSubjectAssignmentFormSet = inlineformset_factory(
    Employee,
    EmployeeSubjectAssignment,
    form=EmployeeSubjectAssignmentForm,
    extra=1,
    can_delete=True
)



from django import forms
from .models import Subject, Semester, Course, CourseType
from master.models import Course as MasterCourse, Employee
from .models import Subject, Course, AcademicYear

# ---------- Subject Form ----------
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'subject_code', 'credit', 'course', 'semester', 'is_active', 'academic_year']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'subject_code': forms.TextInput(attrs={'class': 'form-control'}),
            'credit': forms.NumberInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-select', 'id': 'id_course'}),
            'semester': forms.Select(attrs={'class': 'form-select', 'id': 'id_semester'}),  # ✅ Changed
            'is_active': forms.RadioSelect(choices=[(True, 'Active'), (False, 'Inactive')]),
            'academic_year': forms.Select(attrs={'class': 'form-select'}),

        }

   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter active courses
        self.fields['course'].queryset = Course.objects.filter(is_active=True)

        # Set academic year queryset (only active, newest first)
        self.fields['academic_year'].queryset = AcademicYear.objects.filter(is_active=True).order_by('-year')

        # Disable semester dropdown until course is selected (optional UI choice)
        self.fields['semester'].choices = []

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        semester = cleaned_data.get('semester')

        if name and semester:
            name = name.strip()
            qs = Subject.objects.filter(name__iexact=name, semester=semester)

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                self.add_error('name', f"This subject name already exists for Semester {semester}.")

        return cleaned_data







# ---------- Semester Form ----------
class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Only show active courses
        self.fields['course'].queryset = MasterCourse.objects.filter(is_active=True)


from .models import Course, AcademicYear
# ---------- Course Form ----------
from django import forms
from .models import Course, AcademicYear
from django.core.exceptions import ValidationError
 
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'course_type', 'duration_years', 'total_semesters', 'academic_year']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'course_type': forms.Select(attrs={'class': 'form-control'}),
            'duration_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_semesters': forms.NumberInput(attrs={'class': 'form-control'}),
            'academic_year': forms.Select(attrs={'class': 'form-control'}),
        }
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
 
        if 'academic_year' in self.fields:
            self.fields['academic_year'].queryset = AcademicYear.objects.filter(is_active=True).order_by('-year')
 
 
    def clean(self):
        cleaned_data = super().clean()
        course_type = cleaned_data.get('course_type')
        duration_years = cleaned_data.get('duration_years')
        academic_year = cleaned_data.get('academic_year')
 
        if course_type and duration_years and academic_year:
            try:
                year_parts = academic_year.year.split('-')
                if len(year_parts) == 2:
                    start_year = int(year_parts[0])
                    end_suffix = year_parts[1]
                    if len(end_suffix) == 2:
                        end_year = int(str(start_year)[:2] + end_suffix)
                    else:
                        end_year = int(end_suffix)
                    academic_duration = end_year - start_year
                else:
                    self.add_error('academic_year', "Format must be like '2024-25'.")
                    return
            except Exception:
                self.add_error('academic_year', "Invalid academic year format.")
                return
 
            course_type_name = course_type.name.lower()
 
            if "pu" in course_type_name or "puc" in course_type_name:
                if duration_years != 2:
                    self.add_error('duration_years', "PU-related course types must have a duration of 2 years.")
                if academic_duration != 2:
                    self.add_error('academic_year', "PU course batch must span 2 academic years.")
            elif "degree" in course_type_name or "ug" in course_type_name or "commerce" in course_type_name:
                if duration_years != 3:
                    self.add_error('duration_years', "Degree-related course types must have a duration of 3 years.")
                if academic_duration != 3:
                    self.add_error('academic_year', "Degree course batch must span 3 academic years.")


class CourseTypeForm(forms.ModelForm):
    class Meta:
        model = CourseType
        fields = ['name','academic_year']

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if CourseType.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("This Program Type already exists.")
        return name


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
from master.models import StudentDatabase, CourseType, PUAdmission, DegreeAdmission  # Ensure all are imported

STATUS_CHOICES = [
    ('Active', 'Active'),
    ('Graduated', 'Graduated'),
    ('Dropped', 'Dropped'),
    ('Transferred', 'Transferred'),
    ('Suspended', 'Suspended'),
    ('Inactive', 'Inactive'),
]

class StudentDatabaseForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Status'
    )

    class Meta:
        model = StudentDatabase
        fields = [
            'pu_admission',
            'degree_admission',
            'student_name',
            'course',
            'course_type',
            'quota_type',
            'status',
            'student_userid',
            'student_phone_no',
            'father_name',
        ]
        widgets = {
            'pu_admission': forms.Select(attrs={'class': 'form-control'}),
            'degree_admission': forms.Select(attrs={'class': 'form-control'}),
            'student_name': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}), 
            'course_type': forms.Select(attrs={'class': 'form-control'}),
            'quota_type': forms.TextInput(attrs={'class': 'form-control'}),
            'student_userid': forms.TextInput(attrs={'class': 'form-control'}),
            'student_phone_no': forms.TextInput(attrs={'class': 'form-control'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'pu_admission': 'PU Admission',
            'degree_admission': 'Degree Admission',
            'student_name': 'Student Name',
            'course': 'Course',
            'course_type': 'Course Type',
            'quota_type': 'Quota Type',
            'student_userid': 'Student User ID',
            'student_phone_no': 'Student Phone Number',
            'father_name': 'Father Name',
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



# from django import forms
# from .models import AcademicEvent
# from datetime import datetime, date, time
# from django.core.exceptions import ValidationError

# class AcademicEventForm(forms.ModelForm):
#     class Meta:
#         model = AcademicEvent
#         fields = ['title', 'description', 'event_type', 'date', 'time']
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date'}),
#             'time': forms.TimeInput(attrs={'type': 'time'}),
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         event_date = cleaned_data.get('date')
#         event_time = cleaned_data.get('time')

#         if event_date and event_time:
#             now = datetime.now()

#             # Combine selected date and time to one datetime
#             event_datetime = datetime.combine(event_date, event_time)

#             if event_datetime < now:
#                 raise ValidationError("The event date and time must be in the future.")


from django import forms
from .models import AcademicYear

class AcademicYearForm(forms.ModelForm):
    class Meta:
        model = AcademicYear
        fields = ['year', 'is_active']


    def clean_is_active(self):
        value = self.data.get('is_active')
        return value == '1'  # Returns True if '1', False otherwise
 
 


        #Fee Master
from django import forms
from django import forms
from .models import FeeMaster, Course, CourseType, AcademicYear  # ✅ add AcademicYear

class FeeMasterForm(forms.ModelForm):
    class Meta:
        model = FeeMaster
        fields = '__all__'
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Order program_type by name for clean dropdown
        self.fields['program_type'].queryset = CourseType.objects.all().order_by('name')

        # Handle dependent filtering of 'combination' on 'program_type'
        self.fields['combination'].queryset = Course.objects.none()

        if 'program_type' in self.data:
            try:
                program_type_id = int(self.data.get('program_type'))
                self.fields['combination'].queryset = Course.objects.filter(
                    course_type_id=program_type_id
                ).order_by('name')
            except (ValueError, TypeError):
                pass  # Ignore if invalid input
        elif self.instance.pk:
            self.fields['combination'].queryset = Course.objects.filter(
                course_type=self.instance.program_type
            )

        # ✅ Ensure academic_year is ordered cleanly
        self.fields['academic_year'].queryset = AcademicYear.objects.all().order_by('-year')




from django import forms
from .models import PromotionHistory

class PromotionHistoryForm(forms.ModelForm):
    promotion_cycle = forms.ChoiceField(
        choices=[],  # initially empty, will populate in __init__
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = PromotionHistory
        fields = '__all__'
        widgets = {
            'admission_no': forms.TextInput(attrs={'class': 'form-control'}),
            'student_userid': forms.TextInput(attrs={'class': 'form-control'}),
            'student_name': forms.TextInput(attrs={'class': 'form-control'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
            'from_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'to_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'from_semester': forms.NumberInput(attrs={'class': 'form-control'}),
            'to_semester': forms.NumberInput(attrs={'class': 'form-control'}),
            'promotion_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.promotion_date:
            self.fields['promotion_date'].initial = self.instance.promotion_date.strftime('%Y-%m-%d')

        # Get academic_year from initial, data, or instance
        academic_year_raw = (
            self.initial.get("academic_year") or
            self.data.get("academic_year") or
            (self.instance.academic_year if self.instance else None)
        )

        # Normalize and expand the academic year (e.g., 2025-28 → 2025-2028)
        academic_year_str = None
        if academic_year_raw and "-" in academic_year_raw:
            start_part, end_part = academic_year_raw.split("-")

            try:
                start_year = int(start_part.strip())
                # Expand end year if shortened (e.g., "28" → 2028)
                if len(end_part.strip()) == 2:
                    end_year = int(str(start_year)[:2] + end_part.strip())
                else:
                    end_year = int(end_part.strip())

                academic_year_str = f"{start_year}-{end_year}"

                choices = [
                    (f"{year}-{year+1}", f"{year}-{year+1}")
                    for year in range(start_year, end_year)
                ]
                self.fields['promotion_cycle'].choices = choices
            except ValueError:
                pass

        # Add current value if not already in choices
        if self.instance and self.instance.promotion_cycle:
            current_value = self.instance.promotion_cycle
            if current_value not in dict(self.fields['promotion_cycle'].choices):
                self.fields['promotion_cycle'].choices += [(current_value, current_value)]



 
from django import forms
from .models import FeeType

class FeeTypeForm(forms.ModelForm):
    class Meta:
        model = FeeType
        fields = ['name', 'is_optional', 'is_deductible']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'border-radius: 5px;',
                # 'placeholder': 'Enter Fee Type Name'
            }),
            'is_optional': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_deductible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

