from django.db import models
from master.models import CourseType, Course  # adjust if your app name is different
import datetime
from django.utils.timezone import now
class Enquiry1(models.Model):
    enquiry_no = models.CharField(max_length=10, unique=True, blank=True)
    student_name = models.CharField(max_length=100)

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    PARENT_CHOICES = [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Guardian', 'Guardian'),
    ]
    enquiry_date = models.DateField(default=now)
    parent_relation = models.CharField(max_length=10, choices=PARENT_CHOICES)
    guardian_relation = models.CharField(max_length=100, blank=True, null=True)  # new field
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=15)

    course_type = models.ForeignKey('master.CourseType', on_delete=models.PROTECT, default=1)
    course = models.ForeignKey('master.Course', on_delete=models.PROTECT)

    percentage_10th = models.FloatField()
    percentage_12th = models.FloatField(null=True, blank=True)
    
    email = models.EmailField(max_length=254)
    created_by = models.IntegerField(null=True, blank=True)
    permanent_address = models.TextField(blank=True, null=True)
    current_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=6, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    SOURCE_CHOICES = [
    ('Messages/Calls', 'Messages/Calls'),
    ('Social Media', 'Social Media'),
    ('Friends', 'Friends'),
    ('Other', 'Other'),
]

    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    other_source = models.CharField(max_length=100, blank=True, null=True)


    def save(self, *args, **kwargs):
        if not self.enquiry_no:
            last_enquiry = Enquiry1.objects.order_by('-id').first()
            if last_enquiry and last_enquiry.enquiry_no and last_enquiry.enquiry_no.startswith('PU-ENQ-'):
                try:
                    last_number = int(last_enquiry.enquiry_no.split('-')[-1])
                except (IndexError, ValueError):
                    last_number = 0
            else:
                last_number = 0
            self.enquiry_no = f"PU-ENQ-{last_number+1:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.enquiry_no} - {self.student_name}"



class Enquiry2(models.Model):
    enquiry_no = models.CharField(max_length=10, unique=True, blank=True)
    student_name = models.CharField(max_length=100)
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    PARENT_CHOICES = [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Guardian', 'Guardian'),
    ]
    parent_relation = models.CharField(max_length=10, choices=PARENT_CHOICES)
    enquiry_date = models.DateField(default=now)

    
    guardian_relation = models.CharField(max_length=100, blank=True, null=True)  # new field
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=15)

    course_type = models.ForeignKey('master.CourseType', on_delete=models.PROTECT, default=1)
    course = models.ForeignKey('master.Course', on_delete=models.PROTECT)

    percentage_10th = models.FloatField()
    percentage_12th = models.FloatField(null=True, blank=True)
    
    email = models.EmailField(max_length=254)
    created_by = models.IntegerField(null=True, blank=True)
    permanent_address = models.TextField(blank=True, null=True)
    current_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=6, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    SOURCE_CHOICES = [
    ('Messages/Calls', 'Messages/Calls'),
    ('Social Media', 'Social Media'),
    ('Friends', 'Friends'),
    ('Other', 'Other'),
]

    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    other_source = models.CharField(max_length=100, blank=True, null=True)


    def save(self, *args, **kwargs):
        if not self.enquiry_no:
            last_enquiry = Enquiry2.objects.order_by('-id').first()
            if last_enquiry and last_enquiry.enquiry_no and last_enquiry.enquiry_no.startswith('DEG-ENQ-'):
                try:
                    last_number = int(last_enquiry.enquiry_no.split('-')[-1])
                except (IndexError, ValueError):
                    last_number = 0
            else:
                last_number = 0
            self.enquiry_no = f"DEG-ENQ-{last_number+1:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.enquiry_no} - {self.student_name}"





class FollowUp(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]
    pu_enquiry = models.ForeignKey(Enquiry1, null=True, blank=True, on_delete=models.CASCADE)
    degree_enquiry = models.ForeignKey(Enquiry2, null=True, blank=True, on_delete=models.CASCADE)
    follow_up_type = models.CharField(max_length=100)
    follow_up_date = models.DateTimeField()
    priority = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    next_action_required = models.CharField(max_length=255, blank=True, null=True)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        verbose_name="Follow-up Status"
    )
    def __str__(self):
        return f"{self.enquiry} - {self.follow_up_type} - {self.status}"


 

from master.models import CourseType, Course  # adjust import as per your app structure

from master.models import CourseType, Course  # adjust import as per your app structure

class PUAdmission(models.Model):
    enquiry_no = models.CharField(max_length=20, blank=True, null=True)
    admission_no = models.CharField(max_length=20, blank=True, null=True)
    student_name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
    )
    parent_name = models.CharField(max_length=100)

    parent_mobile_no = models.CharField(max_length=15, blank=True, null=True)  # Updated to match HTML
    email = models.EmailField(max_length=100, blank=True, null=True)
    student_phone_no = models.CharField(max_length=15, blank=True, null=True)
    aadhar_no = models.CharField(max_length=12, blank=True, null=True)
    CATEGORY_CHOICES = [
        ('GENERAL', 'General'),
        ('OBC', 'OBC'),
        ('SC', 'SC'),
        ('ST', 'ST'),
    ]
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')
    ]
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    current_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=6, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    parents_occupation = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    document_submitted = models.BooleanField(default=False)
    hostel_required = models.BooleanField(default=False)
    hostel_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # ✅ New field
    transport = models.ForeignKey('master.Transport', on_delete=models.SET_NULL, null=True, blank=True)

    # Academic details
    year_of_passing = models.CharField(max_length=7, blank=True, null=True)
    sslc_reg_no = models.CharField(max_length=30, null=True, blank=True)
    sslc_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    medium = models.CharField(max_length=50, blank=True, null=True)
    second_language = models.CharField(max_length=50, blank=True, null=True)

    # Foreign keys for course
    course_type = models.ForeignKey('master.CourseType', on_delete=models.SET_NULL, null=True, blank=True, related_name='pu_admissions')
    course = models.ForeignKey('master.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='pu_admissions')

    # Quota type
    QUOTA_TYPE_CHOICES = [
        ('Regular', 'Regular'),
        ('Management', 'Management'),
        ('NRI', 'NRI'),
    ]
    quota_type = models.CharField(
        max_length=20,
        choices=QUOTA_TYPE_CHOICES,
        default='Regular'
    )
    admission_taken_by = models.IntegerField(null=True, blank=True)
    admission_date = models.DateField(default=datetime.date.today)
    # Last studied course details (subjects/marks)
    register_no_course = models.CharField(max_length=100, blank=True, null=True)
    month_year_passed = models.CharField(max_length=50, blank=True, null=True)
    subject1 = models.CharField(max_length=100, blank=True, null=True)
    marks_obtained1 = models.CharField(max_length=50, blank=True, null=True)
    total_marks_percentage1 = models.CharField(max_length=50, blank=True, null=True)
    subject2 = models.CharField(max_length=100, blank=True, null=True)
    marks_obtained2 = models.CharField(max_length=50, blank=True, null=True)
    total_marks_percentage2 = models.CharField(max_length=50, blank=True, null=True)
    subject3 = models.CharField(max_length=100, blank=True, null=True)
    marks_obtained3 = models.CharField(max_length=50, blank=True, null=True)
    total_marks_percentage3 = models.CharField(max_length=50, blank=True, null=True)
    subject4 = models.CharField(max_length=100, blank=True, null=True)
    marks_obtained4 = models.CharField(max_length=50, blank=True, null=True)
    total_marks_percentage4 = models.CharField(max_length=50, blank=True, null=True)
    subject5 = models.CharField(max_length=100, blank=True, null=True)
    marks_obtained5 = models.CharField(max_length=50, blank=True, null=True)
    total_marks_percentage5 = models.CharField(max_length=50, blank=True, null=True)
    subject6 = models.CharField(max_length=100, blank=True, null=True)
    marks_obtained6 = models.CharField(max_length=50, blank=True, null=True)
    total_marks_percentage6 = models.CharField(max_length=50, blank=True, null=True)

    co_curricular_activities = models.TextField(blank=True, null=True)

    # Declaration
    student_declaration_date = models.DateField(blank=True, null=True)
    student_declaration_place = models.CharField(max_length=100, blank=True, null=True)
    parent_declaration_date = models.DateField(blank=True, null=True)
    parent_declaration_place = models.CharField(max_length=100, blank=True, null=True)
    admitted_to = models.ForeignKey('master.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='pu_admitted_students')

    # Office use
    receipt_no = models.CharField(max_length=50, blank=True, null=True)
    receipt_date = models.DateField(blank=True, null=True)
    payment_mode = models.CharField(max_length=50, blank=True, null=True)
    utr_no = models.CharField(max_length=50, blank=True, null=True)
    # accountant_signature = models.CharField(max_length=255, blank=True, null=True)

    # Document submission flags
    doc_aadhar = models.BooleanField(default=False)
    doc_marks_card = models.BooleanField(default=False)
    doc_caste_certificate = models.BooleanField(default=False)  # ✅ New field
    doc_income_certificate = models.BooleanField(default=False)  # ✅ New field
    doc_transfer = models.BooleanField(default=False)
    doc_migration = models.BooleanField(default=False)
        # Scholarship details
    has_scholarship = models.BooleanField(default=False)
    scholarship_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(
    max_length=20,
    choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Review', 'Review')],
    default='Pending'
)

    # Photo
    photo = models.ImageField(upload_to='student_photos/', null=True, blank=True)


    def __str__(self):
        return f"{self.student_name} - {self.admission_no}"


import datetime
from django.db import models
from master.models import Transport
class DegreeAdmission(models.Model):
    CATEGORY_CHOICES = [
        ('GENERAL', 'General'),
        ('OBC', 'OBC'),
        ('SC', 'SC'),
        ('ST', 'ST'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    QUOTA_TYPE_CHOICES = [
        ('Regular', 'Regular'),
        ('Management', 'Management'),
        ('NRI', 'NRI'),
    ]
    quota_type = models.CharField(
        max_length=20,
        choices=QUOTA_TYPE_CHOICES,
        default='Regular'
    )
    # Primary key 'id' is auto-created by Django unless you specify otherwise
    admission_no = models.CharField(max_length=20, blank=True, null=True)
    student_name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    student_phone_no = models.CharField(max_length=15, blank=True, null=True)
    parent_phone_no = models.CharField(max_length=15, blank=True, null=True)
    pu_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    pu_reg_no = models.CharField(max_length=30, blank=True, null=True)
    year_of_passing = models.CharField(max_length=7, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    admission_date = models.DateField(default=datetime.date.today)
    photo = models.ImageField(upload_to='student_photos/', null=True, blank=True)
    application_status = models.CharField(max_length=30, default='Pending', blank=True, null=True)
    enquiry_no = models.CharField(max_length=10, blank=True, null=True)
    has_scholarship = models.BooleanField(default=False)
    scholarship_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    course_type = models.ForeignKey(
        'master.CourseType', on_delete=models.SET_NULL, null=True, blank=True, related_name='degree_admissions'
    )
    course = models.ForeignKey(
        'master.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='degree_admissions'
    )

    nationality = models.CharField(max_length=50, blank=True, null=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    current_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    parents_occupation = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    document_submitted = models.BooleanField(default=False)
    hostel_required = models.BooleanField(default=False)
    hostel_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # ✅ New field
    transport = models.ForeignKey(Transport, on_delete=models.SET_NULL, null=True, blank=True)

    pincode = models.CharField(max_length=6, blank=True, null=True)
    parent_name = models.CharField(max_length=100, blank=True, null=True)
    aadhar_no = models.CharField(max_length=12, blank=True, null=True)
    admission_taken_by = models.IntegerField(blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    sslc_reg_no = models.CharField(max_length=30, blank=True, null=True)
    sslc_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    pu_college_name = models.CharField(max_length=255, blank=True, null=True)
    medium = models.CharField(max_length=50, blank=True, null=True)
    second_language = models.CharField(max_length=50, blank=True, null=True)
    college_last_attended = models.CharField(max_length=255, blank=True, null=True)
    register_no_course = models.CharField(max_length=100, blank=True, null=True)
    month_year_passed = models.CharField(max_length=50, blank=True, null=True)
    co_curricular_activities = models.TextField(blank=True, null=True)
    student_declaration_date = models.DateField(blank=True, null=True)
    student_declaration_place = models.CharField(max_length=100, blank=True, null=True)
    parent_declaration_date = models.DateField(blank=True, null=True)
    parent_declaration_place = models.CharField(max_length=100, blank=True, null=True)
    receipt_no = models.CharField(max_length=50, blank=True, null=True)
    receipt_date = models.DateField(blank=True, null=True)
    payment_mode = models.CharField(max_length=50, blank=True, null=True)
    utr_no = models.CharField(max_length=50, blank=True, null=True)
    accountant_signature = models.CharField(max_length=255, blank=True, null=True)

    subject1 = models.CharField(max_length=100, blank=True, null=True)
    marks_obtained1 = models.CharField(max_length=50, blank=True, null=True)
    total_marks_percentage1 = models.CharField(max_length=50, blank=True, null=True)

    subject2 = models.CharField(max_length=100, blank=True, null=True)
    marks_obtained2 = models.CharField(max_length=50, blank=True, null=True)
    total_marks_percentage2 = models.CharField(max_length=50, blank=True, null=True)

    subject3 = models.CharField(max_length=100, blank=True, null=True)
    marks_obtained3 = models.CharField(max_length=50, blank=True, null=True)
    total_marks_percentage3 = models.CharField(max_length=50, blank=True, null=True)

    subject4 = models.CharField(max_length=100, blank=True, null=True)
    marks_obtained4 = models.CharField(max_length=50, blank=True, null=True)
    total_marks_percentage4 = models.CharField(max_length=50, blank=True, null=True)

    subject5 = models.CharField(max_length=100, blank=True, null=True)
    marks_obtained5 = models.CharField(max_length=50, blank=True, null=True)
    total_marks_percentage5 = models.CharField(max_length=50, blank=True, null=True)

    # Document submission checkboxes
    doc_aadhar = models.BooleanField(default=False)
    doc_marks_card = models.BooleanField(default=False)
    doc_caste_certificate = models.BooleanField(default=False)  # ✅ New field
    doc_income_certificate = models.BooleanField(default=False)  # ✅ New field
    doc_transfer = models.BooleanField(default=False)
    doc_migration = models.BooleanField(default=False)

    status = models.CharField(
    max_length=20,
    choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Review', 'Review')],
    default='Pending'
)
    # STATS Number field
    sats_number = models.CharField(max_length=50, blank=True, null=True)

    admitted_to = models.ForeignKey(
        'master.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='admitted_students'
    )

    def __str__(self):
        return f"{self.admission_no} - {self.student_name}"



    def __str__(self):
        return self.student_name
    
    # For PUAdmission
from django.db import models
class PUAdmissionshortlist(models.Model):
    admission_no = models.CharField(max_length=20)
    parent_mobile_no = models.CharField(max_length=15)
    email = models.EmailField()
    student_name = models.CharField(max_length=100)
    quota_type = models.CharField(
        max_length=20,
        choices=[
            ('Regular', 'Regular'),
            ('Management', 'Management'),
        ]
    )
    application_status = models.CharField(
        max_length=50,
        choices=[
            ('Pending', 'Pending'),
            ('Shortlisted', 'Shortlisted'),
            ('Rejected', 'Rejected'),
            ('Shortlisted(M)', 'Shortlisted Management'),  # Short code stored, label shown
        ],
        default='Pending'
    )
    admin_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.student_name


class DegreeAdmissionshortlist(models.Model):
    admission_no = models.CharField(max_length=20)
    parent_mobile_no = models.CharField(max_length=15)
    email = models.EmailField()
    student_name = models.CharField(max_length=100)
    quota_type = models.CharField(
        max_length=20,
        choices=[
            ('Regular', 'Regular'),
            ('Management', 'Management'),
        ]
    )
    application_status = models.CharField(
        max_length=50,
        choices=[
            ('Pending', 'Pending'),
            ('Shortlisted', 'Shortlisted'),
            ('Rejected', 'Rejected'),
            ('Shortlisted(M)', 'Shortlisted Management'),  # Short code stored, label shown
        ],
        default='Pending'
    )
    admin_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.student_name

from django.db import models

class PUFeeDetail(models.Model):
    student_name = models.CharField(max_length=100)
    admission_no = models.CharField(max_length=20)
    course = models.CharField(max_length=100)

    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2)
    scholarship = models.DecimalField(max_digits=10, decimal_places=2)
    final_fee_after_advance = models.DecimalField(max_digits=10, decimal_places=2)
    tuition_advance_amount = models.DecimalField(max_digits=10, decimal_places=2)
    gross_fee = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    payment_mode = models.CharField(
        max_length=20,
        choices=[('Online', 'Online'), ('Offline', 'Offline')]
    )

    transport_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hostel_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    books_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    uniform_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
     # 🔁 Automatically updates on save

    def __str__(self):
        return f"{self.admission_no} - {self.student_name}"





from django.db import models
from .models import DegreeAdmission  # Make sure this import is correct

class DegreeFeeDetail(models.Model):
    student_name = models.CharField(max_length=100)
    admission_no = models.CharField(max_length=20)
    course = models.CharField(max_length=10)

    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2)
    scholarship = models.DecimalField(max_digits=10, decimal_places=2)
    final_fee_after_advance = models.DecimalField(max_digits=10, decimal_places=2)
    tuition_advance_amount = models.DecimalField(max_digits=10, decimal_places=2)
    gross_fee = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    # Newly added fields
    transport_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hostel_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    books_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    uniform_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    payment_mode = models.CharField(
        max_length=20,
        choices=[('Online', 'Online'), ('Offline', 'Offline')]
    )
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)


    def __str__(self):
        return f"{self.admission_no} - {self.student_name}"

from django.db import models

class StudentLogin(models.Model):
    admission_no = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)
    is_default_password = models.BooleanField(default=True)
    # student_type = models.CharField(max_length=10, choices=[('PU', 'PU'), ('Degree', 'Degree')])
    parent_mobile_no = models.CharField(max_length=15)
    email = models.EmailField()
    student_name = models.CharField(max_length=100)

    def __str__(self):
        return self.admission_no




from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from django.utils.timezone import now

from django.db import models


from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from django.utils.timezone import now

from django.db import models


class Student(models.Model):          # ← or keep “Student”
    STATUS_CHOICES = [
        ('Regular', 'Regular'),
        ('Paid', 'Paid'),
        ('Partial', 'Partial'),
        ('Due', 'Due'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Online', 'Online'),
        ('Bank Transfer', 'Bank Transfer'),
    ]


    # ─────────── Core Fields ───────────
    admission_no = models.CharField(max_length=20, unique=True)
    name         = models.CharField(max_length=100)
    course       = models.CharField(max_length=100)

    #fee types
    transport_fee = models.CharField(max_length=100)
    hostel_fee = models.CharField(max_length=100)
    books_fee = models.CharField(max_length=100)
    uniform_fee = models.CharField(max_length=100)
    scholarship = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tuition_advance_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # fee paid
    transport_fee_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_pending_fee = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    transport_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    hostel_fee_paid = models.DecimalField(max_digits=10, decimal_places=2)
    hostel_pending_fee = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    hostel_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    books_fee_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    books_pending_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    books_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    uniform_fee_paid = models.DecimalField(max_digits=10, decimal_places=2)
    uniform_pending_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    uniform_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


    # renamed ↓↓↓
    tuition_fee= models.DecimalField(max_digits=10, decimal_places=2)
    final_fee_after_advance = models.DecimalField(max_digits=10, decimal_places=2)

    # existing payment-tracking fields
    tuition_fee_paid         = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tuition_pending_fee      = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tuition_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


    # optional instalment helpers
    next_installment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    next_due_date = models.DateField(null=True, blank=True)



    # meta / status
    payment_date = models.DateField(auto_now_add=True)
    payment_method   = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)

            # New fields
    other_fee = models.CharField(max_length=100, blank=True, null=True)
    other_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.admission_no} - {self.name}"


from django.db import models

class StudentPaymentHistory(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Online', 'Online'),
        ('Bank Transfer', 'Bank Transfer'),
    ]

    # ─────────── Core Student Info ───────────
    admission_no = models.CharField(max_length=20)
    name         = models.CharField(max_length=100)
    course       = models.CharField(max_length=100)

    # ─────────── Fee Type (for logging what kind of payment this is) ───────────
    fee_type     = models.CharField(max_length=50)  # e.g., 'Tuition', 'Transport', etc.

    # ─────────── Fee Fields ───────────
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tuition_fee_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tuition_pending_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tuition_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    transport_fee = models.CharField(max_length=100, null=True, blank=True)
    transport_fee_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_pending_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    hostel_fee = models.CharField(max_length=100, null=True, blank=True)
    hostel_fee_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hostel_pending_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hostel_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    books_fee = models.CharField(max_length=100, null=True, blank=True)
    books_fee_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    books_pending_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    books_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    uniform_fee = models.CharField(max_length=100, null=True, blank=True)
    uniform_fee_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    uniform_pending_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    uniform_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    other_fee = models.CharField(max_length=100, null=True, blank=True)
    other_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # ─────────── Scholarships / Advance / Final ───────────
    scholarship = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tuition_advance_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_fee_after_advance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # ─────────── Installments ───────────
    next_installment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    next_due_date = models.DateField(null=True, blank=True)

    # ─────────── Meta Info ───────────
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    # models.py
    payment_date = models.DateField(null=True, blank=True)  # Ensure this exists

    def __str__(self):
        return f"{self.admission_no} - {self.fee_type} - ₹{self.get_amount_paid()}"

    def get_amount_paid(self):
        # Return amount paid based on fee_type
        return {
            'Tuition': self.tuition_fee_paid,
            'Transport': self.transport_fee_paid,
            'Hostel': self.hostel_fee_paid,
            'Books': self.books_fee_paid,
            'Uniform': self.uniform_fee_paid,
            'Other': self.other_amount
        }.get(self.fee_type, 0)

from master.models import CourseType
class ConfirmedAdmission(models.Model):
    admission_no = models.CharField(max_length=20)
    student_name = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    admission_date = models.DateField()
    documents_complete = models.BooleanField(default=False)
    admission_type = models.CharField(max_length=10)  # 'PU' or 'Degree'
    status = models.CharField(max_length=20, default='confirmed')
    student_userid = models.CharField(max_length=50, blank=True, null=True)
    student_password = models.CharField(max_length=128, blank=True, null=True)
    course_type = models.ForeignKey(CourseType, on_delete=models.SET_NULL, null=True, blank=True, related_name='confirmed_admissions')   

    def __str__(self):
        return f"{self.admission_no} ({self.admission_type})"
