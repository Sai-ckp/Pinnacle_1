"""
Definition of models.
"""

from django.db import models

from django.db import models
class UserCustom(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)

    passcode = models.CharField(max_length=10, blank=True, null=True)  # Or use max_length you want
    passcode_set = models.BooleanField(default=False)
    can_reset_password = models.BooleanField(default=False) 

    wrong_attempts = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)


    def __str__(self):
        return self.username

class UserPermission(models.Model):
    user = models.ForeignKey(UserCustom, on_delete=models.CASCADE)
    form_name = models.CharField(max_length=150)

    can_view = models.BooleanField(default=False)
    can_add = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_access = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'form_name')

    def __str__(self):
        return f"{self.user.username} - {self.form_name}"



class Employee(models.Model):
    DESIGNATION_CHOICES = [
        ('Professor', 'Professor'),
        ('Associate Professor', 'Associate Professor'),
        ('Assistant Professor', 'Assistant Professor'),
    ]

    EMPLOYMENT_TYPE = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
    ]

    CATEGORY_CHOICES = [
        ('Teaching Staff', 'Teaching Staff'),
        ('Non-Teaching Staff', 'Non-Teaching Staff'),
    ]
    ROLE_CHOICES = [
        ('Primary', 'Primary'),
        ('Secondary', 'Secondary'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES,  blank=True,  # <-- Make it optional
    null=True )  # New field
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES) 
    emp_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    designation = models.CharField(
    max_length=50,
    choices=DESIGNATION_CHOICES,
    blank=True,  # <-- Make it optional
    null=True    # <-- Optional in DB too (for MySQL)
)

    department = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE)
    courses_taught = models.PositiveIntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class ExcelUpload(models.Model):
    file = models.FileField(upload_to='excel_uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

class StudentRecord(models.Model):
    student_id = models.CharField(max_length=20)
    student_name = models.CharField(max_length=100)
    guardian_name = models.CharField(max_length=100)
    guardian_phone = models.CharField(max_length=15)
    guardian_relation = models.CharField(max_length=50)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.student_name} ({self.student_id})"
# class SentMessage(models.Model):
#     subject = models.CharField(max_length=255)
#     message = models.TextField()
#     send_sms = models.BooleanField(default=False)
#     send_whatsapp = models.BooleanField(default=False)
#     department = models.CharField(max_length=100)
#     sent_at = models.DateTimeField(auto_now_add=True)
    
#     # Add this field for status
#     status = models.CharField(max_length=255, default="sms:0 whatsapp:0")

#     # Adding foreign keys to link the message to the student and guardian phone
#     student_name = models.ForeignKey(StudentRecord, on_delete=models.CASCADE, related_name='sent_messages')
#     guardian_phone_no = models.CharField(max_length=15, blank=True, null=True)  # Added phone number field

#     def __str__(self):
#         return f"{self.subject} ({self.department})"

# class MessageDelivery(models.Model):
#     message = models.ForeignKey(SentMessage, on_delete=models.CASCADE, related_name='deliveries')
#     student = models.ForeignKey(StudentRecord, on_delete=models.CASCADE)
#     phone_number = models.CharField(max_length=15)
#     status = models.CharField(
#         max_length=20,
#         choices=[('Delivered', 'Delivered'), ('Not Delivered', 'Not Delivered'), ('Pending', 'Pending')],
#         default='Pending'
#     )

#     def __str__(self):
#         return f"{self.student.student_name} - {self.status}"

class Student(models.Model):
    id = models.AutoField(primary_key=True)
    admission_no = models.CharField(max_length=20, unique=True)
    student_name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=15, null=True, blank=True)
    parent_phone = models.CharField(max_length=15, null=True, blank=True)
    course_type = models.CharField(max_length=10, choices=[('PU', 'PU'), ('Degree', 'Degree')])
    category = models.CharField(max_length=10, null=True, blank=True)
    quota_type = models.CharField(max_length=20)
    admission_date = models.DateField()

    class Meta:
        db_table = 'master_student'  # tells Django to use your manually created table

    def __str__(self):
        return f"{self.student_name} ({self.admission_no})"




 # or wherever your Course model is defined
class Subject(models.Model):
    name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=20, null=True, blank=True)
    credit = models.PositiveIntegerField(null=True, blank=True)
    course = models.ForeignKey('master.Course', on_delete=models.CASCADE)
    semester_number = models.PositiveIntegerField()
    faculty = models.ForeignKey('master.Employee', on_delete=models.SET_NULL, null=True, blank=True) # adjust if needed
    is_active = models.BooleanField(default=True)  # ✅ Add this field

    def __str__(self):
        return f"{self.name} (Sem {self.semester_number})"
       
# class Subject(models.Model):
#     name = models.CharField(max_length=100)
#     semester_number = models.PositiveIntegerField()
#     course = models.ForeignKey('Course', on_delete=models.CASCADE)
#     subject_code = models.CharField(max_length=20, null=True, blank=True)
#     credit = models.PositiveIntegerField(null=True, blank=True)
#     faculty = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True)

#     def __str__(self):
#         return f"{self.name} (Sem {self.semester_number}, {self.course.name})"

# class Subject(models.Model):
#     name = models.CharField(max_length=100)
#     semester_number = models.PositiveIntegerField()
#     course = models.ForeignKey('Course', on_delete=models.CASCADE)
#     subject_code = models.CharField(max_length=20, null=True, blank=True)
#     credit = models.PositiveIntegerField(null=True, blank=True)

#     def __str__(self):
#         return f"{self.name} (Sem {self.semester_number}, {self.course.name})"

from django.db import models

class Semester(models.Model):
    number = models.PositiveIntegerField()
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)  # ✅ Active (1) or Inactive (0)

    def __str__(self):
        return f"Sem {self.number} - {self.course.name}"


class CourseType(models.Model):
    id = models.AutoField(primary_key=True)  # AutoIncrement field, UNSIGNED is not explicitly specified in Django
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


from django.db import models

class Course(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    duration_years = models.PositiveIntegerField()
    total_semesters = models.PositiveIntegerField()
    course_type = models.ForeignKey(
        'CourseType',
        on_delete=models.CASCADE,
        related_name='courses'
    )
    is_active = models.BooleanField(default=True)  # NEW FIELD

    def __str__(self):
        return self.name

class Transport(models.Model):
    route_name = models.CharField(max_length=100)
    route = models.CharField(max_length=255)
    bus_no = models.CharField(max_length=50)
    driver_name = models.CharField(max_length=100)
    driver_contact_no = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.bus_no} - {self.route_name}"

class StudentDatabase(models.Model):
    admission_no = models.CharField(max_length=20)
    student_name = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    quota_type = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    student_userid = models.CharField(max_length=50, blank=True, null=True)
    # New fields:
    student_phone_no = models.CharField(max_length=15, blank=True, null=True)  # Match admission model
    parent_name = models.CharField(max_length=100, blank=True, null=True)
    course_type = models.ForeignKey(CourseType, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_database_entries')
    class Meta:
        db_table = 'master_student_database'

    def __str__(self):
        return f"{self.admission_no} - {self.student_name}"


# models.py

from django.db import models

EVENT_TYPES = [
    ('deadline', 'Deadline'),
    ('registration', 'Registration'),
    ('event', 'Event'),
    ('meeting', 'Meeting'),
    ('cultural', 'Cultural Event'),
    ('fest', 'Fest'),
]

class AcademicEvent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.date}"

from django.db import models

EVENT_TYPES = [
    ('deadline', 'Deadline'),
    ('registration', 'Registration'),
    ('event', 'Event'),
    ('meeting', 'Meeting'),
    ('cultural', 'Cultural Event'),
    ('fest', 'Fest'),
]

class AcademicEvent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.date}"





class SentMessage(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    send_sms = models.BooleanField(default=False)
    send_whatsapp = models.BooleanField(default=False)
    department = models.CharField(max_length=100)
    template_name = models.CharField(max_length=255, null=True, blank=True)  # <-- add this
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} ({self.department})"




class SentMessageContact(models.Model):
    sent_message = models.ForeignKey(SentMessage, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15)
    status = models.CharField(max_length=20, default='Pending')  # Sent / Failed / Pending
    sent_date = models.DateField(null=True, blank=True)  

    def __str__(self):
        return f"{self.phone} - {self.status}"
