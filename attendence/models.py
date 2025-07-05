from django.db import models
from django.db import models
from master.models import Employee  # Adjust if Employee is in another app

class attendancesettings(models.Model):
    check_in_time = models.TimeField(default="09:00")
    grace_period = models.IntegerField(default=15)  # in minutes
    late_threshold = models.IntegerField(default=40)  # in minutes

    class Meta:
        db_table = 'attendence_attendancesettings'

import datetime

class attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    check_in = models.TimeField()
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20)  # 'Present', 'Late', 'Absent'
 
    def save(self, *args, **kwargs):
        settings = attendancesettings.objects.first()
        if settings and self.check_in:
            check_in_time = datetime.datetime.combine(self.date, settings.check_in_time)
            actual = datetime.datetime.combine(self.date, self.check_in)
            diff = (actual - check_in_time).total_seconds() / 60
            if diff <= settings.grace_period:
                self.status = "Present"
            elif diff <= settings.late_threshold:
                self.status = "Late"
            else:
                self.status = "Absent"
        else:
            self.status = "Absent"
        super().save(*args, **kwargs)


from django.db import models
from master.models import StudentDatabase, Subject


class StudentAttendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('late', 'Late'),
        ('absent', 'Absent'),
    ]

    course = models.CharField(max_length=100, null=True, blank=True)
    subject = models.CharField(max_length=100, null=True, blank=True)
    attendance_date = models.DateField(null=True, blank=True)
    faculty_name = models.CharField(max_length=100, null=True, blank=True)

    student_name = models.CharField(max_length=100, null=True, blank=True)
    admission_no = models.CharField(max_length=20, null=True, blank=True)
    student_userid = models.CharField(max_length=50, null=True, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True, blank=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    overall_attendance = models.FloatField(default=0, null=True, blank=True)

    def __str__(self):
        return f"{self.student_name} ({self.admission_no}) - {self.subject} on {self.attendance_date}: {self.status}"

    class Meta:
        unique_together = ('admission_no', 'subject', 'attendance_date')

