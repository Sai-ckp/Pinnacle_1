from django.db import models
from django.db import models
from django.utils import timezone
from master.models import Subject,Employee,Semester


# Create your models here.

class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    def __str__(self): return f"{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"

class TimetableEntry(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'),
        ('Friday', 'Friday')
    ]
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.CharField(max_length=20)
    def __str__(self): return f"{self.semester} - {self.day} - {self.time_slot}"


class DailySubstitution(models.Model):
    timetable_entry = models.ForeignKey(TimetableEntry, on_delete=models.CASCADE)
    date = models.DateField()
    substitute_faculty = models.ForeignKey(Employee, on_delete=models.CASCADE)
    updated_subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL)