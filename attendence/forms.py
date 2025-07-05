# forms.py
from django import forms



from django import forms
from .models import attendance, Employee
from django.core.exceptions import ValidationError
from datetime import date


class AttendanceForm(forms.ModelForm):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.Select(attrs={'onchange': 'fetchDepartmentAndCode()'}))
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), initial=date.today)
    check_in = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    check_out = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=False)

    class Meta:
        model = attendance
        fields = ['employee', 'date', 'check_in', 'check_out']

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        selected_date = cleaned_data.get('date')

        if employee and selected_date:
            qs = attendance.objects.filter(employee=employee, date=selected_date)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                self.add_error(None, f"Attendance for {employee.name} has already been recorded on {selected_date}.")
        return cleaned_data





from django import forms
from .models import attendancesettings

class AttendanceSettingsForm(forms.ModelForm):
    class Meta:
        model = attendancesettings
        fields = ['check_in_time', 'grace_period', 'late_threshold']
        widgets = {
            'check_in_time': forms.TimeInput(attrs={'type': 'time'}),
        }


from django import forms
from .models import StudentAttendance

class StudentAttendanceForm(forms.ModelForm):
    class Meta:
        model = StudentAttendance
        fields = [
            'course',
            'subject',
            'attendance_date',
            'faculty_name',
            'student_name',
            'admission_no',
            'student_userid',
            'status',
            'remarks',
            'overall_attendance'
        ]

        widgets = {
            'attendance_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'course': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'faculty_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_name': forms.TextInput(attrs={'class': 'form-control'}),
            'admission_no': forms.TextInput(attrs={'class': 'form-control'}),
            'student_userid': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.RadioSelect(choices=StudentAttendance.STATUS_CHOICES),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'overall_attendance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }

    def __init__(self, *args, **kwargs):
        super(StudentAttendanceForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False  # Make all fields optional
