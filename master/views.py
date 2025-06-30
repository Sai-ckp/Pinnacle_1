from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages

from django.shortcuts import render, redirect
from .models import UserCustom
from license.models import License

def blank_view(request):
    return render(request, 'master/blank.html')
 
def custom_login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
 
        try:
            user = UserCustom.objects.get(username=username)
            if user.password == password:  # plain password check (consider hashing!)
                # Set logged-in user session
                request.session['user_id'] = user.id
                # Check license validity here (simple example)
                try:
                    license = License.objects.get(client_name=user.username, activated=True)
                except License.DoesNotExist:
                    license = None
                if license and license.is_valid():
                    request.session['license_valid'] = True
                    request.session['license_end_date'] = license.end_date.isoformat()
                    # Redirect to user dashboard
                    if user.id == 2:
                        return redirect('dashboard')
                    else:
                        return redirect('dashboard2')
                else:
                    # License invalid or not found - clear session and redirect to license check page
                    request.session['license_valid'] = False
                    return redirect('license_check_view')
 
            else:
                error = 'Invalid password'
        except UserCustom.DoesNotExist:
            error = 'User does not exist'
 
    users = UserCustom.objects.all()  # For user dropdown on login page
    return render(request, 'master/login.html', {'error': error, 'users': users})


from django.shortcuts import render, redirect
from .models import Course, Subject , Semester
from .forms import SubjectForm
 
def subject_list(request):
    subjects = Subject.objects.select_related('course', 'faculty').all()
    return render(request, 'master/subject_list.html', {'subjects': subjects})
 
 

from django.shortcuts import render, redirect
from .forms import SubjectForm
from .models import Semester, Subject

def add_subject(request):
    # Bind the form on POST, empty otherwise
    form = SubjectForm(request.POST or None)

    # Determine which course is selected (for loading semesters)
    if request.method == 'POST':
        selected_course_id = request.POST.get('course')
    else:
        selected_course_id = request.GET.get('course')

    # Load semesters for the dropdown if we have a course
    semesters = (
        Semester.objects
        .filter(course_id=selected_course_id)
        .order_by('number')
        if selected_course_id else []
    )

    # If the user submitted and the form fields (name, code, credit, etc.) are valid:
    if request.method == 'POST' and form.is_valid():
        semester_number = request.POST.get('semester_number')
        is_active_flag = request.POST.get('is_active', '1')

        # Make sure they actually picked a semester
        if not semester_number:
            form.add_error(None, "Please select a semester.")
        else:
            # Build the Subject instance, assign the manual fields, save, then redirect
            subject = form.save(commit=False)
            subject.semester_number = int(semester_number)
            subject.is_active = (is_active_flag == '1')
            subject.save()
            return redirect('subject_list')

    # Render the “Add Subject” page
    return render(request, 'master/add_subject.html', {
        'form': form,
        'semesters': semesters,
        'selected_course_id': selected_course_id,
    })




def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect('subject_list')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'master/subject_form.html', {'form': form})

# Subject Delete
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    subject.delete()
    return redirect('master/subject_list')

from django.http import JsonResponse
from .models import Employee

def get_faculties_by_subject(request):
    subject_name = request.GET.get('name', '').strip()
    faculties = Employee.objects.filter(department__iexact=subject_name)
    data = [{'id': f.id, 'name': f.name} for f in faculties]
    return JsonResponse({'faculties': data})




from django.shortcuts import render, redirect
from .models import Employee
from .forms import EmployeeForm
from django.db.models import Count


def employee_list(request):
    query = request.GET.get('q', '')
    employees = Employee.objects.filter(name__icontains=query) if query else Employee.objects.all()

    context = {
        'employees': employees,
        'total': employees.count(),
        'professors': employees.filter(designation="Professor").count(),
        'associate_professors': employees.filter(designation="Associate Professor").count(),
        'assistant_professors': employees.filter(designation="Assistant").count(),
    }
    return render(request, 'master/employee_list.html', context)

from django.shortcuts import render, redirect
from .models import Employee
from .forms import EmployeeForm

from django.shortcuts import render, redirect
from .forms import EmployeeForm
from .models import Employee

from django.shortcuts import render, redirect
from .forms import EmployeeForm
from .models import Employee

def add_employee(request):
    # Auto-generate next employee code

    excluded_fields= ['emp_code', 'category', 'designation', 'role']
    last_emp = Employee.objects.order_by('-id').first()
    if last_emp and last_emp.emp_code and last_emp.emp_code.startswith('EMP'):
        last_number = int(last_emp.emp_code.replace('EMP', ''))
    else:
        last_number = 0
    next_emp_code = f"EMP{last_number + 1:03d}"

    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            if not employee.emp_code:
                employee.emp_code = next_emp_code
            employee.save()
            return redirect('employee_list')  # Change to your list view URL name
    else:
        form = EmployeeForm(initial={'emp_code': next_emp_code})

    return render(request, 'master/employee_form.html', {
        'form': form,
        'next_emp_code': next_emp_code,
        'excluded_fields': excluded_fields,
    })



@login_required
def dashboard_view(request):
    return render(request, 'master/dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')


# def dashboard_router_view(request):
#     user_id = request.session.get('user_id')

#     if not user_id:
#         return redirect('login')

#     try:
#         user = UserCustom.objects.get(id=user_id)

#         if user.can_access_all:
#             return dashboard_view(request)
#         else:
#             return dashboard_view2(request)

#     except UserCustom.DoesNotExist:
#         return redirect('login')

from django.shortcuts import render, redirect
from .forms import ExcelUploadForm
from .models import ExcelUpload, StudentRecord
import pandas as pd
import os
import pandas as pd
import os
from django.shortcuts import render, redirect
from .models import ExcelUpload, StudentRecord
from .forms import ExcelUploadForm

import pandas as pd
import os
from django.shortcuts import render, redirect
from .models import ExcelUpload, StudentRecord
from .forms import ExcelUploadForm

def student_data_view(request):
    upload_form = ExcelUploadForm()
    files = ExcelUpload.objects.order_by('-uploaded_at')
    table_data = []

    # ✅ Handle file upload
    if request.method == 'POST' and 'upload_submit' in request.POST:
        upload_form = ExcelUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            upload_form.save()
            return redirect('student_data_view')

    # ✅ Combine and read all Excel files
    all_files = ExcelUpload.objects.all()
    combined_df = pd.DataFrame()

    for file_obj in all_files:
        try:
            file_path = file_obj.file.path
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext == '.xlsx':
                df = pd.read_excel(file_path, engine='openpyxl')
            else:
                continue

            # ✅ Normalize column names
            df.columns = df.columns.str.strip().str.lower()
            combined_df = pd.concat([combined_df, df], ignore_index=True)

        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

    # ✅ Safe processing
    required_cols = {'student id', 'student name'}

    if not combined_df.empty:
        actual_cols = set(combined_df.columns)
        print("Available columns:", combined_df.columns)

        if required_cols.issubset(actual_cols):
            combined_df.drop_duplicates(subset=['student id', 'student name'], inplace=True)

            existing_records = StudentRecord.objects.values_list('student_id', 'student_name')
            existing_set = set((str(i).strip(), n.strip().lower()) for i, n in existing_records)

            for _, row in combined_df.iterrows():
                student_id = str(row.get('student id', '')).strip()
                student_name = str(row.get('student name', '')).strip().lower()

                if not student_id or not student_name:
                    continue

                if (student_id, student_name) not in existing_set:
                    StudentRecord.objects.create(
                        student_id=student_id,
                        student_name=row.get('student name', ''),
                        guardian_name=row.get('guardian name', ''),
                        guardian_phone=row.get('guardian phone number', ''),
                        guardian_relation=row.get('guardian relation with student', ''),
                        department=row.get('department', '')
                    )
                    existing_set.add((student_id, student_name))
        else:
            print("❌ Required columns missing in Excel. Found only:", actual_cols)

    # ✅ Always show saved data
    saved_records = StudentRecord.objects.all().values(
        'student_id', 'student_name', 'guardian_name',
        'guardian_phone', 'guardian_relation', 'department'
    )
    table_data = list(saved_records)

    return render(request, 'master/student_form.html', {
        'upload_form': upload_form,
        'files': files,
        'table_data': table_data
    })
# from .models import SentMessage, StudentRecord
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.db.models import Q
# from .models import SentMessage, StudentRecord

# @login_required
# def message_history_view(request):
#     # Get filters from URL parameters
#     channel_filter = request.GET.get('channel', '')
#     status_filter = request.GET.get('status', '')
#     department = request.GET.get('department')

#     # Start with all sent messages ordered by 'sent_at' date
#     messages = SentMessage.objects.all().order_by('-sent_at')

#     # Apply channel filters (SMS or WhatsApp)
#     if channel_filter == 'sms':
#         messages = messages.filter(send_sms=True)
#     elif channel_filter == 'whatsapp':
#         messages = messages.filter(send_whatsapp=True)

#     # Apply status and department filters
#     if status_filter:
#         messages = messages.filter(status=status_filter)
#     if department:
#         messages = messages.filter(department=department)

#     # Get the list of departments for the filter dropdown
#     departments = SentMessage.objects.values_list('department', flat=True).distinct()

#     # Process each message and add status and guardian details
#     for msg in messages:
#         # Fetch guardians for the given department of the message
#         students = StudentRecord.objects.filter(department=msg.department)
#         msg.guardians = []

#         # Loop through the guardians to check the status of each one
#         for guardian in students:
#             guardian_status = "Not Delivered"

#             # Check delivery status based on the message channels (SMS/WhatsApp)
#             if msg.send_sms and msg.send_whatsapp:
#                 guardian_status = "Delivered via SMS and WhatsApp"
#             elif msg.send_sms:
#                 guardian_status = "Delivered via SMS"
#             elif msg.send_whatsapp:
#                 guardian_status = "Delivered via WhatsApp"
            
#             # Add the guardian details to the message status
#             msg.guardians.append({
#                 "student": guardian.student_name,
#                 "phone": guardian.guardian_phone,
#                 "status": guardian_status
#             })

#         # Human-readable status based on the message's state
#         if msg.status.lower() == "pending":
#             # If both SMS and WhatsApp failed or are still in progress, mark it as Pending
#             if not msg.send_sms and not msg.send_whatsapp:
#                 msg.status_display = "Not Delivered"
#             else:
#                 msg.status_display = "Pending"
#         else:
#             # If both SMS and WhatsApp were successful, mark it as Delivered
#             if msg.send_sms and msg.send_whatsapp:
#                 msg.status_display = "Delivered"
#             else:
#                 msg.status_display = "Not Delivered"

#     return render(request, 'master/message_history.html', {
#         'messages': messages,
#         'channel_filter': channel_filter,
#         'status_filter': status_filter,
#         'department_filter': department,
#         'departments': departments,
#     })

import datetime
from django.shortcuts import render
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from admission.models import (
    Enquiry1, Enquiry2, PUAdmission, DegreeAdmission,
    Student as AdmissionStudent, Student
    
)
from attendence.models import StudentAttendance,attendance 
from .models import SentMessageContact, Employee

def dashboard_view(request):
    # Total Students
    total_pu_students = PUAdmission.objects.filter(status="confirmed").count()
    total_degree_students = DegreeAdmission.objects.filter(status="confirmed").count()
    total_students = total_pu_students + total_degree_students

    # Enquiries
    total_pu_enquiries = Enquiry1.objects.count()
    total_degree_enquiries = Enquiry2.objects.count()
    total_enquiries = total_pu_enquiries + total_degree_enquiries

    # Employees & Faculties
    total_employees = Employee.objects.count()
    faculty_designations = ['Professor', 'Associate Professor', 'Assistant']
    total_faculties = Employee.objects.filter(designation__in=faculty_designations).count()

    # WhatsApp & Admission messages
    enquiry1_sent = Enquiry1.objects.filter(whatsapp_status='sent').count()
    enquiry2_sent = Enquiry2.objects.filter(whatsapp_status='sent').count()
    enquiries_whatsapp_sent = enquiry1_sent + enquiry2_sent

    admission_messages_sent = SentMessageContact.objects.filter(status="Sent").count()
    pending_messages = SentMessageContact.objects.filter(status="Pending").count()
    total_messages_sent = enquiries_whatsapp_sent + admission_messages_sent

    # Total Collected Fee
  # --- Additional Fee Stats (Total Collected Fee from Student model only) ---
    decimal_type = DecimalField(max_digits=12, decimal_places=2)
    total_collected_fee = Student.objects.aggregate(
        total=Sum(
            ExpressionWrapper(
                Coalesce(F('tuition_fee_paid'), 0) +
                Coalesce(F('transport_fee_paid'), 0) +
                Coalesce(F('hostel_fee_paid'), 0) +
                Coalesce(F('books_fee_paid'), 0) +
                Coalesce(F('uniform_fee_paid'), 0) +
                Coalesce(F('other_amount'), 0),
                output_field=decimal_type
            )
        )
    )['total'] or 0
 
    # Total Application Fee Collected from PUAdmission
    total_pu_application_fee = PUAdmission.objects.aggregate(
        total=Sum('application_fee')
    )['total'] or 0
 
    # Total Application Fee Collected from DegreeAdmission
    total_degree_application_fee = DegreeAdmission.objects.aggregate(
        total=Sum('application_fee')
    )['total'] or 0
 
    # Combined Total Application Fee Collected
    total_application_fee = total_pu_application_fee + total_degree_application_fee

    # Faculty Attendance Rate (ALL TIME)
    total_faculty_attendance = attendance.objects.count()
    if total_faculty_attendance > 0:
        present_faculty_attendance = attendance.objects.filter(status__in=["Present", "Late"]).count()
        faculty_attendance_rate = round((present_faculty_attendance / total_faculty_attendance) * 100, 2)
    else:
        faculty_attendance_rate = 0

    # Student Attendance Rate (ALL TIME)
    total_student_attendance = StudentAttendance.objects.count()
    if total_student_attendance > 0:
        present_student_attendance = StudentAttendance.objects.filter(status__in=['present', 'late']).count()
        student_attendance_rate = round((present_student_attendance / total_student_attendance) * 100, 2)
    else:
        student_attendance_rate = 0

    context = {
        'total_students': total_students,
        'total_messages_sent': total_messages_sent,
        'total_collected_fee': total_collected_fee,
        'total_pu_enquiries': total_pu_enquiries,
        'total_degree_enquiries': total_degree_enquiries,
        'total_pu_students': total_pu_students,
        'total_degree_students': total_degree_students,
        'total_enquiries': total_enquiries,
        'total_employees': total_employees,
        'total_faculties': total_faculties,
        'enquiries_whatsapp_sent': enquiries_whatsapp_sent,
        'admission_messages_sent': admission_messages_sent,
        'pending_messages': pending_messages,
        'faculty_attendance_rate': faculty_attendance_rate,
        'student_attendance_rate': student_attendance_rate,
    }

    return render(request, 'master/dashboard.html', context)




from django.shortcuts import render
from django.db.models import Count
from admission.models import Enquiry1, Enquiry2
from .models import SentMessageContact

def communication_dashboard(request):
    # WhatsApp sent counts
    enquiry1_sent = Enquiry1.objects.filter(whatsapp_status='sent').count()
    enquiry2_sent = Enquiry2.objects.filter(whatsapp_status='sent').count()
    enquiry_total_sent = enquiry1_sent + enquiry2_sent

    sentmessage_sent = SentMessageContact.objects.filter(status="Sent").count()
    sentmessage_pending = SentMessageContact.objects.filter(status="Pending").count()
    total_messages_sent = enquiry_total_sent + sentmessage_sent

    # Recent Enquiry WhatsApp Messages
    recent_enquiry_msgs = list(
        Enquiry1.objects.filter(whatsapp_status__in=['sent', 'pending', 'failed']).order_by('-id').values(
            'enquiry_no', 'student_name', 'parent_phone', 'whatsapp_status', 'id'
        )
    ) + list(
        Enquiry2.objects.filter(whatsapp_status__in=['sent', 'pending', 'failed']).order_by('-id').values(
            'enquiry_no', 'student_name', 'parent_phone', 'whatsapp_status', 'id'
        )
    )
    # Sort together by id descending
    recent_enquiry_msgs = sorted(recent_enquiry_msgs, key=lambda x: x["id"], reverse=True)

    # Status breakdown for Enquiry WhatsApp Messages
    enquiry_status_breakdown = (
        list(Enquiry1.objects.values('whatsapp_status').annotate(count=Count('id'))) +
        list(Enquiry2.objects.values('whatsapp_status').annotate(count=Count('id')))
    )
    # Combine counts for same status
    enquiry_status_dict = {}
    for item in enquiry_status_breakdown:
        status = item['whatsapp_status']
        if status in enquiry_status_dict:
            enquiry_status_dict[status] += item['count']
        else:
            enquiry_status_dict[status] = item['count']
    # Ensure all statuses present, even if 0
    for key in ['pending', 'sent', 'failed']:
        if key not in enquiry_status_dict:
            enquiry_status_dict[key] = 0
    enquiry_status_labels = ['pending', 'sent', 'failed']
    enquiry_status_counts = [enquiry_status_dict.get(k, 0) for k in enquiry_status_labels]

    # Recent Admission WhatsApp Messages
    recent_sentmessage_msgs = list(
        SentMessageContact.objects.all().order_by('-id').values(
            'phone', 'status', 'id'
        )
    )

    # Status breakdown for Admission Open Messages
    status_breakdown = (
        SentMessageContact.objects
        .values('status')
        .annotate(count=Count('id'))
    )
    # Ensure all statuses present, even if 0
    status_dict = {item['status']: item['count'] for item in status_breakdown}
    for key in ['Pending', 'Sent', 'Failed']:
        if key not in status_dict:
            status_dict[key] = 0
    status_labels = ['Pending', 'Sent', 'Failed']
    status_counts = [status_dict.get(k, 0) for k in status_labels]

    context = {
        'total_messages_sent': total_messages_sent,
        'enquiry_total_sent': enquiry_total_sent,
        'sentmessage_sent': sentmessage_sent,
        'sentmessage_pending': sentmessage_pending,
        'recent_enquiry_msgs': recent_enquiry_msgs,
        'recent_sentmessage_msgs': recent_sentmessage_msgs,
        'status_labels': status_labels,
        'status_counts': status_counts,
        'enquiry_status_labels': enquiry_status_labels,
        'enquiry_status_counts': enquiry_status_counts,
    }
    return render(request, 'master/communication_dashboard.html', context)



 


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import StudentRecord, SentMessage
from asgiref.sync import sync_to_async, async_to_sync
import asyncio
from twilio.rest import Client
from django.conf import settings
from functools import partial
from django.utils import timezone

# Async Twilio sender with separate tracking
async def send_twilio_message(to_number, body, send_sms, send_whatsapp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    loop = asyncio.get_event_loop()
    result = {'sms': False, 'whatsapp': False}

    try:
        if send_whatsapp:
            await loop.run_in_executor(
                None,
                partial(
                    client.messages.create,
                    body=body,
                    from_=f'whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}',
                    to=f'whatsapp:{to_number}'
                )
            )
            result['whatsapp'] = True
    except Exception as e:
        print(f"❌ WhatsApp failed for {to_number}: {e}")

    try:
        if send_sms:
            await loop.run_in_executor(
                None,
                partial(
                    client.messages.create,
                    body=body,
                    from_=settings.TWILIO_SMS_NUMBER,
                    to=to_number
                )
            )
            result['sms'] = True
    except Exception as e:
        print(f"❌ SMS failed for {to_number}: {e}")

    return result

# ORM helpers wrapped in sync_to_async
@sync_to_async
def get_guardians_queryset(department):
    if department == "All":
        return list(StudentRecord.objects.all())
    return list(StudentRecord.objects.filter(department=department))

@sync_to_async
def create_pending_message(guardian, subject, message_text, send_sms, send_whatsapp):
    status = "sms:0 whatsapp:0"  # Initially not sent
    return SentMessage.objects.create(
        subject=subject,
        message=message_text,
        send_sms=send_sms,
        send_whatsapp=send_whatsapp,
        department=guardian.department,
        status=status,
        student_name=guardian,
        guardian_phone_no=guardian.guardian_phone.strip()
    )

@sync_to_async
def update_message_status(message_obj, status):
    message_obj.status = status
    message_obj.sent_at = timezone.now()
    message_obj.save()

# View Function
def compose_message(request):
    departments = StudentRecord.objects.values_list('department', flat=True).distinct()
    departments = sorted(set(departments))
    selected_department = request.POST.get('department', '')

    if request.method == 'POST':
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')
        send_sms = 'sms' in request.POST
        send_whatsapp = 'whatsapp' in request.POST
        department = request.POST.get('department')

        async def send_all():
            guardians = await get_guardians_queryset(department)
            full_message = f"Subject: {subject}\n{message_text}"
            failed = 0

            for guardian in guardians:
                phone = guardian.guardian_phone.strip()
                number = f'+91{phone}'  # Update this format if needed

                # Save initial message as pending
                message_obj = await create_pending_message(
                    guardian, subject, message_text, send_sms, send_whatsapp
                )

                # Send messages via Twilio
                result = await send_twilio_message(number, full_message, send_sms, send_whatsapp)

                # Compose actual status string
                status = f"sms:{int(result['sms'])} whatsapp:{int(result['whatsapp'])}"
                await update_message_status(message_obj, status)

                if not result['sms'] and not result['whatsapp']:
                    print(f"❌ Failed to send to: {number}")
                    failed += 1
                else:
                    print(f"✅ Sent to: {number} | Status: {status}")

            return failed

        failed_count = async_to_sync(send_all)()

        if failed_count == 0:
            messages.success(request, "✅ All messages sent successfully.")
        else:
            messages.warning(request, f"⚠️ Sent with {failed_count} failures.")

        return redirect('compose_message')

    return render(request, 'master/compose_message.html', {
        'departments': departments,
        'selected_department': selected_department
    })




# View for Message History with Filter
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import SentMessage

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import SentMessage


def message_history_view(request):
    channel_filter = request.GET.get('channel', '')
    status_filter = request.GET.get('status', '')
    department_filter = request.GET.get('department', '')

    # Get all messages and apply filters
    messages = SentMessage.objects.all().order_by('-sent_at')

    if channel_filter == 'sms':
        messages = messages.filter(send_sms=True)
    elif channel_filter == 'whatsapp':
        messages = messages.filter(send_whatsapp=True)

    if department_filter:
        messages = messages.filter(department=department_filter)

    departments = SentMessage.objects.values_list('department', flat=True).distinct()

    # Enhance messages with readable status and channel
    filtered_messages = []
    for msg in messages:
        # Safely parse status string like: "sms:1 whatsapp:0"
        status_parts = dict(part.split(":") for part in msg.status.split() if ":" in part)

        sms_status = status_parts.get("sms", "0")
        whatsapp_status = status_parts.get("whatsapp", "0")

        msg.sms_status_display = "Delivered" if sms_status == "1" else "Not Delivered"
        msg.whatsapp_status_display = "Delivered" if whatsapp_status == "1" else "Not Delivered"

        if sms_status == "1" and whatsapp_status == "1":
            msg.status_display = "Delivered via SMS and WhatsApp"
        elif sms_status == "1":
            msg.status_display = "Delivered via SMS"
        elif whatsapp_status == "1":
            msg.status_display = "Delivered via WhatsApp"
        else:
            msg.status_display = "Not Delivered"

        # Sent via channel
        if msg.send_sms and msg.send_whatsapp:
            msg.sent_via = "SMS & WhatsApp"
        elif msg.send_sms:
            msg.sent_via = "SMS"
        elif msg.send_whatsapp:
            msg.sent_via = "WhatsApp"
        else:
            msg.sent_via = "-"

        # Apply status filter logic
        if status_filter == "delivered":
            # At least one is delivered
            if sms_status == "1" or whatsapp_status == "1":
                filtered_messages.append(msg)
        elif status_filter in ["pending", "failed"]:
            # At least one is not delivered
            if sms_status != "1" or whatsapp_status != "1":
                filtered_messages.append(msg)
        elif not status_filter:
            # No filter, include all
            filtered_messages.append(msg)

    return render(request, 'master/message_history.html', {
        'messages': filtered_messages,
        'channel_filter': channel_filter,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'departments': departments,
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from twilio.rest import Client
from .models import SentMessage


@login_required
def resend_message_view(request, message_id):
    message = get_object_or_404(SentMessage, id=message_id)

    to_number = f"+91{message.guardian_phone_no.strip()}"
    body = f"Subject: {message.subject}\n{message.message}"

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    result = {'sms': False, 'whatsapp': False}

    try:
        if message.send_whatsapp:
            client.messages.create(
                body=body,
                from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
                to=f"whatsapp:{to_number}"
            )
            result['whatsapp'] = True
    except Exception as e:
        print(f"WhatsApp resend failed: {e}")

    try:
        if message.send_sms:
            client.messages.create(
                body=body,
                from_=settings.TWILIO_SMS_NUMBER,
                to=to_number
            )
            result['sms'] = True
    except Exception as e:
        print(f"SMS resend failed: {e}")

    # Update status after resend
    message.status = f"sms:{int(result['sms'])} whatsapp:{int(result['whatsapp'])}"
    message.save()

    messages.success(request, "Message resent successfully.")
    return redirect('compose_message')

from django.shortcuts import render, get_object_or_404, redirect
from .models import StudentDatabase
from .forms import StudentDatabaseForm


def student_list(request):
    """
    Display all students in the database.
    """
    students = StudentDatabase.objects.all().order_by('admission_no')
    return render(request, 'master/student_database_list.html', {
        'students': students,
    })

def master_student_edit(request, pk):
    student = get_object_or_404(StudentDatabase, pk=pk)
    selected_type = request.GET.get('course_type', getattr(student, 'course_type', 'PU'))  # Add this line

    if request.method == 'POST':
        form = StudentDatabaseForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('master_student_list')
    else:
        form = StudentDatabaseForm(instance=student)
    return render(request, 'master/student_database_form.html', {
        'form': form,
        'student': student,
        'edit_mode': True,
        'back_to_list_url': 'master_student_list',
        'selected_type': selected_type,  # Add this to context
    })

def master_student_view(request, pk):
    student = get_object_or_404(StudentDatabase, pk=pk)
    selected_type = request.GET.get('course_type', getattr(student, 'course_type', 'PU'))  # Add this line

    return render(request, 'master/student_database_form.html', {
        'form': StudentDatabaseForm(instance=student),
        'student': student,
        'edit_mode': False,
        'back_to_list_url': 'master_student_list',
        'selected_type': selected_type,  # Add this to context
    })




# from django.shortcuts import render, redirect
# from .models import Employee
# from .forms import EmployeeForm

# def employee_list_view(request):
#     Employees = Employee.objects.all()
#     return render(request, 'master/employee_list.html', {'Faculties': Employees})

# def employee_add_view(request):
#     if request.method == 'POST':
#         form = EmployeeForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('master/employee_list')   
#     else:
#         form = EmployeeForm()
#     return render(request, 'master/employee_form.html', {'form': form})




# views.py

# from django.shortcuts import render, redirect
# from .models import Course, Subject
# from .forms import SubjectForm

# def subject_list(request):
#     subjects = Subject.objects.select_related('course', 'faculty').all()
#     return render(request, 'master/subject_list.html', {'subjects': subjects})

# from django.shortcuts import render, redirect
# from .forms import SubjectForm
# from .models import Semester

# def add_subject(request):
#     semesters = []
#     selected_course_id = request.POST.get('course') if request.method == 'POST' else None

#     # Fetch semesters only if course is selected (to populate semester dropdown)
#     if selected_course_id:
#         semesters = Semester.objects.filter(course_id=selected_course_id).order_by('number')

#     if request.method == 'POST':
#         form = SubjectForm(request.POST)
#         semester_number = request.POST.get('semester')  # This is the selected semester number from form

#         if form.is_valid() and semester_number:
#             subject = form.save(commit=False)
#             subject.semester_number = int(semester_number)  # Save semester number as integer
#             subject.save()
#             return redirect('subject_list')  # Redirect after save
#     else:
#         form = SubjectForm()

#     return render(request, 'master/add_subject.html', {
#         'form': form,
#         'semesters': semesters,
#         'selected_course_id': selected_course_id
#     })

# views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, CourseType
from .forms import CourseForm, CourseTypeForm

# CourseType Views
def course_type_list(request):
    types = CourseType.objects.all()
    return render(request, 'master/course_type_list.html', {'types': types})

def course_type_create(request):
    if request.method == 'POST':
        form = CourseTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_type_list')
    else:
        form = CourseTypeForm()
    return render(request, 'master/course_type_form.html', {'form': form})

def course_type_edit(request, pk):
    course_type = get_object_or_404(CourseType, pk=pk)
    if request.method == 'POST':
        form = CourseTypeForm(request.POST, instance=course_type)
        if form.is_valid():
            form.save()
            return redirect('course_type_list')
    else:
        form = CourseTypeForm(instance=course_type)
    return render(request, 'master/course_type_form.html', {'form': form})

def course_type_delete(request, pk):
    course_type = get_object_or_404(CourseType, pk=pk)
    course_type.delete()
    return redirect('master/course_type_list')

# Course Views
def course_list(request):
    courses = Course.objects.select_related('course_type').all()
    return render(request, 'master/course_list.html', {'courses': courses})

from .models import Course
from .forms import CourseForm
from django.shortcuts import render, redirect
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)

            # Handle is_active manually based on radio input
            is_active_value = request.POST.get('is_active')
            course.is_active = True if is_active_value == '1' else False

            course.save()
            return redirect('course_list')  # Change to your list view name
    else:
        form = CourseForm()

    return render(request, 'master/course_form.html', {'form': form})

def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'master/course_form.html', {'form': form})

from django.db.models import ProtectedError

def course_delete(request, pk):
    course = Course.objects.get(pk=pk)
    try:
        course.delete()
        messages.success(request, "Course deleted successfully.")
    except ProtectedError:
        messages.error(request, "Cannot delete course because it is referenced by other data (e.g., Enquiries).")
    return redirect('course_list')  # or wherever you list coursesx



from .models import Semester
from .forms import SemesterForm

def semester_list(request):
    semesters = Semester.objects.select_related('course').all()
    return render(request, 'master/semester_list.html', {'semesters': semesters})

from .models import Semester
from .forms import SemesterForm
from django.shortcuts import render, redirect

def semester_add(request):
    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            semester = form.save(commit=False)

            # ✅ Manual handling of is_active (same style as course_create)
            is_active_value = request.POST.get('is_active')
            semester.is_active = True if is_active_value == '1' else False

            semester.save()
            return redirect('semester_list')
    else:
        form = SemesterForm()

    return render(request, 'master/semester_form.html', {
        'form': form
    })


# views.py
from django.http import JsonResponse
from .models import Course

def get_semester_numbers(request):
    course_id = request.GET.get('course_id')
    try:
        course = Course.objects.get(id=course_id)
        semesters = list(range(1, course.total_semesters + 1))
        return JsonResponse({'numbers': semesters})
    except Course.DoesNotExist:
        return JsonResponse({'numbers': []})






from django.shortcuts import render
from django.db.models import Sum
from admission.models import Enquiry1, PUAdmission, DegreeAdmission, Student as AdmissionStudent,DegreeAdmissionshortlist,PUAdmissionshortlist
from .models import StudentRecord, SentMessage

def dashboard_view2(request):
    # SMS Dashboard Stats
    total_students = StudentRecord.objects.count()
    messages_sent = SentMessage.objects.count()
    active_departments = SentMessage.objects.values('department').distinct().count()

    # Delivery Status Counts
    delivered_count = 0
    failed_count = 0

    all_messages = SentMessage.objects.all()
    for msg in all_messages:
        try:
            status_parts = dict(part.split(":") for part in msg.status.split() if ":" in part)
        except ValueError:
            status_parts = {}

        sms_status = status_parts.get("sms", "0")
        whatsapp_status = status_parts.get("whatsapp", "0")

        if sms_status == "1" or whatsapp_status == "1":
            delivered_count += 1
        else:
            failed_count += 1

    not_sent_count = SentMessage.objects.filter(status__isnull=False).exclude(status__icontains='sms:1').exclude(status__icontains='whatsapp:1').count()


    # Recent 5 Messages
    recent_messages_qs = SentMessage.objects.order_by('-sent_at')[:5]
    recent_messages = []

    for msg in recent_messages_qs:
        try:
            status_parts = dict(part.split(":") for part in msg.status.split() if ":" in part)
        except ValueError:
            status_parts = {}

        sms_status = status_parts.get("sms", "0")
        whatsapp_status = status_parts.get("whatsapp", "0")

        if sms_status == "1" and whatsapp_status == "1":
            msg.status_display = "Delivered via SMS and WhatsApp"
        elif sms_status == "1":
            msg.status_display = "Delivered via SMS"
        elif whatsapp_status == "1":
            msg.status_display = "Delivered via WhatsApp"
        else:
            msg.status_display = "Not Delivered"

        recent_messages.append(msg)

    # Enquiry & Admission Stats
    total_enquiries = Enquiry1.objects.count()
    total_pu_admissions = PUAdmissionshortlist.objects.count()
    total_degree_admissions = DegreeAdmissionshortlist.objects.count()

    pu_converted_enquiries = PUAdmission.objects.exclude(enquiry_no__isnull=True).exclude(enquiry_no='').count()
    degree_converted_enquiries = DegreeAdmission.objects.exclude(enquiry_no__isnull=True).exclude(enquiry_no='').count()

    # Fee Stats (from admission Student model)
   

    context = {
        # SMS
        'total_students': total_students,
        'messages_sent': messages_sent,
        'active_departments': active_departments,
        'not_sent_count': not_sent_count,
        'recent_messages': recent_messages,

        # Enquiry/Admission
        'total_enquiries': total_enquiries,
        'total_pu_admissions': total_pu_admissions,
        'total_degree_admissions': total_degree_admissions,
        'pu_converted_enquiries': pu_converted_enquiries,
        'degree_converted_enquiries': degree_converted_enquiries,

    }
    return render(request, 'master/dashboard2.html', context)

from .models import Transport
from .forms import TransportForm

def transport_list(request):
    transports = Transport.objects.all()
    return render(request, 'master/transport_list.html', {'transports': transports})

def transport_create(request):
    if request.method == 'POST':
        form = TransportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transport_list')
    else:
        form = TransportForm()
    return render(request, 'master/transport_form.html', {'form': form})



# views.py
from django.shortcuts import render
from django.utils import timezone
from .models import AcademicEvent
import calendar

def calendar_view(request):
    today = timezone.localdate()
    year = today.year
    month = today.month

    # Get the calendar for the current month, week starts on Sunday (6)
    cal = calendar.Calendar(firstweekday=6)
    month_days = list(cal.monthdayscalendar(year, month))
    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    # Filter future events only (date >= today)
    future_events_qs = AcademicEvent.objects.filter(date__gte=today).order_by('date', 'time')

    # Convert QuerySet to list of dicts for safe JSON serialization if needed
    future_events = list(future_events_qs.values(
        'id', 'title', 'date', 'time', 'description', 'event_type'
    ))

    context = {
        'today': today,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'month_days': month_days,
        'weekdays': weekdays,
        'events': future_events_qs,  # Use this for Django template iteration
        'events_json': future_events, # Use this for passing to JavaScript safely
    }

    return render(request, 'master/calendar.html', context)



from .forms import AcademicEventForm


def add_event_view(request):
    if request.method == 'POST':
        form = AcademicEventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('calendar')
    else:
        form = AcademicEventForm()

    return render(request, 'master/add_event.html', {'form': form})






import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from .models import SentMessage, SentMessageContact
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_exempt
def upload_excel(request):
    context = {}

    if request.method == 'POST' and request.FILES.get('file'):
        template_name = request.POST.get("template_name", "")

        # Save SentMessage
        msg = SentMessage.objects.create(
            subject="Auto Generated",
            message=f"Template: {template_name}",
            department="Auto",
            send_whatsapp=True,
            template_name=template_name
        )

        # Read uploaded Excel
        excel_file = request.FILES['file']
        df = pd.read_excel(excel_file)
        df.fillna("", inplace=True)

        # Save to DB
        headers = df.columns.tolist()
        rows = []

        for _, row in df.iterrows():
            phone = ""
            for col in headers:
                val = str(row[col]).strip()
                if any(x in col.lower() for x in ['phone', 'mobile', 'contact']):
                    phone = val
                    break

            contact = SentMessageContact.objects.create(
                sent_message=msg,
                phone=phone
            )

            row_data = [str(row[h]) for h in headers] + [contact.status, contact.id]
            rows.append(row_data)

        context = {
            'message': msg,
            'data_headers': headers + ['Status', 'Action'],
            'data_rows': rows
        }

    return render(request, 'master/whatsapp_bulk.html', context)




from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import requests
from .models import SentMessage

from django.conf import settings

@csrf_exempt
def send_message(request, msg_id):
    msg = get_object_or_404(SentMessage, id=msg_id)
    contacts = msg.contacts.all()

    if request.method == 'POST':
        template_name = request.POST.get('template_name') or msg.template_name
        msg.template_name = template_name
        msg.save()

        subscribers = [{"subscriberId": c.phone} for c in contacts]

        payload = {
            "message": {
                "messageType": "template",
                "name": template_name,
                "language": "en_US"
            },
            "subscribers": subscribers,
            "phoneNumberId": settings.MSGKART_PHONE_ID
        }

        url = f"{settings.MSGKART_BASE_URL}/api/v2/message/{settings.MSGKART_ACCOUNT_ID}/template?apikey={settings.MSGKART_API_KEY}"

        try:
            response = requests.post(url, json=payload)
            status = "Sent" if response.status_code == 200 else "Failed"
        except Exception:
            status = "Failed"

        for c in contacts:
            c.status = status
            c.save()

    # Render previous data again
    rows = []
    headers = []
    if contacts.exists():
        headers = ['Phone']
        rows = [[c.phone, c.status, c.id] for c in contacts]

    return render(request, 'master/whatsapp_bulk.html', {
        'message': msg,
        'data_headers': headers + ['Status', 'Action'],
        'data_rows': rows
    })




def delete_contact(request, contact_id):
    contact = get_object_or_404(SentMessageContact, id=contact_id)
    msg_id = contact.sent_message.id
    contact.delete()
    return redirect('send_message', msg_id=msg_id)


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def master_dashboard(request):
    # This assumes your permission logic is already handled in middleware or context processor
    context = {
        "allowed_forms": request.session.get("allowed_forms", []),
        "can_access_all": request.session.get("can_access_all", False),
    }
    return render(request, "master/master_dashboard.html", context)