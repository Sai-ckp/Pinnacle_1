
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


class TimetableEntryForm(forms.ModelForm):
    class Meta:
        model = TimetableEntry
        fields = ['day', 'time_slot', 'semester', 'subject', 'faculty', 'room']
        widgets = {
            'faculty': forms.Select(attrs={'readonly': 'readonly'}),
        }
