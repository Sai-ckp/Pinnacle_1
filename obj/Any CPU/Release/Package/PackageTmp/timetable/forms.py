
from django import forms
from .models import  TimeSlot, TimetableEntry

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['start_time', 'end_time']


# class TimetableEntryForm(forms.ModelForm):
#     class Meta:
#         model = TimetableEntry
#         fields = ['day', 'time_slot', 'semester', 'subject', 'faculty', 'room']


from django import forms
from .models import TimetableEntry
from master.models import Employee

class TimetableEntryForm(forms.ModelForm):
    semester_number = forms.ChoiceField(
        choices=[('', 'Select Course First')],
        required=True,
        label="Semester",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_semester_number'})
    )

    class Meta:
        model = TimetableEntry
        fields = ['day', 'time_slot', 'course', 'semester_number', 'subject', 'faculty', 'room']
        widgets = {
            'day': forms.Select(attrs={'class': 'form-select'}),
            'time_slot': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select', 'id': 'id_course'}),
            'subject': forms.Select(attrs={'class': 'form-select', 'id': 'id_subject'}),
            'faculty': forms.Select(attrs={'class': 'form-select', 'id': 'id_faculty'}),
            'room': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'day': 'Day',
            'time_slot': 'Time Slot',
            'course': 'Course',
            'semester_number': 'Semester',
            'subject': 'Subject',
            'faculty': 'Faculty',
            'room': 'Room',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initially empty faculty list
        self.fields['faculty'].queryset = Employee.objects.all()

        if 'course' in self.data and 'semester_number' in self.data and 'subject' in self.data:
            try:
                course_id = int(self.data.get('course'))
                semester_number = int(self.data.get('semester_number'))
                subject_id = int(self.data.get('subject'))

                # Filter based on assignment model
                assigned_employees = Employee.objects.filter(
                    subject_assignments__course_id=course_id,
                    subject_assignments__semester=semester_number,
                    subject_assignments__subject_id=subject_id
                ).distinct()

                self.fields['faculty'].queryset = assigned_employees

                # Optionally auto-select the first employee
                if assigned_employees.exists():
                    self.initial['faculty'] = assigned_employees.first().id

            except (ValueError, TypeError):
                pass  # invalid input, ignore

        elif self.instance.pk:
            # If editing an instance, prefill the faculty
            self.fields['faculty'].queryset = Employee.objects.filter(
                subject_assignments__course=self.instance.course,
                subject_assignments__semester=self.instance.semester_number,
                subject_assignments__subject=self.instance.subject
            ).distinct()

 