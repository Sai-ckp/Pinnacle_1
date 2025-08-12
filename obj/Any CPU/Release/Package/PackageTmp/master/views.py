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
from core.utils import log_activity

def blank_view(request):
    return render(request, 'master/blank.html')
 
from django.shortcuts import render, redirect
from .models import UserCustom
from license.models import License
from core.utils import log_activity

def custom_login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = UserCustom.objects.get(username=username)
            if user.is_locked:
                error = "User account is locked due to multiple wrong attempts. Please contact admin."
            elif user.password == password:
                user.wrong_attempts = 0
                user.save()
                request.session['user_id'] = user.id
                log_activity(user, 'login', user)
                
                if not user.passcode_set:
                    return redirect('choose_passcode_view')
                
                # Apply license logic only for user IDs 1 and 2
                if user.id in [1, 2]:
                    return handle_license_and_redirect(user, request)
                else:
                    # Role/ID based redirection
                    if user.id == 1:
                        return redirect('dashboard_view')
                    elif user.id == 2:
                        return redirect('dashboard_view2')
                    elif user.id ==5:
                        return redirect('dashboard_view3')
                    elif user.id == 6:
                        return redirect('dashboard_view4')            
                   
                
            else:
                user.wrong_attempts += 1
                if user.wrong_attempts >= 3:
                    user.is_locked = True
                user.save()
                if user.is_locked:
                    error = "Invalid password. Account locked after 3 wrong attempts. Please contact admin."
                else:
                    error = "Invalid password."
        except UserCustom.DoesNotExist:
            error = 'User does not exist'

    users = UserCustom.objects.all()
    return render(request, 'master/login.html', {'error': error, 'users': users})

 
from django.shortcuts import render, redirect
from .models import UserCustom
from license.models import License
from core.utils import log_activity
import json
from django.http import JsonResponse
import re

def handle_license_and_redirect(user, request):
    """Handles license logic and redirects to dashboard or license page."""
    try:
        license = License.objects.get(client_name=user.username, activated=True)
    except License.DoesNotExist:
        license = None

    if license and license.is_valid():
        request.session['license_valid'] = True
        request.session['license_end_date'] = license.end_date.isoformat()
        return redirect('dashboard')
    else:
        request.session['license_valid'] = False
        return redirect('license_check_view')

def choose_passcode_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('custom_login_view')
    try:
        user = UserCustom.objects.get(id=user_id)
    except UserCustom.DoesNotExist:
        return redirect('custom_login_view')

    if user.passcode_set:
        # Already set, proceed to license logic
        return handle_license_and_redirect(user, request)

    error = None
    if request.method == 'POST':
        passcode = request.POST.get('passcode', '')
        if len(passcode) < 4 or not passcode.isdigit():
            error = "Passcode must be at least 4 digits and contain only numbers."
        else:
            user.passcode = passcode
            user.passcode_set = True
            user.save()
            # After setting passcode, proceed to license logic
            return handle_license_and_redirect(user, request)

    return render(request, 'master/choose_passcode.html', {
        'user': user,
        'error': error
    })

def password_reset_view(request):
    error = None
    success_message = None
    stage = None
    username = request.POST.get('username') or request.GET.get('username')
    if request.method == 'POST':
        user = UserCustom.objects.filter(username=username).first()
        if not user:
            error = "User does not exist."
        elif 'new_password' not in request.POST:
            passcode = request.POST.get('passcode')
            if not user.passcode_set or user.passcode != passcode:
                error = "Passcode is incorrect. Please contact admin."
            else:
                stage = 'set_new_password'
        else:
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            pattern = r'^[A-Z][a-z]*[!@#$%^&*(),.?":{}|<>][a-zA-Z0-9]*[0-9]+$'
            if new_password != confirm_password:
                error = "Passwords do not match."
                stage = 'set_new_password'
            elif not re.match(pattern, new_password) or not (8 <= len(new_password) <= 16):
                error = "Invalid password format."
                stage = 'set_new_password'
            else:
                user.password = new_password
                user.save()
                success_message = "Password has been reset successfully."
    return render(request, 'master/password_reset.html', {
        'users': UserCustom.objects.all(),
        'username': username,
        'error': error,
        'success_message': success_message,
        'stage': stage,
    })

def verify_passcode_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        passcode = data.get("passcode")
        user = UserCustom.objects.filter(username=username).first()
        if user and user.passcode == passcode:
            return JsonResponse({'valid': True})
        return JsonResponse({'valid': False})









# views.py

import re
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from master.models import UserCustom  # adjust if model is elsewhere

def add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Username and password are required.")
        else:
            # Password format validation
            pattern = r'^[A-Z][a-z]*[!@#$%^&*(),.?":{}|<>][a-zA-Z0-9]*[0-9]+$'
            if not re.match(pattern, password) or not (8 <= len(password) <= 16):
                messages.error(request, "Invalid password format. Password must:\n"
                                        "- Start with a capital letter\n"
                                        "- Include a special character\n"
                                        "- End with a digit\n"
                                        "- Be 8-16 characters long.")
            else:
                try:
                    # Save user with hashed password
                    user_instance = UserCustom.objects.create(
                        username=username,
                        password=password
                    )

                    # Log activity
                    user = get_logged_in_user(request)
                    log_activity(user, 'created', user_instance)

                    messages.success(request, "User added successfully.")
                    return redirect('user_list')
                except Exception as e:
                    messages.error(request, f"Error adding user: {e}")

    return render(request, 'master/add_user.html')

 



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UserCustom
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UserCustom

def edit_user(request, user_id):
    user_instance = get_object_or_404(UserCustom, id=user_id)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        is_locked_str = request.POST.get('is_locked')

        if not username or not password:
            messages.error(request, "Username and password are required.")
        else:
            user_instance.username = username
            user_instance.password = password

            # Convert 'True'/'False' to boolean
            is_locked_new = True if is_locked_str == 'True' else False

            # If it was locked and now changed to unlocked, reset wrong_attempts
            if user_instance.is_locked and not is_locked_new:
                user_instance.wrong_attempts = 0

            user_instance.is_locked = is_locked_new

            user_instance.save()

            user = get_logged_in_user(request)
            log_activity(user, 'updated', user_instance)


            messages.success(request, "User updated successfully.")
            return redirect('user_list')

    return render(request, 'master/add_user.html', {
        'user_instance': user_instance,
        'action': 'edit'
    })

from django.shortcuts import render, get_object_or_404
from .models import UserCustom

def view_user(request, user_id):
    user_instance = get_object_or_404(UserCustom, id=user_id)
    
    return render(request, 'master/add_user.html', {
        'user_instance': user_instance,
        'action': 'view'
    })

from django.shortcuts import redirect
from django.contrib import messages

def delete_user(request, user_id):
    user1 = get_object_or_404(UserCustom, id=user_id)
    user1.delete()
    user = get_logged_in_user(request)
    log_activity(user, 'deleted', user1)
    messages.success(request, "User deleted successfully.")
    return redirect('user_list')





from django.shortcuts import render, redirect
from .models import UserCustom

def user_list(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            UserCustom.objects.create(username=username, password=password)
            return redirect('add_user')

    users = UserCustom.objects.all()
    return render(request, 'master/user_list.html', {'users': users})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UserCustom, UserPermission





def user_rights_view(request, user_id=None):
    # If no user selected, just show the user list
    all_users = UserCustom.objects.exclude(id=1)
   
    user = get_object_or_404(UserCustom, id=user_id)

    all_forms = [
        'course_type','course_form','semester_form','subject_form','transport_form','enquiry_form','schedule_follow_up_form','pu_admission_form','degree_admission_form','student_fee_form','communication_dashboard','student_database','employee_form','employee_attendance_form','student_attendance_form','timetable_form','calendar_form','recent_activity_view']
    form_display_names = {
    
    'employee_attendance_form':'Employee Attendance',
     'pu_admission_form': 'PU Application Form',
    'degree_admission_form': 'BCOM Application Form',
    'schedule_follow_up_form':'Schedule Enquiry Follow-Up ',
    'enquiry_form':'Enquiry Form',
    'student_attendance_form':'Student Attendance',
    'communication_dashboard':'Communication Dashboard',
    'semester_form':'Academic Cycle',
    'student_fee_form':'Fee Form',
    'timetable_form':'Timetable',
    'calendar_form':'Calendar',
    'student_database':'Student Information',
    'employee_form':'Employee',
    'course_type':'Program Types',
    'course_form':'Combinations',
    'subject_form':'Subjects',
    'transport_form':'Transport',
     'recent_activity_view':'Recent Activities'
}


    if request.method == 'POST':
        # Update or create permissions for each form
        for form in all_forms:
            perm, created = UserPermission.objects.get_or_create(user=user, form_name=form)
            if form in ['communication_dashboard', 'calendar_form','student_database','recent_activity_view']:
                perm.can_access = f"{form}_access" in request.POST
                # Optional: Clear other CRUD permissions
                perm.can_view = False
                perm.can_add = False
                perm.can_edit = False
                perm.can_delete = False
            else:
                perm.can_view = f"{form}_view" in request.POST
                perm.can_add = f"{form}_add" in request.POST
                perm.can_edit = f"{form}_edit" in request.POST
                perm.can_delete = f"{form}_delete" in request.POST
                perm.can_access = False
            
            perm.save()

        messages.success(request, f"Permissions updated for {user.username}.")
        return redirect('user_rights_view', user_id=user.id)


    # Build dict of permissions for template usage
    user_perms = UserPermission.objects.filter(user=user)
    perms = {}
    for perm in user_perms:
        perms[perm.form_name] = {
            'view': perm.can_view,
            'add': perm.can_add,
            'edit': perm.can_edit,
            'delete': perm.can_delete,
             'access': perm.can_access,
        }

    return render(request, 'master/user_rights.html', {
        'all_users': all_users,
        'selected_user': user,
        'all_forms': all_forms,
        'perms': perms,
        'form_display_names': form_display_names,  
    })


from django.shortcuts import render, redirect
from .models import Course, Subject , Semester
from .forms import SubjectForm
 
def subject_form_list(request):
    subjects = Subject.objects.select_related('course', 'faculty').all()
    return render(request, 'master/subject_list.html', {'subjects': subjects})
 
 

def subject_form_list(request):
    subjects = Subject.objects.select_related('course').all()
    return render(request, 'master/subject_list.html', {'subjects': subjects})
 
 

 
 


from django.shortcuts import render, redirect
from .forms import SubjectForm
from .models import  Subject
from master.models import Course  # Make sure to import Course



def subject_form_add(request):
    selected_course_id = None
    selected_semester = None
    selected_course_name = ""
    semesters = []

    if request.method == 'POST':
        selected_course_id = request.POST.get("course")
        selected_semester = request.POST.get("semester")

        post_data = request.POST.copy()

        if selected_course_id and selected_semester:
            try:
                course = Course.objects.get(id=selected_course_id)
                selected_course_name = course.name
                post_data['semester'] = selected_semester
                post_data['course'] = selected_course_id
            except Course.DoesNotExist:
                pass

        form = SubjectForm(post_data)

        if form.is_valid():
            subject_code = form.cleaned_data.get('subject_code')

            # ✅ Check for duplicate before saving
            if Subject.objects.filter(subject_code=subject_code).exists():
                form.add_error('subject_code', 'Subject code already exists.')
            else:
                try:
                    new_subject = form.save()
                    messages.success(request, f"Subject '{new_subject.name}' added successfully.")
                    return redirect('subject_form_list')
                except IntegrityError:
                    form.add_error('subject_code', 'Subject code already exists (DB check).')

    else:
        form = SubjectForm()

    if selected_course_id:
        try:
            course = Course.objects.get(id=selected_course_id)
            selected_course_name = course.name
            if course.total_semesters:
                semesters = [{'number': i, 'name': f"Semester {i}"} for i in range(1, course.total_semesters + 1)]
        except Course.DoesNotExist:
            pass

    return render(request, 'master/add_subject.html', {
        'form': form,
        'semesters': semesters,
        'selected_course_id': selected_course_id,
        'selected_course_name': selected_course_name,
        'is_view': False
    })

from django.http import JsonResponse
from .models import Course

from django.http import JsonResponse
from .models import Course

def get_semesters_by_course(request):
    if request.method == "POST":
        course_id = request.POST.get("course_id")
        try:
            course = Course.objects.get(id=course_id)
            semester_list = []

            course_type_name = course.course_type.name.strip().lower()

            if course_type_name == "puc regular":
                # Use duration_years as the number of semesters for PUC Regular
                total = course.duration_years or 0
                for i in range(1, total + 1):
                    semester_list.append({
                        'number': i,
                        'name': f"{course.name} {i}"
                    })
            else:
                # Use total_semesters for other course types
                total = course.total_semesters or 0
                for i in range(1, total + 1):
                    semester_list.append({
                        'number': i,
                        'name': f"{course.name} {i}"
                    })

            if not semester_list:
                semester_list.append({
                    'number': 0,
                    'name': "NOT APPLICABLE"
                })

            return JsonResponse({'semesters': semester_list})

        except Course.DoesNotExist:
            return JsonResponse({'error': 'Invalid course ID'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


from django.shortcuts import render, get_object_or_404
from .models import Subject
from .forms import SubjectForm
from django import forms


def subject_form_view(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    form = SubjectForm(instance=subject)

    for field in form.fields.values():
        field.disabled = True
        field.widget.attrs['readonly'] = True
        field.widget.attrs['class'] = 'form-control'

    # Manually set dropdown fields to plain text
    form.fields['course'].widget = forms.TextInput(attrs={
        'readonly': True,
        'class': 'form-control'
    })
    form.fields['course'].initial = subject.course.name

    form.fields['semester'].widget = forms.TextInput(attrs={
        'readonly': True,
        'class': 'form-control'
    })
    form.fields['semester'].initial = subject.semester

    return render(request, 'master/add_subject.html', {
        'form': form,
        'semesters': [],  # Not needed in view
        'selected_course_id': subject.course.id,
        'selected_course_name': subject.course.name,
        'selected_semester': subject.semester,
        'is_view': True
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Subject
from .forms import SubjectForm
from master.models import Course
from core.utils import get_logged_in_user, log_activity
 
def subject_form_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)

    if request.method == 'POST':
        selected_course_id = int(request.POST.get('course', subject.course.id))
        selected_semester_number = request.POST.get('semester', '')
        form = SubjectForm(request.POST, instance=subject)
    else:
        selected_course_id = subject.course.id

        # Extract semester number
        if isinstance(subject.semester, int):
            selected_semester_number = str(subject.semester)
        elif isinstance(subject.semester, str):
            parts = subject.semester.strip().split()
            if parts and parts[-1].isdigit():
                selected_semester_number = parts[-1]
            else:
                selected_semester_number = ""
        else:
            selected_semester_number = ""

        form = SubjectForm(instance=subject)
        form.initial['semester'] = selected_semester_number

    # Build semester options for dropdown
    semesters = []
    try:
        course = Course.objects.get(id=selected_course_id)
        if course.total_semesters:
            semesters = [{'number': str(i), 'name': f"{course.name} Semester {i}"} for i in range(1, course.total_semesters + 1)]
    except Course.DoesNotExist:
        pass

    # Set dropdown choices with display names but values as numbers
    form.fields['semester'].choices = [(s['number'], s['name']) for s in semesters]

    if request.method == 'POST' and form.is_valid():
        updated = form.save(commit=False)
        try:
            # ✅ Check for duplicate subject code excluding current subject
            subject_code = form.cleaned_data.get('subject_code')
            if Subject.objects.exclude(pk=pk).filter(subject_code=subject_code).exists():
                form.add_error('subject_code', 'Subject code already exists.')
            else:
                updated.semester = int(selected_semester_number)  # ✅ Store integer in DB
                updated.save()

                log_activity(get_logged_in_user(request), 'updated', updated)
                messages.success(request, f"Subject '{updated.name}' updated successfully.")  # ✅ Snackbar with subject name
                return redirect('subject_form_list')

        except ValueError:
            messages.error(request, "Invalid semester number.")
        except Course.DoesNotExist:
            messages.error(request, "Selected course does not exist.")

    return render(request, 'master/add_subject.html', {
        'form': form,
        'semesters': semesters,
        'selected_course_id': selected_course_id,
        'selected_semester': selected_semester_number,
        'selected_course_name': subject.course.name,
        'is_view': False,
    })




def subject_form_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    subject_name = subject.name  # Save name before deleting
    subject.delete()

    user = get_logged_in_user(request)
    log_activity(user, 'deleted', subject)

    messages.success(request, f"Subject '{subject_name}' deleted successfully.")
    return redirect('subject_form_list')






# from django.http import JsonResponse
# from .models import Employee

# def get_faculties_by_subject(request):
#     subject_name = request.GET.get('name', '').strip()
#     faculties = Employee.objects.filter(department__iexact=subject_name)
#     data = [{'id': f.id, 'name': f.name} for f in faculties]
#     return JsonResponse({'faculties': data})
 




@login_required
def dashboard_view(request):
    return render(request, 'master/dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')




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
from django.utils import timezone
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from core.models import RecentActivity
from master.models import Notification
from django.db.models import DateField
from datetime import datetime, timedelta
import calendar

from admission.models import (
    Enquiry1, Enquiry2, PUAdmission, DegreeAdmission,
    Student as AdmissionStudent, Student
)


from fees.models import StudentFeeCollection



def dashboard_view(request):
    filter_type = request.GET.get('filter', 'all')
    sections = request.GET.getlist('sections')

    if not sections:
        sections = [
            'students', 'enquiries', 'admissions',
            'messages', 'faculties', 'fees',
            'student_attendance', 'faculty_attendance'
        ]

   
    now = timezone.now()
    today = now.date()
    today = datetime.today()
    end_date = None

    if filter_type == 'day':
        start_date = today
        end_date = today
    elif filter_type == 'week':
            start_date = today - timedelta(days=today.weekday())  # Monday
            end_date = start_date + timedelta(days=6)  # Sunday
    elif filter_type == 'month':
            start_date = today.replace(day=1)
            last_day = calendar.monthrange(today.year, today.month)[1]
            end_date = today.replace(day=last_day)
    elif filter_type == 'year':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
    else:
            start_date = None
            end_date = None

    # Initialize QuerySets
    pu_admission_qs = PUAdmission.objects.none()
    degree_admission_qs = DegreeAdmission.objects.none()
    enquiry1_qs = Enquiry1.objects.none()
    enquiry2_qs = Enquiry2.objects.none()
    enquiry1_whatsapp_qs = Enquiry1.objects.none()
    enquiry2_whatsapp_qs = Enquiry2.objects.none()
    sentmessage_qs = SentMessageContact.objects.none()
    student_qs = Student.objects.none()
    employee_qs = Employee.objects.none()
    faculty_attendance_qs = attendance.objects.none()
    student_attendance_qs = StudentAttendance.objects.none()

    if 'students' in sections or 'fees' in sections:
        student_qs = Student.objects.all()
        if start_date:
            student_qs = student_qs.filter(receipt_date__gte=start_date)

    if 'students' in sections:
        pu_admission_qs = PUAdmission.objects.filter(status='confirmed')
        degree_admission_qs = DegreeAdmission.objects.filter(status='confirmed')
        if start_date:
            pu_admission_qs = pu_admission_qs.filter(admission_date__gte=start_date)
            degree_admission_qs = degree_admission_qs.filter(admission_date__gte=start_date)

    # Fees Section
    total_declared_fee = total_collected_fee = total_pending_fees = Decimal('0.00')
    if 'fees' in sections:
        decimal_type = DecimalField(max_digits=12, decimal_places=2)

        declared_expr = ExpressionWrapper(
            Coalesce(F('tuition_fee'), 0) +
            Coalesce(F('transport_fee'), 0) +
            Coalesce(F('hostel_fee'), 0) +
            Coalesce(F('books_fee'), 0) +
            Coalesce(F('uniform_fee'), 0) +
            Coalesce(F('other_fee'), 0),
            output_field=decimal_type
        )
        collected_expr = ExpressionWrapper(
            Coalesce(F('tuition_fee_paid'), 0) +
            Coalesce(F('transport_fee_paid'), 0) +
            Coalesce(F('hostel_fee_paid'), 0) +
            Coalesce(F('books_fee_paid'), 0) +
            Coalesce(F('uniform_fee_paid'), 0) +
            Coalesce(F('other_amount'), 0),
            output_field=decimal_type
        )
        pending_expr = ExpressionWrapper(
            Coalesce(F('tuition_pending_fee'), 0) +
            Coalesce(F('transport_pending_fee'), 0) +
            Coalesce(F('hostel_pending_fee'), 0) +
            Coalesce(F('books_pending_fee'), 0) +
            Coalesce(F('uniform_pending_fee'), 0),
            output_field=decimal_type
        )

        total_declared_fee = student_qs.aggregate(total=Sum(declared_expr))['total'] or 0
        total_collected_fee = student_qs.aggregate(total=Sum(collected_expr))['total'] or 0
        total_pending_fees = student_qs.aggregate(total=Sum(pending_expr))['total'] or 0

    if 'enquiries' in sections:
        enquiry1_qs = Enquiry1.objects.all()
        enquiry2_qs = Enquiry2.objects.all()
        if start_date:
            enquiry1_qs = enquiry1_qs.filter(enquiry_date__gte=start_date)
            enquiry2_qs = enquiry2_qs.filter(enquiry_date__gte=start_date)









    if 'messages' in sections:
        enquiry1_whatsapp_qs = Enquiry1.objects.filter(whatsapp_status='sent')
        enquiry2_whatsapp_qs = Enquiry2.objects.filter(whatsapp_status='sent')
        sentmessage_qs = SentMessageContact.objects.filter(status='Sent')
        if start_date:
            enquiry1_whatsapp_qs = enquiry1_whatsapp_qs.filter(whatsapp_sent_date__gte=start_date)
            enquiry2_whatsapp_qs = enquiry2_whatsapp_qs.filter(whatsapp_sent_date__gte=start_date)
            sentmessage_qs = sentmessage_qs.filter(sent_date__gte=start_date)

   
    if 'faculties' in sections:
        employee_qs = Employee.objects.all()
        if start_date:
            employee_qs = employee_qs.filter(created_at__gte=start_date)
            
    total_staff = Employee.objects.count()
    
     
    faculty_qs = attendance.objects.all()
    if start_date and end_date:
        faculty_qs = faculty_qs.filter(date__range=(start_date, end_date))
    elif start_date:
        faculty_qs = faculty_qs.filter(date=start_date)

    total_staff = Employee.objects.count()
    staff_present = faculty_qs.filter(status='Present').count()
    staff_late = faculty_qs.filter(status='Late').count()
    staff_absent = total_staff - (staff_present + staff_late)
    faculty_attendance_rate = round(((staff_present + staff_late) / total_staff) * 100, 1) if total_staff else 0

    # Student Attendance
    student_qs = StudentAttendance.objects.all()
    if start_date and end_date:
        student_qs = student_qs.filter(attendance_date__range=(start_date, end_date))
    elif start_date:
        student_qs = student_qs.filter(attendance_date=start_date)

    total_students_db = StudentDatabase.objects.count()
    student_present_ids = set(student_qs.filter(status__iexact='present').values_list('student_id', flat=True))
    student_late_ids = set(student_qs.filter(status__iexact='late').values_list('student_id', flat=True))
    student_absent_ids = set(student_qs.filter(status__iexact='absent').values_list('student_id', flat=True))

    student_present = len(student_present_ids)
    student_late = len(student_late_ids)
    student_absent = len(student_absent_ids)
    student_attendance_rate = round(((student_present + student_late) / total_students_db) * 100, 1) if total_students_db else 0

    recent_activities = RecentActivity.objects.select_related('user').order_by('-timestamp')[:5]


    #fees
    total_expected = StudentFeeCollection.objects.aggregate(total=Sum('amount'))['total'] or 0
 
# Total collected = sum of paid_amount
    total_collected = StudentFeeCollection.objects.aggregate(collected=Sum('paid_amount'))['collected'] or 0
 
# Pending payments = sum of balance_amount
    pending_amount = StudentFeeCollection.objects.aggregate(pending=Sum('balance_amount'))['pending'] or 0
 
 
    total_fees=total_collected+pending_amount
 
# Count of students with pending fees
    pending_students = StudentFeeCollection.objects.filter(Q(status='Pending') | Q(status='Partial')).values('student_userid').distinct().count()
 
 





    # Stats
    total_pu_students = pu_admission_qs.count()
    total_degree_students = degree_admission_qs.count()
    total_students = total_pu_students + total_degree_students

    total_pu_enquiries = enquiry1_qs.count()
    total_degree_enquiries = enquiry2_qs.count()
    total_enquiries = total_pu_enquiries + total_degree_enquiries

    enquiries_whatsapp_sent = enquiry1_whatsapp_qs.count() + enquiry2_whatsapp_qs.count()
    admission_messages_sent = sentmessage_qs.count()
    total_messages_sent = enquiries_whatsapp_sent + admission_messages_sent

    pending_messages = 0
 
    if 'messages' in sections:
        pending_enquiry1_qs = Enquiry1.objects.filter(whatsapp_status='pending')
        pending_enquiry2_qs = Enquiry2.objects.filter(whatsapp_status='pending')
        pending_sentmessage_qs = SentMessageContact.objects.filter(status='Pending')
 
        if start_date:
            pending_enquiry1_qs = pending_enquiry1_qs.filter(whatsapp_sent_date__gte=start_date)
            pending_enquiry2_qs = pending_enquiry2_qs.filter(whatsapp_sent_date__gte=start_date)
            pending_sentmessage_qs = pending_sentmessage_qs.filter(sent_date__gte=start_date)
 
        pending_messages = (
            pending_enquiry1_qs.count() +
            pending_enquiry2_qs.count() +
            pending_sentmessage_qs.count()
        )

    total_employees = employee_qs.count()
    faculty_designations = ['Professor', 'Associate Professor', 'Assistant Professor']
    total_faculties = employee_qs.filter(designation__in=faculty_designations).count()

    # faculty_attendance_rate = 0
    # if faculty_attendance_qs.exists():
    #     present_faculty = faculty_attendance_qs.filter(status__in=['Present', 'Late']).count()
    #     faculty_attendance_rate = round((present_faculty / faculty_attendance_qs.count()) * 100, 2)

    # student_attendance_rate = 0
    # if student_attendance_qs.exists():
    #     present_student = student_attendance_qs.filter(status__in=['present', 'late']).count()
    #     student_attendance_rate = round((present_student / student_attendance_qs.count()) * 100, 2)

    recent_activities = RecentActivity.objects.select_related('user').order_by('-timestamp')[:5]
    # 🚨 Promotion Notifications for PU and Degree Students older than 15 days
    forty_eight_hours_ago = timezone.now() - timedelta(hours=48)

    # Define notification list
    unread_notifications = []

    # Collect pending PU and Degree admissions
    pending_pu_admissions = PUAdmission.objects.filter(status='pending', admission_date__lte=forty_eight_hours_ago)
    pending_degree_admissions = DegreeAdmission.objects.filter(status='pending', admission_date__lte=forty_eight_hours_ago)

    for admission in pending_pu_admissions:
        unread_notifications.append({
            'user': request.user,
            'message': f"Pending PU admission for {getattr(admission, 'student_name', 'Unknown Student')}",
            'timestamp': datetime.combine(admission.admission_date, time.min),
            'link': '/admissions/pu/pending/'
        })

    for admission in pending_degree_admissions:     
        unread_notifications.append({
            'user': request.user,
            'message': f"Pending Degree admission for {getattr(admission, 'student_name', 'Unknown Student')}",
            'timestamp': datetime.combine(admission.admission_date, time.min),
            'link': '/admissions/degree/pending/'
        })

    # Sort and count
    unread_notifications.sort(key=lambda x: x['timestamp'], reverse=True)
    notification_count = len(unread_notifications)

    context = {
        # Student Stats
        'total_students': total_students if 'students' in sections else 0,
        'total_pu_students': total_pu_students if 'students' in sections else 0,
        'total_degree_students': total_degree_students if 'students' in sections else 0,

        # Enquiry Stats
        'total_enquiries': total_enquiries if 'enquiries' in sections else 0,
        'total_pu_enquiries': total_pu_enquiries if 'enquiries' in sections else 0,
        'total_degree_enquiries': total_degree_enquiries if 'enquiries' in sections else 0,

        # Messaging Stats
        'total_messages_sent': total_messages_sent if 'messages' in sections else 0,
        'enquiries_whatsapp_sent': enquiries_whatsapp_sent if 'messages' in sections else 0,
        'admission_messages_sent': admission_messages_sent if 'messages' in sections else 0,
        'pending_messages': pending_messages if 'messages' in sections else 0,

        # Fees Stats



        'total_collected': total_collected,
        'pending_amount': pending_amount,
        'total_fees':total_fees,
        # 'total_collected_fee': total_collected_fee if 'fees' in sections else 0,
        # 'total_declared_fee': total_declared_fee if 'fees' in sections else 0,
        # 'total_pending_fees': total_pending_fees if 'fees' in sections else 0,

        # Faculty & Staff Stats
        'total_employees': total_employees if 'faculties' in sections else 0,
        'total_faculties': total_faculties if 'faculties' in sections else 0,
        'staff_present': staff_present if 'faculty_attendance' in sections else 0,
        'staff_late': staff_late if 'faculty_attendance' in sections else 0,
        'staff_absent': staff_absent if 'faculty_attendance' in sections else 0,
        'faculty_attendance_rate': round(faculty_attendance_rate, 1) if 'faculty_attendance' in sections else 0,

        # Student Attendance Stats
        'student_present': len(student_present_ids) if 'student_attendance' in sections else 0,
        'student_late': len(student_late_ids) if 'student_attendance' in sections else 0,
        'student_absent': len(student_absent_ids) if 'student_attendance' in sections else 0,
        'student_attendance_rate': round(student_attendance_rate, 1) if 'student_attendance' in sections else 0,

        # Misc
        'filter_type': filter_type,
        'selected_sections': request.GET.getlist('sections') if 'sections' in request.GET else [],
        'should_show_cards': bool(sections),
        'recent_activities': recent_activities,
        'unread_notifications': unread_notifications,
        'notification_count': notification_count,
    }

    return render(request, 'master/dashboard.html', context)







from django.shortcuts import render
from django.utils import timezone
import datetime
from decimal import Decimal
from django.db.models import Sum, F, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.db.models import DecimalField

from admission.models import PUAdmission, DegreeAdmission, Enquiry1, Enquiry2
from admission.models import Student
from master.models import Employee 
from attendence.models import attendance, StudentAttendance
from master.models import SentMessageContact
from core.models import RecentActivity
from master.models import Notification
from datetime import timedelta
import datetime

import datetime
from datetime import timedelta
from django.utils import timezone
from django.db.models import F, CharField, DateField
from django.db.models.functions import Coalesce, Cast
from django.urls import reverse
from datetime import datetime, time, timedelta
from datetime import datetime, timedelta
import calendar

def dashboard_view2(request):
    filter_type = request.GET.get('filter', 'all')
    sections = request.GET.getlist('sections')

    if not sections:
        sections = [
            'students', 'enquiries', 'admissions',
            'messages', 'faculties',
            'student_attendance', 'faculty_attendance'
        ]

    now = timezone.now()
    today = now.date()
    today = datetime.today()
    end_date = None

    if filter_type == 'day':
        start_date = today
        end_date = today
    elif filter_type == 'week':
            start_date = today - timedelta(days=today.weekday())  # Monday
            end_date = start_date + timedelta(days=6)  # Sunday
    elif filter_type == 'month':
            start_date = today.replace(day=1)
            last_day = calendar.monthrange(today.year, today.month)[1]
            end_date = today.replace(day=last_day)
    elif filter_type == 'year':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
    else:
            start_date = None
            end_date = None


    # Initialize QuerySets
    pu_admission_qs = PUAdmission.objects.none()
    degree_admission_qs = DegreeAdmission.objects.none()
    enquiry1_qs = Enquiry1.objects.none()
    enquiry2_qs = Enquiry2.objects.none()
    enquiry1_whatsapp_qs = Enquiry1.objects.none()
    enquiry2_whatsapp_qs = Enquiry2.objects.none()
    sentmessage_qs = SentMessageContact.objects.none()
    student_qs = Student.objects.none()
    employee_qs = Employee.objects.none()
    faculty_attendance_qs = attendance.objects.none()
    student_attendance_qs = StudentAttendance.objects.none()

    # Students Section
    if 'students' in sections or 'fees' in sections:
        student_qs = Student.objects.all()
        if start_date:
            student_qs = student_qs.filter(receipt_date__gte=start_date)

    if 'students' in sections:
        pu_admission_qs = PUAdmission.objects.filter(status='confirmed')
        degree_admission_qs = DegreeAdmission.objects.filter(status='confirmed')
        if start_date:
            pu_admission_qs = pu_admission_qs.filter(admission_date__gte=start_date)
            degree_admission_qs = degree_admission_qs.filter(admission_date__gte=start_date)

    # Enquiries Section
    if 'enquiries' in sections:
        enquiry1_qs = Enquiry1.objects.all()
        enquiry2_qs = Enquiry2.objects.all()
        if start_date:
            enquiry1_qs = enquiry1_qs.filter(enquiry_date__gte=start_date)
            enquiry2_qs = enquiry2_qs.filter(enquiry_date__gte=start_date)

    # Messages Section
    if 'messages' in sections:
        enquiry1_whatsapp_qs = Enquiry1.objects.filter(whatsapp_status='sent')
        enquiry2_whatsapp_qs = Enquiry2.objects.filter(whatsapp_status='sent')
        sentmessage_qs = SentMessageContact.objects.filter(status='Sent')
        if start_date:
            enquiry1_whatsapp_qs = enquiry1_whatsapp_qs.filter(whatsapp_sent_date__gte=start_date)
            enquiry2_whatsapp_qs = enquiry2_whatsapp_qs.filter(whatsapp_sent_date__gte=start_date)
            sentmessage_qs = sentmessage_qs.filter(sent_date__gte=start_date)

  
    if 'faculties' in sections:
        employee_qs = Employee.objects.all()
        if start_date:
            employee_qs = employee_qs.filter(created_at__gte=start_date)
            
    total_staff = Employee.objects.count()
    
     
    faculty_qs = attendance.objects.all()
    if start_date and end_date:
        faculty_qs = faculty_qs.filter(date__range=(start_date, end_date))
    elif start_date:
        faculty_qs = faculty_qs.filter(date=start_date)

    total_staff = Employee.objects.count()
    staff_present = faculty_qs.filter(status='Present').count()
    staff_late = faculty_qs.filter(status='Late').count()
    staff_absent = total_staff - (staff_present + staff_late)
    faculty_attendance_rate = round(((staff_present + staff_late) / total_staff) * 100, 1) if total_staff else 0

    # Student Attendance
    student_qs = StudentAttendance.objects.all()
    if start_date and end_date:
        student_qs = student_qs.filter(attendance_date__range=(start_date, end_date))
    elif start_date:
        student_qs = student_qs.filter(attendance_date=start_date)

    total_students_db = StudentDatabase.objects.count()
    student_present_ids = set(student_qs.filter(status__iexact='present').values_list('student_id', flat=True))
    student_late_ids = set(student_qs.filter(status__iexact='late').values_list('student_id', flat=True))
    student_absent_ids = set(student_qs.filter(status__iexact='absent').values_list('student_id', flat=True))

    student_present = len(student_present_ids)
    student_late = len(student_late_ids)
    student_absent = len(student_absent_ids)
    student_attendance_rate = round(((student_present + student_late) / total_students_db) * 100, 1) if total_students_db else 0


    # Stats
    total_pu_students = pu_admission_qs.count()
    total_degree_students = degree_admission_qs.count()
    total_students = total_pu_students + total_degree_students

    total_pu_enquiries = enquiry1_qs.count()
    total_degree_enquiries = enquiry2_qs.count()
    total_enquiries = total_pu_enquiries + total_degree_enquiries

    enquiries_whatsapp_sent = enquiry1_whatsapp_qs.count() + enquiry2_whatsapp_qs.count()
    admission_messages_sent = sentmessage_qs.count()
    total_messages_sent = enquiries_whatsapp_sent + admission_messages_sent

    pending_messages = 0
    if 'messages' in sections:
        pending_enquiry1_qs = Enquiry1.objects.filter(whatsapp_status='pending')
        pending_enquiry2_qs = Enquiry2.objects.filter(whatsapp_status='pending')
        pending_sentmessage_qs = SentMessageContact.objects.filter(status='Pending')

        if start_date:
            pending_enquiry1_qs = pending_enquiry1_qs.filter(whatsapp_sent_date__gte=start_date)
            pending_enquiry2_qs = pending_enquiry2_qs.filter(whatsapp_sent_date__gte=start_date)
            pending_sentmessage_qs = pending_sentmessage_qs.filter(sent_date__gte=start_date)

        pending_messages = (
            pending_enquiry1_qs.count() +
            pending_enquiry2_qs.count() +
            pending_sentmessage_qs.count()
        )

    total_employees = employee_qs.count()
    faculty_designations = ['Professor', 'Associate Professor', 'Assistant Professor']
    total_faculties = employee_qs.filter(designation__in=faculty_designations).count()


    # 🚨 Notifications Section - Pending admissions older than 48 hours
    forty_eight_hours_ago = timezone.now() - timedelta(hours=48)

    pending_pu_admissions = PUAdmission.objects.filter(
        status='pending',
        admission_date__lte=forty_eight_hours_ago
    )

    pending_degree_admissions = DegreeAdmission.objects.filter(
        status='pending',
        admission_date__lte=forty_eight_hours_ago
    )

    unread_notifications = []

    for admission in pending_pu_admissions:
        unread_notifications.append({
            'user': request.user,
            'message': f"Pending PU admission for {getattr(admission, 'student_name', 'Unknown Student')}",
            'timestamp': datetime.combine(admission.admission_date, time.min),

            'link': reverse('pending_admissions')  # replace with your actual URL name

        })

    for admission in pending_degree_admissions:
        unread_notifications.append({
            'user': request.user,
            'message': f"Pending Degree admission for {getattr(admission, 'student_name', 'Unknown Student')}",
            'timestamp': datetime.combine(admission.admission_date, time.min),

            'link': reverse('pending_admissions')

        })

    # 🚨 Promotion Notifications
    ten_days_ago = timezone.now().date() - timedelta(days=10)

    students_with_admission_dates = StudentDatabase.objects.annotate(
        admission_date=Coalesce(
            Cast('pu_admission__admission_date', DateField()),
            Cast('degree_admission__admission_date', DateField()),
            output_field=DateField()
        ),
        admission_number=Coalesce(
            F('pu_admission__admission_no'),
            F('degree_admission__admission_no'),
            output_field=CharField()
        )
    ).filter(
        admission_date__lte=ten_days_ago,
    )

    for student in students_with_admission_dates:
        if student.pu_admission_id and student.pu_admission:
            name = student.pu_admission.student_name
            program_type = "PU"
        elif student.degree_admission_id and student.degree_admission:
            name = student.degree_admission.student_name
            program_type = "Degree"
        else:
            continue

        message = f"{program_type} promotion pending for {name} (admitted {student.admission_date.strftime('%b %d, %Y')})"

        unread_notifications.append({
            'user': request.user,
            'message': message,
            'timestamp': datetime.combine(student.admission_date, time.min),

            'link': reverse('student_database')
        })

    unread_notifications.sort(key=lambda x: x['timestamp'], reverse=True)
    notification_count = len(unread_notifications)

    context = {
        # Student Stats
        'total_students': total_students if 'students' in sections else 0,
        'total_pu_students': total_pu_students if 'students' in sections else 0,
        'total_degree_students': total_degree_students if 'students' in sections else 0,

        # Enquiry Stats
        'total_enquiries': total_enquiries if 'enquiries' in sections else 0,
        'total_pu_enquiries': total_pu_enquiries if 'enquiries' in sections else 0,
        'total_degree_enquiries': total_degree_enquiries if 'enquiries' in sections else 0,

        # Messaging Stats
        'total_messages_sent': total_messages_sent if 'messages' in sections else 0,
        'enquiries_whatsapp_sent': enquiries_whatsapp_sent if 'messages' in sections else 0,
        'admission_messages_sent': admission_messages_sent if 'messages' in sections else 0,
        'pending_messages': pending_messages if 'messages' in sections else 0,

   

        # Faculty & Staff Stats
        'total_employees': total_employees if 'faculties' in sections else 0,
        'total_faculties': total_faculties if 'faculties' in sections else 0,
        'staff_present': staff_present if 'faculty_attendance' in sections else 0,
        'staff_late': staff_late if 'faculty_attendance' in sections else 0,
        'staff_absent': staff_absent if 'faculty_attendance' in sections else 0,
        'faculty_attendance_rate': round(faculty_attendance_rate, 1) if 'faculty_attendance' in sections else 0,

        # Student Attendance Stats
        'student_present': len(student_present_ids) if 'student_attendance' in sections else 0,
        'student_late': len(student_late_ids) if 'student_attendance' in sections else 0,
        'student_absent': len(student_absent_ids) if 'student_attendance' in sections else 0,
        'student_attendance_rate': round(student_attendance_rate, 1) if 'student_attendance' in sections else 0,

        # Misc
        'filter_type': filter_type,
        'selected_sections': request.GET.getlist('sections') if 'sections' in request.GET else [],
        'should_show_cards': bool(sections),
        'unread_notifications': unread_notifications,
        'notification_count': notification_count,
    }

    return render(request, 'master/dashboard2.html', context)

from datetime import timedelta
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce

from admission.models import (
    PUAdmission, DegreeAdmission,
    Enquiry1, Enquiry2,
    Student,
)


def dashboard_view3(request):
    user_role = getattr(request.user, 'role', None)
    filter_type = request.GET.get('filter', 'all')
    sections = request.GET.getlist('sections')
    if not sections:
        sections = ['students', 'enquiries', 'fees', 'pending_admissions']

    now = timezone.now()
    today = now.date()

    # Determine start_date based on filter
    if filter_type == 'day':
        start_date = today
    elif filter_type == 'week':
        start_date = today - timedelta(days=today.weekday())
    elif filter_type == 'month':
        start_date = today.replace(day=1)
    elif filter_type == 'year':
        start_date = today.replace(month=1, day=1)
    else:
        start_date = None

    # Base querysets
    pu_adm_confirmed = PUAdmission.objects.filter(status='confirmed')
    deg_adm_confirmed = DegreeAdmission.objects.filter(status='confirmed')
    pu_adm_pending = PUAdmission.objects.filter(status='pending')
    deg_adm_pending = DegreeAdmission.objects.filter(status='pending')
    enqu1 = Enquiry1.objects.all()
    enqu2 = Enquiry2.objects.all()
    students = Student.objects.all()

    # Apply date filters correctly to each section
    if start_date:
        if 'students' in sections:
            pu_adm_confirmed = pu_adm_confirmed.filter(admission_date__gte=start_date)
            deg_adm_confirmed = deg_adm_confirmed.filter(admission_date__gte=start_date)
            students = students.filter(receipt_date__gte=start_date)

        if 'pending_admissions' in sections:
            pu_adm_pending = pu_adm_pending.filter(admission_date__gte=start_date)
            deg_adm_pending = deg_adm_pending.filter(admission_date__gte=start_date)

        if 'enquiries' in sections:
            enqu1 = enqu1.filter(enquiry_date__gte=start_date)
            enqu2 = enqu2.filter(enquiry_date__gte=start_date)

        if 'fees' in sections:
            students = students.filter(receipt_date__gte=start_date)

    # Counts
    total_pu_students = pu_adm_confirmed.count()
    total_deg_students = deg_adm_confirmed.count()
    total_students = total_pu_students + total_deg_students

    total_pu_enquiries = enqu1.count()
    total_deg_enquiries = enqu2.count()
    total_enquiries = total_pu_enquiries + total_deg_enquiries

    total_pu_pending_adm = pu_adm_pending.count()
    total_deg_pending_adm = deg_adm_pending.count()
    total_pending_admissions = total_pu_pending_adm + total_deg_pending_adm

    # Fees – apply only if allowed
    if user_role != 'Academic Director' and ('fees' in sections or 'all' in sections):
        expr_declared = ExpressionWrapper(
            Coalesce(F('tuition_fee'), 0) + Coalesce(F('transport_fee'), 0)
            + Coalesce(F('hostel_fee'), 0) + Coalesce(F('books_fee'), 0)
            + Coalesce(F('uniform_fee'), 0) + Coalesce(F('other_fee'), 0),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
        expr_collected = ExpressionWrapper(
            Coalesce(F('tuition_fee_paid'), 0) + Coalesce(F('transport_fee_paid'), 0)
            + Coalesce(F('hostel_fee_paid'), 0) + Coalesce(F('books_fee_paid'), 0)
            + Coalesce(F('uniform_fee_paid'), 0) + Coalesce(F('other_amount'), 0),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
        expr_pending = ExpressionWrapper(
            Coalesce(F('tuition_pending_fee'), 0) + Coalesce(F('transport_pending_fee'), 0)
            + Coalesce(F('hostel_pending_fee'), 0) + Coalesce(F('books_pending_fee'), 0)
            + Coalesce(F('uniform_pending_fee'), 0),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
        total_declared_fee = students.aggregate(total=Sum(expr_declared))['total'] or 0
        total_collected_fee = students.aggregate(total=Sum(expr_collected))['total'] or 0
        total_pending_fees = students.aggregate(total=Sum(expr_pending))['total'] or 0
    else:
        total_declared_fee = total_collected_fee = total_pending_fees = None

    # Alerts for 10‑minute pending
    pending_10_pu = []
    pending_10_deg = []
    if user_role == 'Front Office':
        ts_10 = timezone.now() - timedelta(minutes=10)
        pending_10_pu = PUAdmission.objects.filter(status='pending', admission_date__lte=ts_10)
        pending_10_deg = DegreeAdmission.objects.filter(status='pending', admission_date__lte=ts_10)

    # Alerts for 24‑hour pending
    ts_24 = timezone.now() - timedelta(hours=24)
    pending_24_pu = PUAdmission.objects.filter(status='pending', admission_date__lte=ts_24)
    pending_24_deg = DegreeAdmission.objects.filter(status='pending', admission_date__lte=ts_24)
    show_24hr_warning = pending_24_pu.exists() or pending_24_deg.exists()

    context = {
        # Student stats
        'total_students': total_students if 'students' in sections else 0,
        'total_pu_students': total_pu_students if 'students' in sections else 0,
        'total_degree_students': total_deg_students if 'students' in sections else 0,

        # Enquiry stats
        'total_enquiries': total_enquiries if 'enquiries' in sections else 0,
        'total_pu_enquiries': total_pu_enquiries if 'enquiries' in sections else 0,
        'total_degree_enquiries': total_deg_enquiries if 'enquiries' in sections else 0,

        # Pending admissions (match frontend naming)
        'total_pending_admissions': total_pending_admissions if 'pending_admissions' in sections else 0,
        'total_pu_pending_admissions': total_pu_pending_adm if 'pending_admissions' in sections else 0,
        'total_pending_pu_admissions': total_pu_pending_adm if 'pending_admissions' in sections else 0,
        'total_pending_degree_admissions': total_deg_pending_adm if 'pending_admissions' in sections else 0,

        # Fees
        'total_declared_fee': total_declared_fee,
        'total_collected_fee': total_collected_fee,
        'total_pending_fees': total_pending_fees,

        # Alerts
        'pending_alert_pu': pending_10_pu,
        'pending_alert_degree': pending_10_deg,
        'show_24hr_warning': show_24hr_warning,
        'pending_24hr_pu': pending_24_pu,
        'pending_24hr_degree': pending_24_deg,

        # UI state
        'filter_type': filter_type,
        'selected_sections': sections,
    }
    return render(request, 'master/dashboard3.html', context)




from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, F, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.db.models import DecimalField
import datetime
from admission.models import PUAdmission, DegreeAdmission, Enquiry1, Enquiry2, Student



def dashboard_view4(request):
    user_role = getattr(request.user, 'role', None)  # ✅ Get user role
    filter_type = request.GET.get('filter', 'all')
    sections = request.GET.getlist('sections')  # ✅ Corrected to get a list of sections

    if not sections:
        sections = ['student_attendance']

    # Get current date/time
    now = timezone.now()
    today = now.date()
    end_date = None

    # Apply filter type to calculate date range
    if filter_type == 'day':
        start_date = today
        end_date = today
    elif filter_type == 'week':
        start_date = today - timedelta(days=today.weekday())  # Monday
        end_date = start_date + timedelta(days=6)  # Sunday
    elif filter_type == 'month':
        start_date = today.replace(day=1)
        last_day = calendar.monthrange(today.year, today.month)[1]
        end_date = today.replace(day=last_day)
    elif filter_type == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    else:
        start_date = None
        end_date = None

    # ===================== STUDENT ATTENDANCE ==========================
    student_qs = StudentAttendance.objects.all()
    if start_date and end_date:
        student_qs = student_qs.filter(attendance_date__range=(start_date, end_date))
    elif start_date:
        student_qs = student_qs.filter(attendance_date=start_date)

    total_students_db = StudentDatabase.objects.count()

    student_present_ids = set(student_qs.filter(status__iexact='present').values_list('student_id', flat=True))
    student_late_ids = set(student_qs.filter(status__iexact='late').values_list('student_id', flat=True))
    student_absent_ids = set(student_qs.filter(status__iexact='absent').values_list('student_id', flat=True))

    student_present = len(student_present_ids)
    student_late = len(student_late_ids)
    student_absent = len(student_absent_ids)

    student_attendance_rate = (
        round(((student_present + student_late) / total_students_db) * 100, 1)
        if total_students_db else 0
    )

    # ===================== CONTEXT ==========================
    context = {
        'student_present': student_present if 'student_attendance' in sections else 0,
        'student_late': student_late if 'student_attendance' in sections else 0,
        'student_absent': student_absent if 'student_attendance' in sections else 0,
        'student_attendance_rate': student_attendance_rate if 'student_attendance' in sections else 0,
        'selected_filter': filter_type,
    }

    return render(request, 'master/dashboard4.html', context)


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
from django.db.models import F, CharField
from django.db.models.functions import Coalesce

from .models import StudentDatabase
from .forms import StudentDatabaseForm


# Update import paths as needed
from django.db.models.functions import Coalesce, Cast
from django.db.models import F, CharField, DateTimeField

def student_database(request):
    selected_program_type = request.GET.get('program_type', '')
    selected_combination = request.GET.get('combination', '')

    students = StudentDatabase.objects.none()

    if selected_program_type and selected_combination:
        students = StudentDatabase.objects.annotate(
            admission_number=Coalesce(
                F('pu_admission__admission_no'),
                F('degree_admission__admission_no'),
                output_field=CharField()
            ),
            admission_date=Coalesce(
                Cast('pu_admission__admission_date', DateTimeField()),
                Cast('degree_admission__admission_date', DateTimeField()),
                output_field=DateTimeField()
            )
        )

        if selected_program_type != 'all':
            students = students.filter(course_type__name__iexact=selected_program_type)
        if selected_combination != 'all':
            students = students.filter(course__name__iexact=selected_combination)

        students = students.order_by('admission_number')

    program_type_list = CourseType.objects.values_list('name', flat=True).distinct()

    if selected_program_type and selected_program_type != 'all':
        combination_list = Course.objects.filter(
            course_type__name__iexact=selected_program_type
        ).values_list('name', flat=True).distinct()
    else:
        combination_list = Course.objects.values_list('name', flat=True).distinct()

    context = {
        'students': students,
        'program_type_list': program_type_list,
        'combination_list': combination_list,
        'selected_program_type': selected_program_type,
        'selected_combination': selected_combination,
    }

    return render(request, 'master/student_database_list.html', context)




def master_student_edit(request, pk):
    student = get_object_or_404(StudentDatabase, pk=pk)
    selected_type = request.GET.get('course_type', 'PU')

    # Calculate admission number manually (because it's not a model field)
    admission_no = None
    if student.pu_admission:
        admission_no = student.pu_admission.admission_no
    elif student.degree_admission:
        admission_no = student.degree_admission.admission_no

    if request.method == 'POST':
        form = StudentDatabaseForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student record updated successfully.")
            return redirect('student_database')
    else:
        form = StudentDatabaseForm(instance=student)

    return render(request, 'master/student_database_form.html', {
        'form': form,
        'student': student,
        'admission_no': admission_no,  # ✅ pass this explicitly
        'edit_mode': True,
        'back_to_list_url': 'student_database',
        'selected_type': selected_type,
    })


def master_student_view(request, pk):
    """
    View a single student entry in read-only mode.
    """
    student = get_object_or_404(StudentDatabase, pk=pk)
    selected_type = request.GET.get('course_type', 'PU')

    return render(request, 'master/student_database_form.html', {
        'student': student,
        'edit_mode': False,
        'back_to_list_url': 'student_database',
        'selected_type': selected_type,
    })






from django.shortcuts import render, get_object_or_404
from .models import StudentDatabase

from attendence.models import StudentAttendance  # adjust import based on your app name

from timetable.models import TimetableEntry  
import calendar
from datetime import date
from collections import defaultdict
from django.shortcuts import render, get_object_or_404

from collections import defaultdict
from datetime import date, timedelta
import calendar
from fees.models import StudentFeeCollection

# Map weekday index to day name
WEEKDAY_MAP = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}


def student_profile_view(request, student_id):
    student = get_object_or_404(StudentDatabase, id=student_id)

    if student.pu_admission:
        admission = student.pu_admission
        admission_type = "PU"
        admission_no = admission.admission_no
    elif student.degree_admission:
        admission = student.degree_admission
        admission_type = "Degree"
        admission_no = admission.admission_no
    else:
        admission = None
        admission_type = "Unknown"
        admission_no = None

    months = [
        (5, 'May'), (6, 'Jun'), (7, 'Jul'), (8, 'Aug'), (9, 'Sep'), (10, 'Oct'),
        (11, 'Nov'), (12, 'Dec'), (1, 'Jan'), (2, 'Feb'), (3, 'Mar'), (4, 'Apr')
    ]

    attendance_grid = []
    total_present = 0
    total_late = 0
    total_absent = 0
    total_holiday = 0
    total_classes = 0
    total_attended_classes = 0

    if admission_no:
        today = date.today()
        current_year = today.year
        start_year = current_year - 1 if today.month < 5 else current_year
        start_date = date(start_year, 5, 1)
        end_date = date(start_year + 1, 4, 30)

        records = StudentAttendance.objects.filter(
            student=student,
            attendance_date__range=(start_date, end_date)
        )

        attendance_by_date = defaultdict(list)
        for record in records:
            attendance_by_date[record.attendance_date].append(record)

        student_semester = getattr(student, 'semester_number', 1)
        timetable_entries = TimetableEntry.objects.filter(
            course=student.course,
            semester_number=student_semester
        )

        timetable_by_day = defaultdict(list)
        for entry in timetable_entries:
            timetable_by_day[entry.day].append(entry)

        valid_days_per_month = {}
        for m, _ in months:
            y = start_year if m >= 5 else start_year + 1
            valid_days_per_month[m] = calendar.monthrange(y, m)[1]

        for day in range(1, 32):
            if not any(day <= valid_days_per_month[m] for m, _ in months):
                continue

            row = []
            for m, _ in months:
                y = start_year if m >= 5 else start_year + 1
                try:
                    current_date = date(y, m, day)
                except ValueError:
                    row.append('')
                    continue

                if current_date > today:
                    row.append('')
                    continue

                weekday = current_date.weekday()
                weekday_name = WEEKDAY_MAP[weekday]

                if weekday in [5, 6]:  # Saturday or Sunday
                    row.append('W')
                    total_holiday += 1
                    continue

                scheduled_classes = timetable_by_day.get(weekday_name, [])
                class_count = len(scheduled_classes)

                if class_count == 0:
                    row.append('H')
                    total_holiday += 1
                    continue

             
                attended_count = 0
                for sched_class in scheduled_classes:
                    records_today = attendance_by_date.get(current_date, [])
                    matched = any(
                        (r.subject == sched_class.subject and r.status in ['present', 'late'])
                        for r in records_today
                    )


                    if matched:
                        attended_count += 1

                total_classes += class_count
                total_attended_classes += attended_count

                if attended_count > 0:
                    percentage = round((attended_count / class_count) * 100)
                    row.append(f'P ({percentage}%)')
                    total_present += 1
                else:
                    row.append('A (0%)')
                    total_absent += 1

            attendance_grid.append({'day': day, 'statuses': row})

        total_late = records.filter(status='L').count()

    attendance_percentage = round((total_attended_classes / total_classes) * 100, 2) if total_classes else 0
         # Fetch the admission again (already available)
    admission_no = admission.admission_no if admission else None

     # Now get fee_collections logic from fee_collection_collect
    fee_collections = StudentFeeCollection.objects.filter(admission_no=admission_no)
    fee_display_list = []
    for fee in fee_collections:
         fee_display_list.append({
             'id': fee.id,
             'fee_type': fee.fee_type,
             'due_date': fee.due_date,
             'amount': fee.amount,
             'paid_amount': fee.paid_amount,
             'balance_amount': fee.balance_amount,
             'status': fee.status,
             'applied_discount': getattr(fee, 'applied_discount', Decimal('0')),
             'total_paid': fee.paid_amount + getattr(fee, 'applied_discount', Decimal('0'))
         })

    context = {
        'student': student,
        'admission': admission,
        'admission_type': admission_type,
        'attendance_grid': attendance_grid,
        'months': months,
        'total_present': total_present,
        'total_late': total_late,
        'total_absent': total_absent,
        'total_holiday': total_holiday,
        'total_classes': total_classes,
        'total_attended_classes': total_attended_classes,
        'attendance_percentage': attendance_percentage,
         'fee_collections':fee_display_list,
    }

    return render(request, 'master/student_profile.html', context)









from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, CourseType
from .forms import CourseForm, CourseTypeForm

# CourseType Views
def course_type_list(request):
    types = CourseType.objects.all()
    return render(request, 'master/course_type_list.html', {'types': types})

from core.utils import log_activity, get_logged_in_user  # Make sure these are imported

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CourseTypeForm
from .models import CourseType

from core.utils import log_activity, get_logged_in_user  # Make sure these are imported

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CourseTypeForm
from .models import CourseType

from django.shortcuts import render, redirect
from django.contrib import messages
from master.forms import CourseTypeForm
from master.models import CourseType
from core.utils import get_logged_in_user, log_activity  # adjust import path as needed


def course_type_add(request):
    if request.method == 'POST':
        form = CourseTypeForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name'].strip()
            academic_year = form.cleaned_data['academic_year']

            # Check for duplicate ignoring case within the same academic year
            if CourseType.objects.filter(name__iexact=name, academic_year=academic_year).exists():
                form.add_error('name', "This Program Type already exists for the selected Batch.")
            else:
                course_type = form.save()

                # ✅ Optional: Track add activity
                user = get_logged_in_user(request)
                log_activity(user, 'created', course_type)

                messages.success(request, "Program Type added successfully.")
                return redirect('course_type_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CourseTypeForm()

    return render(request, 'master/course_type_form.html', {
        'form': form,
        'edit_mode': False
    })

from django.http import JsonResponse
from .models import CourseType

def check_program_type_name(request):
    name = request.GET.get('name', '').strip()
    exists = CourseType.objects.filter(name__iexact=name).exists()
    return JsonResponse({'exists': exists})


def course_type_view(request, pk):
    course_type = get_object_or_404(CourseType, pk=pk)
    form = CourseTypeForm(instance=course_type)

    # Disable all form fields to make it read-only in view mode
    for field in form.fields.values():
        field.disabled = True

    return render(request, 'master/course_type_form.html', {
        'form': form,
        'view_mode': True  # ✅ Consistent with other templates
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from master.forms import CourseTypeForm
from master.models import CourseType
from core.utils import get_logged_in_user, log_activity  # Adjust if your utils path differs


def course_type_edit(request, pk):
    course_type = get_object_or_404(CourseType, pk=pk)

    if request.method == 'POST':
        form = CourseTypeForm(request.POST, instance=course_type)

        if form.is_valid():
            name = form.cleaned_data['name'].strip()
            academic_year = form.cleaned_data['academic_year']

            # Prevent duplicates on update – exclude current record
            duplicate_exists = CourseType.objects.filter(
                name__iexact=name,
                academic_year=academic_year
            ).exclude(pk=course_type.pk).exists()

            if duplicate_exists:
                form.add_error('name', "This Program Type already exists for the selected Batch.")
            else:
                course_type.name = name
                course_type.academic_year = academic_year
                course_type.save()

                # Optional: log activity
                user = get_logged_in_user(request)
                log_activity(user, 'updated', course_type)

                messages.success(request, "Program Type updated successfully.")
                return redirect('course_type_list')
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = CourseTypeForm(instance=course_type)

    return render(request, 'master/course_type_form.html', {
        'form': form,
        'edit_mode': True
    })

def course_type_detail(request, pk):
    course_type = get_object_or_404(CourseType, pk=pk)
    return render(request, 'master/course_type_form.html', {'course_type': course_type})

from django.db.models import ProtectedError
from django.contrib import messages

from django.db.models import ProtectedError
from django.contrib import messages

from django.db.models import ProtectedError

def course_type_delete(request, pk):
    course_type = get_object_or_404(CourseType, pk=pk)
    user = get_logged_in_user(request)  # Get the logged-in user once

    try:
        course_type.delete()
        messages.success(request, "Program type deleted successfully.")
        log_activity(user, 'deleted', course_type)  # Log successful deletion
    except ProtectedError:
        messages.error(request, "Cannot delete this Course Type. It is being used in Courses or Enquiries.")
        log_activity(user, 'failed deletion (protected)', course_type)  # Log protected delete failure

    return redirect('course_type_list')

# Course Views
def course_form_list(request):
    courses = Course.objects.select_related('course_type').all()
    return render(request, 'master/course_list.html', {'courses': courses})

from .models import Course
from .forms import CourseForm
from django.shortcuts import render, redirect
from django.contrib import messages


def course_form_add(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)

            # Get the 'is_active' value from the form (radio button)
            is_active_value = request.POST.get('is_active', '1')
            course.is_active = is_active_value == '1'

            # ✅ Assign the user who is adding the course
            course.created_by = request.user  # or course.user = request.user depending on your model

            course.save()

            # Logging
            user = get_logged_in_user(request)
            log_activity(user, 'added', course)

            messages.success(request, "Course added successfully.")
            return redirect('course_form_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CourseForm()

    return render(request, 'master/course_form.html', {'form': form})
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Course  # ✅ this is your actual model
from . import views

@csrf_exempt
@require_POST
def validate_course(request):
    data = json.loads(request.body)
    name = data.get('name', '').strip()
    course_type = data.get('course_type')
    course_id = data.get('course_id')  # combination_id = course_id

    qs = Course.objects.filter(name__iexact=name, course_type_id=course_type)
    if course_id:
        qs = qs.exclude(pk=course_id)

    if qs.exists():
        return JsonResponse({
            "exists": True,
            "message": "This combination already exists for the selected program type."
        })
    return JsonResponse({"exists": False})


from django.shortcuts import render, get_object_or_404
from .models import Course
from .forms import CourseForm

def course_form_view(request, pk):
    course = get_object_or_404(Course, pk=pk)

    # Make all fields disabled for read-only view, including radio buttons
    form = CourseForm(instance=course)
    for field in form.fields.values():
        field.widget.attrs['readonly'] = True
        field.widget.attrs['disabled'] = True

    return render(request, 'master/course_form.html', {'form': form, 'view_mode': True})



# Course Edit View
# Course Edit View
def course_form_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save(commit=False)

            # Handle is_active from radio button
            is_active_value = request.POST.get('is_active', '1')
            course.is_active = is_active_value == '1'

            course.created_by = request.user  # or course.user = request.user depending on your model

            course.save()
            user = get_logged_in_user(request)
            log_activity(request.user, 'updated', course)
            messages.success(request, "Course updated successfully.")
            return redirect('course_form_list')
    else:
        form = CourseForm(instance=course)

    return render(request, 'master/course_form.html', {'form': form})


# Course Delete View
def course_form_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    try:
        course.delete()
        user = get_logged_in_user(request)
        log_activity(request.user, 'deleted', course)
        messages.success(request, "Course deleted successfully.")
    except ProtectedError:
        messages.error(request, "Cannot delete course because it is referenced by other data.")
    return redirect('course_form_list')

from .models import Semester
from .forms import SemesterForm

def semester_form_list(request):
    semesters = Semester.objects.select_related('course').all()
    return render(request, 'master/semester_list.html', {'semesters': semesters})


from .models import Semester
from .forms import SemesterForm
from django.shortcuts import render, redirect

def semester_form_add(request):
    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            semester = form.save(commit=False)

            # ✅ Manual handling of is_active (same style as course_create)
            is_active_value = request.POST.get('is_active')
            semester.is_active = True if is_active_value == '1' else False

            semester.save()
            return redirect('semester_form_list')
    else:
        form = SemesterForm()

    return render(request, 'master/semester_form.html', {
        'form': form
    })

def semester_form_edit(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    if request.method == 'POST':
        form = SemesterForm(request.POST, instance=semester)
        if form.is_valid():
            form.save()
            return redirect('semester_form_list')
    else:
        form = SemesterForm(instance=semester)
    return render(request, 'master/semester_form.html', {'form': form, 'mode': 'edit'})
 
def semester_form_view(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    form = SemesterForm(instance=semester)

    # Set fields to readonly/disabled
    for field in form.fields.values():
        field.widget.attrs['readonly'] = True
        field.widget.attrs['disabled'] = True

    # Pass `view_mode=True` for template logic
    return render(request, 'master/semester_form.html', {
        'form': form,
        'view_mode': True  # ✅ Important for template conditionals
    })

 
def semester_form_delete(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    if request.method == 'POST':
        semester.delete()
    return redirect('semester_form_list')


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







from .models import Transport
from .forms import TransportForm

def transport_form_list(request):
    transports = Transport.objects.all()
    return render(request, 'master/transport_list.html', {'transports': transports})

from core.utils import get_logged_in_user, log_activity  # ✅ Ensure this is imported

from django.contrib import messages

def transport_form_add(request):
    if request.method == 'POST':
        form = TransportForm(request.POST)
        if form.is_valid():
            transport = form.save()

            user = get_logged_in_user(request)
            log_activity(user, 'created', transport)

            messages.success(request, f"Route '{transport.route}' added successfully.")
            return redirect('transport_form_list')
    else:
        form = TransportForm()
    
    return render(request, 'master/transport_form.html', {'form': form})






from django.shortcuts import render, get_object_or_404, redirect
from .models import Transport
from .forms import TransportForm

# ✅ View Transport (Read-only)
def transport_form_view(request, pk):
    route = get_object_or_404(Transport, pk=pk)
    form = TransportForm(instance=route)

    # Make fields readonly/disabled
    for field in form.fields.values():
        field.widget.attrs['readonly'] = True
        field.widget.attrs['disabled'] = True

    return render(request, 'master/transport_form.html', {
        'form': form,
        'view_mode': True   # ✅ This enables view mode in the template
    })


# ✅ Edit Transport
from core.utils import get_logged_in_user, log_activity  # ✅ Ensure these are imported

def transport_form_edit(request, pk):
    transport = get_object_or_404(Transport, pk=pk)
    if request.method == 'POST':
        form = TransportForm(request.POST, instance=transport)
        if form.is_valid():
            form.save()

            user = get_logged_in_user(request)
            log_activity(user, 'updated', transport)

            messages.success(request, f"Route '{transport.route}' updated successfully.")
            return redirect('transport_form_list')
    else:
        form = TransportForm(instance=transport)

    return render(request, 'master/transport_form.html', {
        'form': form,
        'is_view': False
    })


def transport_form_delete(request, pk):
    transport = get_object_or_404(Transport, pk=pk)
    route_name = transport.route  # ✅ Store before deletion
    transport.delete()

    user = get_logged_in_user(request)
    log_activity(user, 'deleted', transport)

    messages.success(request, f"Route '{route_name}' deleted successfully.")
    return redirect('transport_form_list')



# views.py
from django.shortcuts import render
from django.utils import timezone
from .models import AcademicEvent
import calendar
from datetime import datetime

from datetime import datetime, date


def calendar_form(request):
    today = timezone.localdate()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    cal = calendar.Calendar(firstweekday=6)
    month_days = list(cal.monthdayscalendar(year, month))
    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    future_events_qs = AcademicEvent.objects.filter(
        date__year=year, date__month=month
    ).order_by('date', 'time')

    future_events = list(future_events_qs.values(
        'id', 'title', 'date', 'time', 'description', 'event_type'
    ))

    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    # ✅ Define recurring holidays (fixed dates every year)
    recurring_holidays = [
        {"month": 1, "day": 14, "name": "Makara Sankranti"},
        {"month": 2, "day": 26, "name": "Maha Shivaratri"},
        {"month": 3, "day": 31, "name": "Idul Fitr"},
        {"month": 4, "day": 10, "name": "Mahavir Jayanti"},
        {"month": 4, "day": 14, "name": "Dr. Ambedkar Jayanti"},
        {"month": 4, "day": 18, "name": "Good Friday"},
        {"month": 4, "day": 30, "name": "Basava Jayanti"},
        {"month": 5, "day": 1, "name": "May Day"},
        {"month": 6, "day": 7, "name": "Bakrid"},
        {"month": 7, "day": 6, "name": "Muharram"},
        {"month": 8, "day": 15, "name": "Independence Day"},
        {"month": 8, "day": 27, "name": "Ganesh Chaturthi"},
        {"month": 9, "day": 5, "name": "Eid‑Milad"},
        {"month": 10, "day": 1, "name": "Mahanavami / Vijayadasami"},
        {"month": 10, "day": 2, "name": "Gandhi Jayanti"},
        {"month": 10, "day": 7, "name": "Valmiki Jayanti"},
        {"month": 10, "day": 20, "name": "Naraka Chaturdashi"},
        {"month": 10, "day": 22, "name": "Deepavali"},
        {"month": 11, "day": 1, "name": "Kannada Rajyotsava"},
        {"month": 12, "day": 25, "name": "Christmas"},
    ]

    # ✅ Generate full-date holidays for the selected year
    all_holidays = []
    for h in recurring_holidays:
        try:
            holiday_date = date(year, h["month"], h["day"])
            all_holidays.append({
                "date": holiday_date,
                "name": h["name"]
            })
        except ValueError:
            # Skip invalid dates (e.g., Feb 29 in non-leap year)
            continue

    # ✅ Filter only current month holidays
    month_holidays = [h for h in all_holidays if h["date"].month == month]

    context = {
        'today': today,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'month_days': month_days,
        'weekdays': weekdays,
        'events': future_events_qs,
        'events_json': future_events,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'gov_holidays_json': [
            {"date": h["date"].isoformat(), "name": h["name"]}
            for h in month_holidays
        ],
        'month_holidays': month_holidays,
    }
    return render(request, 'master/calendar.html', context)







from .forms import AcademicEventForm


def add_event_view(request):
    if request.method == 'POST':
        form = AcademicEventForm(request.POST)
        if form.is_valid():
            saved_event = form.save()
            

            user = get_logged_in_user(request)
            log_activity(user, 'created', saved_event)
            return redirect('calendar_form')
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

from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import calendar
from .models import Employee

def employee_dashboard(request):
    today = timezone.localdate()
    filter_type = request.GET.get('filter', 'all')
    query = request.GET.get('q', '')

    employees = Employee.objects.all()

    # Per Day: Exact date match
    if filter_type == 'day':
        employees = employees.filter(created_at=today)

    # Per Week: From this Monday to coming Sunday
    elif filter_type == 'week':
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)          # Sunday
        employees = employees.filter(created_at__range=(start_of_week, end_of_week))

    # Per Month: From 1st to last day of this month
    elif filter_type == 'month':
        start_of_month = today.replace(day=1)
        last_day = calendar.monthrange(today.year, today.month)[1]
        end_of_month = today.replace(day=last_day)
        employees = employees.filter(created_at__range=(start_of_month, end_of_month))

    # Search filtering
    if query:
        employees = employees.filter(
            Q(name__icontains=query) |
            Q(department__icontains=query)
        )

    # Count from the filtered queryset only
    total = employees.count()
    professors = employees.filter(designation='Professor').count()
    associate_professors = employees.filter(designation='Associate Professor').count()
    assistant_professors = employees.filter(designation='Assistant Professor').count()

    context = {
        'employees': employees,
        'total': total,
        'professors': professors,
        'associate_professors': associate_professors,
        'assistant_professors': assistant_professors,
        'active_filter': filter_type,
        'query': query,
    }

    return render(request, 'master/employee_dashboard.html', context)





from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import EmployeeForm
from .models import Employee
from core.utils import get_logged_in_user, log_activity
 
from django.http import JsonResponse
from .models import Course, Subject

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Subject

@csrf_exempt
def get_subjects_by_course_and_semester(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        semester = str(request.POST.get('semester')).strip()  # 🔁 Ensure string comparison

        print(f"🔵 View called\nCourse ID: {course_id}\nSemester: {semester} (type: {type(semester)})")

        subjects = Subject.objects.filter(course_id=course_id, semester=semester)

        print(f"Subjects found: {subjects}")
        print(f"SQL Query: {subjects.query}")

        subject_data = [{'id': subject.id, 'name': subject.name} for subject in subjects]
        return JsonResponse({'subjects': subject_data})



from django.shortcuts import render, redirect
from .forms import EmployeeForm
from .models import Employee
from core.utils import get_logged_in_user,log_activity

from django.shortcuts import render, redirect
from .forms import EmployeeForm
from .models import Employee
from core.utils import get_logged_in_user,log_activity

from .models import EmployeeSubjectAssignment, Course, Subject  


from django.shortcuts import render, redirect
from .forms import EmployeeForm
from .models import Employee
from core.utils import get_logged_in_user,log_activity

from django.shortcuts import render, redirect
from .forms import EmployeeForm
from .models import Employee
from core.utils import get_logged_in_user,log_activity

from .models import EmployeeSubjectAssignment, Course, Subject  

from django.shortcuts import render, redirect
from .forms import EmployeeForm
from .models import Employee
from core.utils import get_logged_in_user,log_activity

from .models import EmployeeSubjectAssignment, Course, Subject  

def employee_form_add(request):
    excluded_fields = ['emp_code', 'category', 'designation', 'role']
    courses = Course.objects.all()

    # Auto-generate next emp_code
    last_emp = Employee.objects.order_by('-id').first()
    last_number = int(last_emp.emp_code.replace('EMP', '')) if last_emp and last_emp.emp_code.startswith('EMP') else 0
    next_emp_code = f"EMP{last_number + 1:03d}"

    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            if not employee.emp_code:
                employee.emp_code = next_emp_code
            employee.save()

            # Handle subject assignments
            course_ids = request.POST.getlist('course[]')
            semesters = request.POST.getlist('semester[]')
            subject_ids = request.POST.getlist('subject_id[]')

            for i in range(len(course_ids)):
                if course_ids[i] and semesters[i] and subject_ids[i]:
                    try:
                        EmployeeSubjectAssignment.objects.create(
                            employee=employee,
                            course_id=course_ids[i],
                            semester=semesters[i],
                            subject_id=subject_ids[i]
                        )
                    except (Course.DoesNotExist, Subject.DoesNotExist):
                        continue

            user = get_logged_in_user(request)
            log_activity(user, 'created', employee)
            messages.success(request, f"Employee '{employee.name}' added successfully!")
            return redirect('employee_list')
    else:
        form = EmployeeForm(initial={'emp_code': next_emp_code})

    context = {
        'form': form,
        'excluded_fields': excluded_fields,
        'courses': courses,
        'selected_assignments': [],
        'readonly': False,
        'title': 'Add Employee',
        'button_label': 'Save',
    }

    return render(request, 'master/employee_form.html', context)

from django.shortcuts import render
from .models import Employee

def employee_list(request):
    # Prefetch related subject assignments, including Course and Subject
    employees = Employee.objects.prefetch_related(
        'subject_assignments__course',
        'subject_assignments__subject'
    ).all()

    return render(request, 'master/employee_list.html', {
        'employees': employees
    })


from django.shortcuts import render, get_object_or_404, redirect
from .models import Employee, Course, Subject, EmployeeSubjectAssignment
from django.shortcuts import render, get_object_or_404, redirect
from .models import Employee, Course, EmployeeSubjectAssignment
from .forms import EmployeeForm

import logging
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Employee, Course, Subject, EmployeeSubjectAssignment
from .forms import EmployeeForm
from core.utils import get_logged_in_user, log_activity

logger = logging.getLogger(__name__)

def employee_form_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    excluded_fields = ['emp_code', 'category', 'designation', 'role']
    courses = Course.objects.all()

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            logger.info(f"Employee '{employee.name}' (ID: {employee.id}) updated via form.")

            assignment_ids = request.POST.getlist('assignment_id[]')  # Hidden input for existing IDs
            course_ids = request.POST.getlist('course[]')
            semesters = request.POST.getlist('semester[]')
            subject_ids = request.POST.getlist('subject_id[]')

            submitted_ids = []

            for i in range(len(course_ids)):
                course_id = course_ids[i]
                semester = semesters[i]
                subject_id = subject_ids[i]

                if not (course_id and semester and subject_id):
                    logger.warning(f"Skipping assignment row {i} due to incomplete data.")
                    continue

                if i < len(assignment_ids) and assignment_ids[i]:
                    assignment_id = assignment_ids[i]
                    submitted_ids.append(int(assignment_id))

                    try:
                        assignment = EmployeeSubjectAssignment.objects.get(id=assignment_id)
                        assignment.course_id = course_id
                        assignment.semester = semester
                        assignment.subject_id = subject_id
                        assignment.save()
                        logger.info(f"Updated assignment ID {assignment.id} for employee {employee.id}.")
                    except EmployeeSubjectAssignment.DoesNotExist:
                        logger.error(f"Assignment ID {assignment_id} not found for update.")
                else:
                    new_assignment = EmployeeSubjectAssignment.objects.create(
                        employee=employee,
                        course_id=course_id,
                        semester=semester,
                        subject_id=subject_id
                    )
                    submitted_ids.append(new_assignment.id)
                    logger.info(f"Created new assignment ID {new_assignment.id} for employee {employee.id}.")

            # Delete removed assignments
            deleted = EmployeeSubjectAssignment.objects.filter(employee=employee).exclude(id__in=submitted_ids)
            deleted_ids = list(deleted.values_list('id', flat=True))
            deleted_count = deleted.count()
            deleted.delete()

            if deleted_count:
                logger.info(f"Deleted {deleted_count} assignments: {deleted_ids} for employee {employee.id}")

            user = get_logged_in_user(request)
            log_activity(user, 'updated', employee)

            messages.success(request, f"Employee '{employee.name}' updated successfully!")
            return redirect('employee_list')
        else:
            logger.warning(f"Employee form not valid for {employee.id}. Errors: {form.errors}")
    else:
        form = EmployeeForm(instance=employee)

    selected_assignments = []
    assignments = EmployeeSubjectAssignment.objects.filter(employee=employee).select_related('course', 'subject')
    for assignment in assignments:
        selected_assignments.append({
            'id': assignment.id,
            'course_id': assignment.course.id,
            'course_name': assignment.course.name,
            'semester': assignment.semester,
            'subject_id': assignment.subject.id,
            'subject_name': assignment.subject.name
        })

    return render(request, 'master/employee_form.html', {
        'form': form,
        'excluded_fields': excluded_fields,
        'title': 'Edit Employee',
        'button_label': 'Update',
        'courses': courses,
        'selected_assignments': selected_assignments,
        'readonly': False
    })


from django.shortcuts import render, get_object_or_404
from .models import Employee, EmployeeSubjectAssignment, Course, Subject
from .forms import EmployeeForm

def employee_form_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    form = EmployeeForm(instance=employee, readonly=True)

    assignments = EmployeeSubjectAssignment.objects.filter(employee=employee).select_related('course', 'subject')
    selected_assignments = [
        {
            'course_id': a.course.id,
            'course_name': a.course.name,
            'semester': a.semester,
            'semester_name': f"Semester {a.semester}" if a.semester else "",
            'subject_id': a.subject.id,
            'subject_name': a.subject.name,
        }
        for a in assignments
    ]

    context = {
        'form': form,
        'readonly': True,
        'title': 'View Employee',
        'employee': employee,
        'selected_assignments': selected_assignments,
        'courses': Course.objects.all(),
    }
    return render(request, 'master/employee_form.html', context)


def employee_form_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        EmployeeSubjectAssignment.objects.filter(employee=employee).delete()
        employee.delete()
        user = get_logged_in_user(request)
        log_activity(user, 'deleted', employee)
        messages.success(request, f"Employee '{employee.name}' deleted successfully!")

    return redirect('employee_list')





from django.shortcuts import render, get_object_or_404, redirect
from master.models import AcademicYear
from master.forms import AcademicYearForm

def academic_year_list(request):
    years = AcademicYear.objects.all()
    return render(request, 'master/academic_year_list.html', {'years': years})


from core.utils import log_activity, get_logged_in_user  # Ensure these are imported

def academic_year_create(request):
    if request.method == 'POST':
        form = AcademicYearForm(request.POST)
        if form.is_valid():
            year = form.save()
            messages.success(request, "Batch added successfully.")

            # ✅ Log activity
            user = get_logged_in_user(request)
            log_activity(user, 'added', year)

            return redirect('academic_year_list')
    else:
        form = AcademicYearForm()
    return render(request, 'master/academic_year_form.html', {
        'form': form,
        'title': 'Add Batch'
    })


def academic_year_edit(request, pk):
    year = get_object_or_404(AcademicYear, pk=pk)
    if request.method == 'POST':
        form = AcademicYearForm(request.POST, instance=year)
        if form.is_valid():
            form.save()
            messages.success(request, "Batch updated successfully.")

            # ✅ Log activity
            user = get_logged_in_user(request)
            log_activity(user, 'updated', year)

            return redirect('academic_year_list')
    else:
        form = AcademicYearForm(instance=year)
    return render(request, 'master/academic_year_form.html', {
        'form': form,
        'title': 'Edit Batch'
    })



from django.db import IntegrityError

from django.db import IntegrityError

def academic_year_delete(request, pk):
    year = get_object_or_404(AcademicYear, pk=pk)
    try:
        user = get_logged_in_user(request)
        log_activity(user, 'deleted', year)  # Log before deleting
        year.delete()
        messages.success(request, "Batch deleted successfully.")
    except IntegrityError:
        messages.error(request, "Cannot delete Batch as it is referenced by other records.")
    return redirect('academic_year_list')



#fee Master

from django.shortcuts import render, redirect, get_object_or_404
from .models import FeeMaster
from .forms import FeeMasterForm

def fee_detail_list(request):
    fees = FeeMaster.objects.all()
    return render(request, 'master/fee_master_list.html', {'fees': fees})

def fee_detail_view(request, pk):
    fee = get_object_or_404(FeeMaster, pk=pk)
    return render(request, 'master/fee_master_form.html', {
        'form': FeeMasterForm(instance=fee),
        'title': 'View Fee Detail',
        'view_only': True
    })

from django.contrib import messages


def fee_detail_create(request):
    if request.method == 'POST':
        form = FeeMasterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee detail added successfully.')
            return redirect('fee_detail_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FeeMasterForm()
    return render(request, 'master/fee_master_form.html', {
        'form': form,
        'title': 'Add Fee Detail'
    })

def fee_detail_edit(request, pk):
    fee = get_object_or_404(FeeMaster, pk=pk)
    if request.method == 'POST':
        form = FeeMasterForm(request.POST, instance=fee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee detail updated successfully.')
            return redirect('fee_detail_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FeeMasterForm(instance=fee)
    return render(request, 'master/fee_master_form.html', {
        'form': form,
        'title': 'Edit Fee Detail'
    })

def fee_detail_delete(request, pk):
    fee = get_object_or_404(FeeMaster, pk=pk)
    if request.method == 'POST':
        fee.delete()
        messages.success(request, 'Fee detail deleted successfully.')
    else:
        messages.error(request, 'Invalid request.')
    return redirect('fee_detail_list')




from django.http import JsonResponse
from .models import Course

def get_program_type_by_combination(request):
    course_id = request.GET.get('course_id')
    course = Course.objects.filter(id=course_id).select_related('course_type').first()
    if course:
        return JsonResponse({'id': course.course_type.id, 'name': course.course_type.name})
    return JsonResponse({}, status=404)


from django.http import JsonResponse
from .models import Course

def load_combinations(request):
    program_type_id = request.GET.get('program_type')
    combinations = Course.objects.filter(course_type_id=program_type_id).values('id', 'name')
    return JsonResponse(list(combinations), safe=False)



from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from .models import StudentDatabase, PromotionHistory



def promote_student(request, student_id):
    if request.method == 'POST':
        student = get_object_or_404(StudentDatabase, id=student_id)

        is_pu = student.current_year is not None
        is_degree = student.semester is not None

        from_year = student.current_year if is_pu else None
        from_semester = student.semester if is_degree else None

        # Determine promotion_cycle from current date
        current_year = timezone.now().year
        next_year = current_year + 1
        promotion_cycle = f"{current_year}-{next_year}"

         # Prepare promotion message parts
        promoted_text = ""

        # Promote
        if is_pu and student.current_year < 2:
            student.current_year += 1
        elif is_degree and student.semester < 6:
            student.semester += 1
        else:
            student.status = "Graduated"

        # Save promotion history
        PromotionHistory.objects.create(
            admission_no=student.get_admission_no(),
            academic_year=student.academic_year,     # Full program duration e.g. 2025–2028
            promotion_cycle=promotion_cycle,         # E.g. "2025–2026"
            from_year=from_year,
            to_year=student.current_year if is_pu else None,
            from_semester=from_semester,
            to_semester=student.semester if is_degree else None,
            student_userid=student.student_userid,
            student_name=student.student_name,
            promotion_date=timezone.now().date(),
        )

          # Add success message for snackbar
        messages.success(request, f"{student.student_name} has been promoted {promoted_text}")

        student.save()
        return redirect('student_database')  # Redirect to your listing page

    return redirect('student_database')

from django.shortcuts import render, get_object_or_404, redirect
from .models import PromotionHistory
from .forms import PromotionHistoryForm

def promotion_history_list(request):
    histories = PromotionHistory.objects.all().order_by('-promotion_date')
    return render(request, 'master/promotion_history_list.html', {'promotion_histories': histories})

def promotion_history_edit(request, pk):
    history = get_object_or_404(PromotionHistory, pk=pk)
    form = PromotionHistoryForm(request.POST or None, instance=history)

    if request.method == 'POST':
        if form.is_valid():
            updated_history = form.save()
            messages.success(
                request,
                f"Promotion history for '{updated_history.student_name}' updated successfully!"
            )
            return redirect('promotion_history_list')
        else:
            messages.error(request, 'Please correct the errors in the form.')

    return render(request, 'master/promotion_history_form.html', {
        'form': form,
        'form_title': 'Edit Promotion History'
    })

def promotion_history_delete(request, pk):
    history = get_object_or_404(PromotionHistory, pk=pk)

    if request.method == 'POST':
        student_name = history.student_name
        history.delete()
        messages.success(
            request,
            f"Promotion history for '{student_name}' deleted successfully!"
        )
        return redirect('promotion_history_list')

    return redirect('promotion_history_list')



def fee_type_list(request):
    fee_types = FeeType.objects.all()
    return render(request, 'master/fee_type_list.html', {'fee_types': fee_types})

from django.http import JsonResponse
from .models import FeeType
 
def check_fee_type_name(request):
    name = request.GET.get('name', '').strip()
    exists = FeeType.objects.filter(name__iexact=name).exists()
    return JsonResponse({'exists': exists})
# ADD VIEW
from django.shortcuts import render, get_object_or_404, redirect
from .models import FeeType
from .forms import FeeTypeForm
 
from django.shortcuts import render, get_object_or_404, redirect
from .models import FeeType
from .forms import FeeTypeForm
def fee_type_add(request):
    if request.method == 'POST':
        form = FeeTypeForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name'].strip()
 
            # Check for duplicate Fee Type (case-insensitive)
            if FeeType.objects.filter(name__iexact=name).exists():
                form.add_error('name', "This Fee Type already exists.")
            else:
                fee_type = form.save()
                messages.success(request, "Fee Type added successfully.")
 
                # Optional: Log the creation
                # user = get_logged_in_user(request)
                # log_activity(user, 'created', fee_type)
 
                return redirect('fee_type_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = FeeTypeForm()
 
    return render(request, 'master/fee_type_form.html', {
        'form': form,
        'mode': 'add',
    })
 
 
def fee_type_edit(request, pk):
    fee_type = get_object_or_404(FeeType, pk=pk)
    if request.method == 'POST':
        form = FeeTypeForm(request.POST, instance=fee_type)
        if form.is_valid():
            name = form.cleaned_data['name'].strip()
 
            # Check for duplicate Fee Type (excluding the current one)
            if FeeType.objects.filter(name__iexact=name).exclude(pk=fee_type.pk).exists():
                form.add_error('name', "This Fee Type already exists.")
            else:
                fee_type = form.save()
                messages.success(request, "Fee Type updated successfully.")
 
                # Optional: Log the update
                # user = get_logged_in_user(request)
                # log_activity(user, 'updated', fee_type)
 
                return redirect('fee_type_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = FeeTypeForm(instance=fee_type)
 
    return render(request, 'master/fee_type_form.html', {
        'form': form,
        'instance': fee_type,
        'mode': 'edit',
    })

# VIEW ONLY (READ-ONLY) VIEW
def fee_type_view(request, pk):
    fee_type = get_object_or_404(FeeType, pk=pk)
    form = FeeTypeForm(instance=fee_type)
    return render(request, 'master/fee_type_form.html', {
        'form': form,
        'instance': fee_type,
        'mode': 'view',
    })


# DELETE VIEW
def fee_type_delete(request, pk):
    fee_type = get_object_or_404(FeeType, pk=pk)
    fee_type.delete()
    return redirect('fee_type_list')



