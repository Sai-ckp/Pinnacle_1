from django import forms
from django.core.exceptions import ValidationError
import re
from .models import PUAdmission
from multiselectfield import MultiSelectFormField
from master.models import Course, CourseType, Transport

class PUAdmissionForm(forms.ModelForm):
    education_boards = MultiSelectFormField(
        choices=PUAdmission.BOARD_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )
    class Meta:
        model = PUAdmission
        exclude = ['admission_no', 'status', 'final_fee_after_advance']
        fields = '__all__'
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
            'student_declaration_date': forms.DateInput(attrs={'type': 'date'}),
            'parent_declaration_date': forms.DateInput(attrs={'type': 'date'}),
            'blood_group': forms.Select(choices=PUAdmission.BLOOD_GROUP_CHOICES),
            'permanent_address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'current_address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'caste': forms.Select(attrs={'class': 'form-select'}),
            'document_submitted': forms.CheckboxInput(),
            'hostel_required': forms.CheckboxInput(),
            'course': forms.Select(),
            'course_type': forms.Select(),
            'admitted_to': forms.Select(),
            'transport': forms.Select(),
            'parent_phone_no': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['course_type'].queryset = CourseType.objects.all()

        # Filter course based on selected course_type
        if 'course_type' in self.data:
            try:
                course_type_id = int(self.data.get('course_type'))
                self.fields['course'].queryset = Course.objects.filter(course_type_id=course_type_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['course'].queryset = Course.objects.none()
        elif self.instance.pk and self.instance.course_type:
            self.fields['course'].queryset = Course.objects.filter(course_type=self.instance.course_type).order_by('name')
        else:
            self.fields['course'].queryset = Course.objects.none()

        self.fields['transport'].queryset = Transport.objects.all()

        if 'admitted_to' in self.fields:
            self.fields['admitted_to'].queryset = Course.objects.all()

        # Add form-control and capitalize class to selected fields
        fields_to_capitalize = [
            'student_name', 'parent_name', 'religion', 'nationality', 'permanent_address', 'current_address'
        ]
        for field in fields_to_capitalize:
            if field in self.fields:
                self.fields[field].widget.attrs.update({'class': 'form-control capitalize-on-input'})

    def clean_student_name(self):
        name = self.cleaned_data.get('student_name', '')
        if not re.match(r'^[A-Z\s]+$', name):
            raise ValidationError("Name must contain only capital letters and spaces. Numbers and lowercase letters are not allowed.")
        return name

    def clean_education_boards(self):
            data = self.cleaned_data.get('education_boards')
            if len(data) > 1:
                raise forms.ValidationError("Please select only one education board.")
            return data



from master.models import Course
from .models import DegreeAdmission
from django import forms
from multiselectfield import MultiSelectFormField
from django.core.exceptions import ValidationError

class DegreeAdmissionForm(forms.ModelForm):
    education_boards = MultiSelectFormField(
        choices=DegreeAdmission.BOARD_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = DegreeAdmission
        exclude = ['admission_no', 'status', 'final_fee_after_advance']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
            'student_declaration_date': forms.DateInput(attrs={'type': 'date'}),
            'parent_declaration_date': forms.DateInput(attrs={'type': 'date'}),
            'transport': forms.Select(),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'caste': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(),
            'blood_group': forms.Select(),
            'quota_type': forms.Select(),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'permanent_address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'current_address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'co_curricular_activities': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(DegreeAdmissionForm, self).__init__(*args, **kwargs)

        # Apply 'form-control' to all except FileInputs
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.FileInput):
                current_class = field.widget.attrs.get('class', '')
                if 'form-control' not in current_class:
                    field.widget.attrs['class'] = f"{current_class} form-control".strip()

        # Dynamic course filtering based on course_type
        self.fields['course_type'].queryset = CourseType.objects.all()

        if 'course_type' in self.data:
            try:
                course_type_id = int(self.data.get('course_type'))
                self.fields['course'].queryset = Course.objects.filter(course_type_id=course_type_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['course'].queryset = Course.objects.none()
        elif self.instance.pk and self.instance.course_type:
            self.fields['course'].queryset = Course.objects.filter(course_type=self.instance.course_type).order_by('name')
        else:
            self.fields['course'].queryset = Course.objects.none()

        # Add frontend validation for phone fields
        phone_fields = ['parent_phone_no', 'student_phone_no', 'emergency_contact']
        for field_name in phone_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'pattern': r'^[0-9]{10}$',
                    'maxlength': '10',
                    'title': 'Enter a valid 10-digit phone number',
                })

        # Add capitalization to selected fields
        fields_to_capitalize = [
            'student_name', 'parent_name', 'religion', 'nationality', 'permanent_address', 'current_address'
        ]
        for field in fields_to_capitalize:
            if field in self.fields:
                existing_class = self.fields[field].widget.attrs.get('class', '')
                if 'capitalize-on-input' not in existing_class:
                    self.fields[field].widget.attrs['class'] = f"{existing_class} capitalize-on-input".strip()

    # Server-side validation for phone numbers
    def clean_parent_phone_no(self):
        return self._validate_phone_number('parent_phone_no')

    def clean_student_phone_no(self):
        return self._validate_phone_number('student_phone_no')

    def clean_emergency_contact(self):
        return self._validate_phone_number('emergency_contact')

    def _validate_phone_number(self, field_name):
        phone = self.cleaned_data.get(field_name)
        if phone:
            phone_str = str(phone).strip()
            if not phone_str.isdigit() or len(phone_str) != 10:
                raise ValidationError("Please enter a valid 10-digit phone number.")
            return phone_str
        return phone

    def clean_education_boards(self):
            data = self.cleaned_data.get('education_boards')
            if len(data) > 1:
                raise forms.ValidationError("Please select only one education board.")
            return data

from .models import Enquiry1, Course, CourseType
from django.utils import timezone

class Enquiry1Form(forms.ModelForm):
    enquiry_date = forms.DateField(
        label="Enquiry Date",
        initial=timezone.now().date(),
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    class Meta:
        model = Enquiry1

        fields = [
            'enquiry_no', 'student_name', 'gender', 'parent_relation', 'parent_name', 'parent_phone',
            'permanent_address', 'current_address', 'city', 'pincode', 'state',
            'course_type', 'course', 'percentage_10th', 'percentage_12th','guardian_relation',
            'email', 'source', 'other_source','enquiry_date'
        ]
        widgets = {
            'source': forms.Select(attrs={'onchange': 'toggleOtherSource(this)'}),
            'permanent_address': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'current_address': forms.Textarea(attrs={'rows': 2, 'cols': 40}),

            # 'other_source': forms.TextInput(attrs={'id': 'other_source_input', 'style': 'display:none;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['enquiry_no'].widget.attrs['readonly'] = True
        course_type_id = 1
        self.fields['course'].queryset = Course.objects.filter(course_type_id=course_type_id).order_by('name')









from django import forms
from .models import Enquiry2, Course, CourseType
class Enquiry2Form(forms.ModelForm):
    enquiry_date = forms.DateField(
        label="Enquiry Date",
        initial=timezone.now().date(),
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    class Meta:
        model = Enquiry2
        fields = [
            'enquiry_no', 'student_name', 'gender', 'parent_relation', 'parent_name', 'parent_phone',
            'permanent_address', 'current_address', 'city', 'pincode', 'state',
            'course_type', 'course', 'percentage_10th', 'percentage_12th','guardian_relation',
            'email', 'source', 'other_source','enquiry_date'
        ]
        widgets = {
            'source': forms.Select(attrs={'onchange': 'toggleOtherSource(this)'}),

            'permanent_address': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'current_address': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            # 'other_source': forms.TextInput(attrs={'id': 'other_source_input', 'style': 'display:none;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['enquiry_no'].widget.attrs['readonly'] = True
        if 'course_type' in self.data:
            try:
                course_type_id = int(self.data.get('course_type'))
                self.fields['course'].queryset = Course.objects.filter(course_type_id=course_type_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['course'].queryset = Course.objects.none()
        elif self.instance.pk and self.instance.course_type:
            self.fields['course'].queryset = Course.objects.filter(course_type=self.instance.course_type).order_by('name')
        else:
            self.fields['course'].queryset = Course.objects.none()


from django import forms
from .models import FollowUp, Enquiry1, Enquiry2
class FollowUpForm(forms.ModelForm):
    combined_enquiry = forms.ChoiceField(
        label='Enquiry',
        choices=[],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    student_name_display = forms.CharField(
        label='Student Name',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    class Meta:
        model = FollowUp
        exclude = ['status']
        widgets = {
            'follow_up_type': forms.Select(
                choices=[('Call', 'Call'), ('Email', 'Email'), ('Visit', 'Visit')],
                attrs={'class': 'form-control'}
            ),
            'follow_up_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'priority': forms.Select(
                choices=[('', 'Select priority'), ('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')],
                attrs={'class': 'form-control'}
            ),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Add notes about the follow-up',
                'style': 'height: 57px;'
            }),
            'next_action_required': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Send brochure, Schedule campus visit'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Prepare PU and Degree Enquiry choices
        pu_converted_nos = PUAdmission.objects.exclude(enquiry_no__isnull=True).exclude(enquiry_no='').values_list('enquiry_no', flat=True)
        deg_converted_nos = DegreeAdmission.objects.exclude(enquiry_no__isnull=True).exclude(enquiry_no='').values_list('enquiry_no', flat=True)

        pu_enquiries = Enquiry1.objects.exclude(enquiry_no__in=pu_converted_nos)
        deg_enquiries = Enquiry2.objects.exclude(enquiry_no__in=deg_converted_nos)

        pu_choices = [('pu_' + str(e.id), f"{e.enquiry_no}") for e in pu_enquiries]
        deg_choices = [('deg_' + str(e.id), f"{e.enquiry_no}") for e in deg_enquiries]

        self.fields['combined_enquiry'].choices = pu_choices + deg_choices

        # Set initial values if editing
        if self.instance and (self.instance.pu_enquiry or self.instance.degree_enquiry):
            if self.instance.pu_enquiry:
                self.fields['combined_enquiry'].initial = 'pu_' + str(self.instance.pu_enquiry.id)
                self.fields['student_name_display'].initial = f"{self.instance.pu_enquiry.enquiry_no} - {self.instance.pu_enquiry.student_name}"
            elif self.instance.degree_enquiry:
                self.fields['combined_enquiry'].initial = 'deg_' + str(self.instance.degree_enquiry.id)
                self.fields['student_name_display'].initial = f"{self.instance.degree_enquiry.enquiry_no} - {self.instance.degree_enquiry.student_name}"

    def clean(self):
        cleaned_data = super().clean()

        # Extract fields to validate
        combined_value = cleaned_data.get('combined_enquiry')
        follow_up_type = cleaned_data.get('follow_up_type')
        follow_up_date = cleaned_data.get('follow_up_date')
        priority = cleaned_data.get('priority')
        notes = cleaned_data.get('notes')
        next_action_required = cleaned_data.get('next_action_required')

        # Manual required field checks
        missing_fields = []
        if not combined_value:
            missing_fields.append("Enquiry")
        if not follow_up_type:
            missing_fields.append("Follow-up Type")
        if not follow_up_date:
            missing_fields.append("Follow-up Date")
        if not priority:
            missing_fields.append("Priority")
        if not notes:
            missing_fields.append("Notes")
        if not next_action_required:
            missing_fields.append("Next Action Required")

        if missing_fields:
            raise forms.ValidationError(f"The following fields are required: {', '.join(missing_fields)}")

        # Extract enquiry info if provided
        if combined_value:
            prefix, obj_id = combined_value.split('_', 1)
            cleaned_data['enquiry_type'] = prefix
            cleaned_data['enquiry_id'] = int(obj_id)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        enquiry_type = self.cleaned_data.get('enquiry_type')
        enquiry_id = self.cleaned_data.get('enquiry_id')

        # Set appropriate foreign key
        if enquiry_type == 'pu':
            instance.pu_enquiry = Enquiry1.objects.get(id=enquiry_id)
            instance.degree_enquiry = None
        elif enquiry_type == 'deg':
            instance.degree_enquiry = Enquiry2.objects.get(id=enquiry_id)
            instance.pu_enquiry = None

        if commit:
            instance.save()
        return instance


from django import forms
from .models import PUFeeDetail, DegreeFeeDetail

class PUFeeDetailForm(forms.ModelForm):
    class Meta:
        model = PUFeeDetail
        fields = [
            'tuition_fee',
            'scholarship',
            'tuition_advance_amount',
            'transport_fee',
            'hostel_fee',
            'books_fee',
            'uniform_fee',
            'payment_mode',
            'final_fee_after_advance',
        ]


    def clean(self):
        cleaned_data = super().clean()
        hostel_fee = cleaned_data.get('hostel_fee') or 0
        transport_fee = cleaned_data.get('transport_fee') or 0

        if hostel_fee > 0:
            cleaned_data['transport_fee'] = 0
        elif transport_fee > 0:
            cleaned_data['hostel_fee'] = 0

        return cleaned_data

class DegreeFeeDetailForm(forms.ModelForm):
    class Meta:
        model = DegreeFeeDetail
        fields = [
            'tuition_fee',
            'scholarship',
            'tuition_advance_amount',
            'transport_fee',
            'hostel_fee',
            'books_fee',
            'uniform_fee',
            'payment_mode',
            'final_fee_after_advance',

        ]

    def clean(self):
        cleaned_data = super().clean()
        hostel_fee = cleaned_data.get('hostel_fee') or 0
        transport_fee = cleaned_data.get('transport_fee') or 0

        # Enforce: if hostel_fee is entered, transport_fee = 0 and vice versa
        if hostel_fee > 0:
            cleaned_data['transport_fee'] = 0
        elif transport_fee > 0:
            cleaned_data['hostel_fee'] = 0

        return cleaned_data


from django import forms
from .models import StudentLogin

class StudentLoginForm(forms.ModelForm):
    class Meta:
        model = StudentLogin
        fields = ['admission_no', 'password']  # user enters only these



from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        widgets = {
            'next_due_date': forms.DateInput(attrs={'type': 'date'}),
            'tuition_due_date': forms.DateInput(attrs={'type': 'date'}),
            'transport_due_date': forms.DateInput(attrs={'type': 'date'}),
            'hostel_due_date': forms.DateInput(attrs={'type': 'date'}),
            'books_due_date': forms.DateInput(attrs={'type': 'date'}),
            'uniform_due_date': forms.DateInput(attrs={'type': 'date'}),
            'other_due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        if not self.instance.pk:
            self.fields['branch_code'].initial = 'PSCM/001/AY/2025-26'



from django import forms
from .models import ConfirmedAdmission

class ConfirmedAdmissionForm(forms.ModelForm):
    class Meta:
        model = ConfirmedAdmission
        fields = [
            'admission_no',
            'student_name',
            'course',
            'admission_date',
            'documents_complete',
            'admission_type',
            'status',
            'student_userid',
            'student_password',
        ]