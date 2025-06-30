from django import forms
from .models import PUAdmission

from django import forms
from .models import PUAdmission, Transport, Course, CourseType

from django import forms
from django.core.exceptions import ValidationError
from .models import PUAdmission
from master.models import Course, CourseType, Transport
import re

class PUAdmissionForm(forms.ModelForm):
    class Meta:
        model = PUAdmission
        exclude = ['admission_no', 'status']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
            'student_declaration_date': forms.DateInput(attrs={'type': 'date'}),
            'parent_declaration_date': forms.DateInput(attrs={'type': 'date'}),
            'blood_group': forms.Select(choices=PUAdmission.BLOOD_GROUP_CHOICES),
            'category': forms.Select(choices=PUAdmission.CATEGORY_CHOICES, attrs={'class': 'form-control'}),
            'permanent_address': forms.Textarea(attrs={'rows': 2}),
            'current_address': forms.Textarea(attrs={'rows': 2}),
            'document_submitted': forms.CheckboxInput(),
            'hostel_required': forms.CheckboxInput(),
            'course': forms.Select(),
            'course_type': forms.Select(),
            'admitted_to': forms.Select(),
            'transport': forms.Select(),
            'parent_phone_no': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(PUAdmissionForm, self).__init__(*args, **kwargs)

        # Populate dropdowns dynamically
        self.fields['transport'].queryset = Transport.objects.all()
        self.fields['course'].queryset = Course.objects.all()
        self.fields['course_type'].queryset = CourseType.objects.all()
        if 'admitted_to' in self.fields:
            self.fields['admitted_to'].queryset = Course.objects.all()

        # Capitalize specific fields
        fields_to_capitalize = [
            'student_name', 'parent_name', 'religion', 'nationality', 'permanent_address', 'current_address'
        ]
        for field in fields_to_capitalize:
            self.fields[field].widget.attrs.update({'class': 'form-control capitalize-on-input'})

    def clean_sats_number(self):
        sats = self.cleaned_data.get("sats_number")
        if sats:
            if not re.fullmatch(r"\d{9}", str(sats)):
                raise ValidationError("SATS number must be a 9-digit number.")
        return sats




from master.models import Course
from django import forms
from .models import DegreeAdmission

from django import forms
from django.core.exceptions import ValidationError
from .models import DegreeAdmission

class DegreeAdmissionForm(forms.ModelForm):
    class Meta:
        model = DegreeAdmission
        exclude = ['admission_no']
        exclude = ['status'] 
        fields = '__all__'
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
            'student_declaration_date': forms.DateInput(attrs={'type': 'date'}),
            'parent_declaration_date': forms.DateInput(attrs={'type': 'date'}),
            'transport': forms.Select(),
            'category': forms.Select(),
            'gender': forms.Select(),
            'blood_group': forms.Select(),
            'quota_type': forms.Select(),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'permanent_address': forms.Textarea(attrs={'rows': 2}),
            'current_address': forms.Textarea(attrs={'rows': 2}),
            'co_curricular_activities': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super(DegreeAdmissionForm, self).__init__(*args, **kwargs)

        # Apply 'form-control' to all except FileInputs
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.FileInput):
                current_class = field.widget.attrs.get('class', '')
                if 'form-control' not in current_class:
                    field.widget.attrs['class'] = f"{current_class} form-control".strip()

        # Add frontend validation for phone fields
        phone_fields = ['parent_phone_no', 'student_phone_no', 'emergency_contact']
        for field_name in phone_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'pattern': r'^[0-9]{10}$',
                    'maxlength': '10',
                    'title': 'Enter a valid 10-digit phone number',
                })

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

    class Meta:
        model = DegreeAdmission
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DegreeAdmissionForm, self).__init__(*args, **kwargs)

        # Fields where first letter capitalization is required
        fields_to_capitalize = [
            'student_name', 'parent_name', 'religion', 'nationality', 'permanent_address','current_address'
        ]
        for field in fields_to_capitalize:
            if field in self.fields:
                self.fields[field].widget.attrs.update({'class': 'form-control capitalize-on-input'})

    class Meta:
        model = DegreeAdmission
        exclude = ['admission_no', 'status']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
            'student_declaration_date': forms.DateInput(attrs={'type': 'date'}),
            'parent_declaration_date': forms.DateInput(attrs={'type': 'date'}),
            
        }

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
    combined_enquiry = forms.ChoiceField(label='Enquiry', choices=[], required=True,widget=forms.Select(attrs={'class': 'form-control'}) )
    class Meta:
        model = FollowUp
        exclude = ['status']
        widgets = {
            # 'enquiry': forms.Select(attrs={'class': 'form-control'}),
            'combined_enquiry': forms.Select(attrs={'class': 'form-control'}),
            'follow_up_type': forms.Select(choices=[('Call', 'Call'), ('Email', 'Email'), ('Visit', 'Visit')], attrs={'class': 'form-control'}),
            'follow_up_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'priority': forms.Select(choices=[('', 'Select priority'), ('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')], attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Add notes about the follow-up','style': 'height: 57px;'}),
            'next_action_required': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Send brochure, Schedule campus visit'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Prepare choices for PU Enquiry (prefix 'pu_')
        pu_choices = [('pu_' + str(e.id), f"PU: {e.student_name}") for e in Enquiry1.objects.all()]
        
        # Prepare choices for Degree Enquiry (prefix 'deg_')
        deg_choices = [('deg_' + str(e.id), f"Degree: {e.student_name}") for e in Enquiry2.objects.all()]

        # Combine both choices
        self.fields['combined_enquiry'].choices = pu_choices + deg_choices

        # If instance exists, pre-select the combined enquiry
        if self.instance and (self.instance.pu_enquiry or self.instance.degree_enquiry):
            if self.instance.pu_enquiry:
                self.fields['combined_enquiry'].initial = 'pu_' + str(self.instance.pu_enquiry.id)
            elif self.instance.degree_enquiry:
                self.fields['combined_enquiry'].initial = 'deg_' + str(self.instance.degree_enquiry.id)

    def clean(self):
        cleaned_data = super().clean()
        combined_value = cleaned_data.get('combined_enquiry')

        if combined_value:
            prefix, obj_id = combined_value.split('_', 1)
            cleaned_data['enquiry_type'] = prefix
            cleaned_data['enquiry_id'] = int(obj_id)
        else:
            raise forms.ValidationError("Please select an enquiry.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        enquiry_type = self.cleaned_data.get('enquiry_type')
        enquiry_id = self.cleaned_data.get('enquiry_id')

        # Set the correct foreign key and clear the other
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
from .models import PUFeeDetail,DegreeFeeDetail

from django import forms
from .models import PUFeeDetail

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

        ]




# forms.py

from django import forms
from .models import DegreeFeeDetail

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

        ]


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
        fields = '__all__'  # or list specific fields you want

        widgets = {
            'next_due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: Add Bootstrap classes
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


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
