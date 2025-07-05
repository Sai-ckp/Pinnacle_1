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
    # If user already logged in, redirect to dashboard
    if request.session.get('user_id'):
        user_id = request.session['user_id']
        if user_id == 2:
            return redirect('dashboard_view')
        else:
            return redirect('dashboard_view')
 
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
 
        try:
            user = UserCustom.objects.get(username=username)
            if user.password == password:  # plain password check (consider hashing!)
                # Set logged-in user session
                request.session['user_id'] = user.id
 
                # Redirect after login
                if user.id == 2:
                    return redirect('dashboard_view')
                else:
                    return redirect('dashboard_view')
            else:
                error = 'Invalid password'
        except UserCustom.DoesNotExist:
            error = 'User does not exist'
 
    users = UserCustom.objects.all()  # For user dropdown on login page
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


def custom_login_view(request):
    # If user already logged in, redirect to dashboard
    if request.session.get('user_id'):
        user_id = request.session['user_id']
        if user_id == 2:
            return redirect('dashboard_view2')
        else:
            return redirect('dashboard_view')
 
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
 
        try:
            user = UserCustom.objects.get(username=username)
            if user.password == password:  # plain password check (consider hashing!)
                # Set logged-in user session
                request.session['user_id'] = user.id
 
                # Redirect after login
                if user.id == 2:
                    return redirect('dashboard_view')
                else:
                    return redirect('dashboard_view')
            else:
                error = 'Invalid password'
        except UserCustom.DoesNotExist:
            error = 'User does not exist'
 
    users = UserCustom.objects.all()  # For user dropdown on login page
    return render(request, 'master/login.html', {'error': error, 'users': users})

# def custom_login_view(request):
#     error = None
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         try:
#             user = UserCustom.objects.get(username=username)
#             if user.is_locked:
#                 error = "User account is locked due to multiple wrong attempts. Please contact admin."
#             elif user.password == password:
#                 user.wrong_attempts = 0
#                 user.save()
#                 request.session['user_id'] = user.id
#                 log_activity(user, 'login', user)
#                 if not user.passcode_set:
#                     return redirect('choose_passcode_view')
#                 # Passcode is set, proceed to license logic
#                 return handle_license_and_redirect(user, request)
#             else:
#                 user.wrong_attempts += 1
#                 if user.wrong_attempts >= 3:
#                     user.is_locked = True
#                 user.save()
#                 if user.is_locked:
#                     error = "Invalid password. Account locked after 3 wrong attempts. Please contact admin."
#                 else:
#                     error = "Invalid password."
#         except UserCustom.DoesNotExist:
#             error = 'User does not exist'
#     users = UserCustom.objects.all()
#     return render(request, 'master/login.html', {'error': error, 'users': users})

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
from core.utils import get_logged_in_user, log_activity

from django.contrib import messages

from django.shortcuts import render, redirect

from master.models import UserCustom
 
def add_user(request):

    if request.method == 'POST':

        username = request.POST.get('username')

        password = request.POST.get('password')
 
        if not username or not password:

            messages.error(request, "Username and password are required.")

        else:

            user_instance = UserCustom.objects.create(username=username, password=password)

            # ✅ Log activity here

            user = get_logged_in_user(request)

            log_activity(user, 'created', user_instance)
 
            messages.success(request, "User added successfully.")

            return redirect('user_list')
 
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
 
 

from django.shortcuts import render, redirect
from .forms import SubjectForm
from .models import Semester, Subject
from master.models import Course  # Make sure to import Course

def subject_form_add(request):
    form = SubjectForm(request.POST or None)

    # Determine which course is selected (for loading semesters)
    selected_course_id = request.POST.get('course') if request.method == 'POST' else request.GET.get('course')

    # Load semesters for the selected course only if one is selected
    semesters = Semester.objects.filter(course_id=selected_course_id).order_by('number') if selected_course_id else []

    if request.method == 'POST' and form.is_valid():
        semester_number = request.POST.get('semester_number')
        is_active_flag = request.POST.get('is_active', '1')

        if not semester_number:
            form.add_error(None, "Please select a semester.")
        else:
            subject = form.save(commit=False)
            subject.semester_number = int(semester_number)
            subject.is_active = (is_active_flag == '1')
            subject.save()
            user = get_logged_in_user(request)
            log_activity(request.user, 'added', subject)

            return redirect('subject_form_list')

    return render(request, 'master/add_subject.html', {
        'form': form,
        'semesters': semesters,
        'selected_course_id': selected_course_id,
    })




from django.shortcuts import render, get_object_or_404, redirect
from .models import Subject, Semester
from .forms import SubjectForm
from django.shortcuts import render, get_object_or_404
from .models import Subject, Semester
from .forms import SubjectForm

# ✅ Subject View (Read-only)
def subject_form_view(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    form = SubjectForm(instance=subject)

    # Disable all form fields, including 'is_active' radio inputs
    for name, field in form.fields.items():
        field.disabled = True
        if name == 'is_active':
            field.widget.attrs['disabled'] = True  # Extra layer for radios

    semesters = Semester.objects.filter(course_id=subject.course.id).order_by('number')

    return render(request, 'master/add_subject.html', {
        'form': form,
        'semesters': semesters,
        'selected_course_id': subject.course.id,
        'selected_semester_number': subject.semester_number,
        'is_view': True  # Use this flag in template to hide Save button
    })


 


# ✅ Subject Edit (Update)
def subject_form_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)

    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        selected_course_id = request.POST.get('course')
        selected_semester_number = request.POST.get('semester_number')
        is_active_flag = request.POST.get('is_active', '1')

        if form.is_valid():
            if not selected_semester_number:
                form.add_error(None, "Please select a semester.")
            else:
                updated_subject = form.save(commit=False)
                updated_subject.semester_number = int(selected_semester_number)
                updated_subject.is_active = (is_active_flag == '1')
                updated_subject.save()
                user = get_logged_in_user(request)
                log_activity(request.user, 'updated', updated_subject)

                return redirect('subject_form_list')
    else:
        form = SubjectForm(instance=subject)
        selected_course_id = subject.course.id
        selected_semester_number = subject.semester_number

    semesters = Semester.objects.filter(course_id=selected_course_id).order_by('number')

    return render(request, 'master/add_subject.html', {
        'form': form,
        'semesters': semesters,
        'selected_course_id': selected_course_id,
        'selected_semester_number': selected_semester_number,
        'is_view': False  # Allow editing
    })


# ✅ Subject Delete
def subject_form_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    subject.delete()
    user = get_logged_in_user(request)
    log_activity(request.user, 'deleted', subject)
    return redirect('subject_form_list')

from django.http import JsonResponse
from .models import Employee

def get_faculties_by_subject(request):
    subject_name = request.GET.get('name', '').strip()
    faculties = Employee.objects.filter(department__iexact=subject_name)
    data = [{'id': f.id, 'name': f.name} for f in faculties]
    return JsonResponse({'faculties': data})




from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import calendar
from .models import Employee

def employee_list(request):
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
from core.utils import get_logged_in_user,log_activity

def employee_form_add(request):
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



            user = get_logged_in_user(request)
            log_activity(user, 'created', employee)
            return redirect('employee_list')  # Change to your list view URL name
    else:
        form = EmployeeForm(initial={'emp_code': next_emp_code})

    return render(request, 'master/employee_form.html', {
        'form': form,
        'next_emp_code': next_emp_code,
        'excluded_fields': excluded_fields,
    })


from django.shortcuts import render, get_object_or_404, redirect
from .models import Employee
from .forms import EmployeeForm

def employee_form_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    excluded_fields = ['emp_code', 'category', 'designation', 'role']

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            user = get_logged_in_user(request)
            log_activity(user, 'edited', employee)
            return redirect('employee_list')  # Change to your list view name
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'master/employee_form.html', {
        'form': form,
        'excluded_fields': excluded_fields,
        'title': 'Edit Employee',
        'button_label': 'Update',
    })

def employee_form_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'master/employee_form_view.html', {'employee': employee})

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Employee


def employee_form_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee.delete()
        user = get_logged_in_user(request)
        log_activity(user, 'deleted', employee)
        messages.success(request, 'Employee deleted successfully.')
        return redirect('employee_list')  # ✅ Make sure this URL name exists

    return redirect('employee_list')  # Fallback redirect for safety

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

from admission.models import (
    Enquiry1, Enquiry2, PUAdmission, DegreeAdmission,
    Student as AdmissionStudent, Student
)
from attendence.models import StudentAttendance, attendance
from .models import SentMessageContact, Employee


def dashboard_view(request):
    filter_type = request.GET.get('filter', 'all')
    section = request.GET.get('sections', 'all')
    now = timezone.now()
    today = now.date()

    if filter_type == 'day':
        start_date = today
    elif filter_type == 'week':
        start_date = today - datetime.timedelta(days=today.weekday())
    elif filter_type == 'month':
        start_date = today.replace(day=1)
    else:
        start_date = None

    # ================= BASE QUERYSETS =================
    pu_admission_qs = PUAdmission.objects.filter(status="confirmed")
    degree_admission_qs = DegreeAdmission.objects.filter(status="confirmed")
    enquiry1_qs = Enquiry1.objects.all()
    enquiry2_qs = Enquiry2.objects.all()
    student_qs = Student.objects.all()
    employee_qs = Employee.objects.all()

    # ============ FILTER BY SECTION AND DATE ============
    if start_date:
        if section in ['students', 'all']:
            pu_admission_qs = pu_admission_qs.filter(admission_date__gte=start_date)
            degree_admission_qs = degree_admission_qs.filter(admission_date__gte=start_date)
            student_qs = student_qs.filter(receipt_date__gte=start_date)

        if section in ['fees']:
            student_qs = student_qs.filter(receipt_date__gte=start_date)

        if section in ['enquiries', 'all']:
            enquiry1_qs = enquiry1_qs.filter(enquiry_date__gte=start_date)
            enquiry2_qs = enquiry2_qs.filter(enquiry_date__gte=start_date)

        if section in ['messages', 'all']:
            enquiry1_whatsapp_qs = Enquiry1.objects.filter(whatsapp_status='sent', whatsapp_sent_date__gte=start_date)
            enquiry2_whatsapp_qs = Enquiry2.objects.filter(whatsapp_status='sent', whatsapp_sent_date__gte=start_date)
            sentmessage_qs = SentMessageContact.objects.filter(status="Sent", sent_date__gte=start_date)
        else:
            enquiry1_whatsapp_qs = Enquiry1.objects.filter(whatsapp_status='sent')
            enquiry2_whatsapp_qs = Enquiry2.objects.filter(whatsapp_status='sent')
            sentmessage_qs = SentMessageContact.objects.filter(status="Sent")

        if section in ['faculties', 'all']:
            employee_qs = employee_qs.filter(created_at__gte=start_date)
    else:
        enquiry1_whatsapp_qs = Enquiry1.objects.filter(whatsapp_status='sent')
        enquiry2_whatsapp_qs = Enquiry2.objects.filter(whatsapp_status='sent')
        sentmessage_qs = SentMessageContact.objects.filter(status="Sent")

    # ===================== COUNTS ==========================
    total_pu_students = pu_admission_qs.count()
    total_degree_students = degree_admission_qs.count()
    total_students = total_pu_students + total_degree_students

    total_pu_enquiries = enquiry1_qs.count()
    total_degree_enquiries = enquiry2_qs.count()
    total_enquiries = total_pu_enquiries + total_degree_enquiries

    enquiry1_sent = enquiry1_whatsapp_qs.count()
    enquiry2_sent = enquiry2_whatsapp_qs.count()
    enquiries_whatsapp_sent = enquiry1_sent + enquiry2_sent

    admission_messages_sent = sentmessage_qs.count()
    total_messages_sent = enquiries_whatsapp_sent + admission_messages_sent

    pending_messages = (
        Enquiry1.objects.filter(whatsapp_status='pending').count() +
        Enquiry2.objects.filter(whatsapp_status='pending').count() +
        SentMessageContact.objects.filter(status='Pending').count()
    )

    # ===================== FEES ==========================
    decimal_type = DecimalField(max_digits=12, decimal_places=2)

    total_declared_fee = student_qs.aggregate(
        total=Sum(ExpressionWrapper(
            Coalesce(F('tuition_fee'), 0) +
            Coalesce(F('transport_fee'), 0) +
            Coalesce(F('hostel_fee'), 0) +
            Coalesce(F('books_fee'), 0) +
            Coalesce(F('uniform_fee'), 0) +
            Coalesce(F('other_fee'), 0),
            output_field=decimal_type
        ))
    )['total'] or 0

    total_collected_fee = student_qs.aggregate(
        total=Sum(ExpressionWrapper(
            Coalesce(F('tuition_fee_paid'), 0) +
            Coalesce(F('transport_fee_paid'), 0) +
            Coalesce(F('hostel_fee_paid'), 0) +
            Coalesce(F('books_fee_paid'), 0) +
            Coalesce(F('uniform_fee_paid'), 0) +
            Coalesce(F('other_amount'), 0),
            output_field=decimal_type
        ))
    )['total'] or 0

    total_pending_fees = student_qs.aggregate(
        total=Sum(ExpressionWrapper(
            Coalesce(F('tuition_pending_fee'), 0) +
            Coalesce(F('transport_pending_fee'), 0) +
            Coalesce(F('hostel_pending_fee'), 0) +
            Coalesce(F('books_pending_fee'), 0) +
            Coalesce(F('uniform_pending_fee'), 0),
            output_field=decimal_type
        ))
    )['total'] or 0

    total_pu_application_fee = PUAdmission.objects.aggregate(total=Sum('application_fee'))['total'] or 0
    total_degree_application_fee = DegreeAdmission.objects.aggregate(total=Sum('application_fee'))['total'] or 0
    total_application_fee = total_pu_application_fee + total_degree_application_fee

          # ===================== ATTENDANCE ==========================
    faculty_attendance_qs = attendance.objects.all()
    student_attendance_qs = StudentAttendance.objects.all()
 
    if start_date:
        faculty_attendance_qs = faculty_attendance_qs.filter(date__gte=start_date)  # Correct field: `date`
        student_attendance_qs = student_attendance_qs.filter(attendance_date__gte=start_date)  # Correct field: `attendance_date`
 
    total_faculty_attendance = faculty_attendance_qs.count()
    faculty_attendance_rate = 0
    if total_faculty_attendance:
        present_faculty_attendance = faculty_attendance_qs.filter(status__in=['Present', 'Late']).count()
        faculty_attendance_rate = round((present_faculty_attendance / total_faculty_attendance) * 100, 2)
 
    total_student_attendance = student_attendance_qs.count()
    student_attendance_rate = 0
    if total_student_attendance:
        present_student_attendance = student_attendance_qs.filter(status__in=['present', 'late']).count()
        student_attendance_rate = round((present_student_attendance / total_student_attendance) * 100, 2)
 
    # ===================== EMPLOYEES ==========================
    total_employees = employee_qs.count()
    faculty_designations = ['Professor', 'Associate Professor', 'Assistant Professor']
    total_faculties = employee_qs.filter(designation__in=faculty_designations).count()
    recent_activities = RecentActivity.objects.select_related('user').order_by('-timestamp')[:5]
    # ===================== CONTEXT ==========================
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
        'total_pending_fees': total_pending_fees,
        'total_declared_fee': total_declared_fee,
        'filter_type': filter_type,
        'section': section,
         'recent_activities': recent_activities,
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


def student_database(request):
    """
    Display all students in the database.
    """
    students = StudentDatabase.objects.all().order_by('admission_no')
    return render(request, 'master/student_database_list.html', {
        'students': students,
    })

def master_student_edit(request, pk):
    student = get_object_or_404(StudentDatabase, pk=pk)
    selected_type = request.GET.get('course_type', getattr(student, 'course_type', 'PU'))
 
    if request.method == 'POST':
        form = StudentDatabaseForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            user = get_logged_in_user(request)
            log_activity(user, 'edited', student)
            return redirect('student_database')
    else:
        form = StudentDatabaseForm(instance=student)
 
    return render(request, 'master/student_database_form.html', {
        'form': form,
        'student': student,
        'edit_mode': True,
        'back_to_list_url': 'student_database',
        'selected_type': selected_type,
    })
 
 
def master_student_view(request, pk):
    student = get_object_or_404(StudentDatabase, pk=pk)
    selected_type = request.GET.get('course_type', getattr(student, 'course_type', 'PU'))
 
    return render(request, 'master/student_database_form.html', {
        'student': student,
        'edit_mode': False,
        'back_to_list_url': 'student_database',
        'selected_type': selected_type,
    })


from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, CourseType
from .forms import CourseForm, CourseTypeForm

# CourseType Views
def course_type_list(request):
    types = CourseType.objects.all()
    return render(request, 'master/course_type_list.html', {'types': types})

from core.utils import log_activity, get_logged_in_user  # Make sure these are imported

def course_type_add(request):
    if request.method == 'POST':
        form = CourseTypeForm(request.POST)
        if form.is_valid():
            course_type = form.save()
 
# ✅ Log activity here
            user = get_logged_in_user(request)
            log_activity(user, 'created', course_type)

            return redirect('course_type_list')
    else:
        form = CourseTypeForm()
    return render(request, 'master/course_type_form.html', {'form': form})



def course_type_view(request, pk):
    course_type = get_object_or_404(CourseType, pk=pk)
    form = CourseTypeForm(instance=course_type)
 
    # Disable all fields to make the form read-only
    for field in form.fields.values():
        field.disabled = True
 
    return render(request, 'master/course_type_form.html', {
        'form': form,
        'is_view': True  # Use this in your template to hide Save button
    })
def course_type_edit(request, pk):
    course_type = get_object_or_404(CourseType, pk=pk)
    if request.method == 'POST':
        form = CourseTypeForm(request.POST, instance=course_type)
        if form.is_valid():
            course_type = form.save()
 
# ✅ Log activity here
            user = get_logged_in_user(request)
            log_activity(user, 'updated', course_type)

            return redirect('course_type_list')
    else:
        form = CourseTypeForm(instance=course_type)
    return render(request, 'master/course_type_form.html', {'form': form})

def course_type_detail(request, pk):
    course_type = get_object_or_404(CourseType, pk=pk)
    return render(request, 'master/course_type_form.html', {'course_type': course_type})

from django.db.models import ProtectedError
from django.contrib import messages

def course_type_delete(request, pk):
    course_type = get_object_or_404(CourseType, pk=pk)
    try:
        course_type.delete()
        
        messages.success(request, "Course type deleted successfully.")
    except ProtectedError:
        messages.error(request, "Cannot delete this Course Type. It is being used in Courses or Enquiries.")
        user = get_logged_in_user(request)
        log_activity(user, 'deleted', course_type)
    return redirect('course_type_list')

# Course Views
def course_form_list(request):
    courses = Course.objects.select_related('course_type').all()
    return render(request, 'master/course_list.html', {'courses': courses})

from .models import Course
from .forms import CourseForm
from django.shortcuts import render, redirect

def course_form_add(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)

            # Get the 'is_active' value from the form (radio button)
            is_active_value = request.POST.get('is_active', '1')
            course.is_active = is_active_value == '1'

            course.save()
            user = get_logged_in_user(request)
            log_activity(request.user, 'added', course)


            return redirect('course_form_list')
    else:
        form = CourseForm()
    
    return render(request, 'master/course_form.html', {'form': form})

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
def course_form_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save(commit=False)

            # Handle is_active from radio button
            is_active_value = request.POST.get('is_active', '1')
            course.is_active = is_active_value == '1'

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
            user = get_logged_in_user(request)
            log_activity(request.user, 'added', semester)

            
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
            semester=form.save()

            user = get_logged_in_user(request)
            log_activity(user, 'updated', semester)

            return redirect('semester_form_list')
    else:
        form = SemesterForm(instance=semester)
    return render(request, 'master/semester_form.html', {'form': form, 'mode': 'edit'})
 
def semester_form_view(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    form = SemesterForm(instance=semester)
    for field in form.fields.values():
        field.widget.attrs['readonly'] = True
        field.widget.attrs['disabled'] = True
    return render(request, 'master/semester_form.html', {'form': form, 'mode': 'view'})
 
def semester_form_delete(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    if request.method == 'POST':
        semester.delete()
        user = get_logged_in_user(request)
        log_activity(request.user, 'deleted', semester)
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

def transport_form_add(request):
    if request.method == 'POST':
        form = TransportForm(request.POST)
        if form.is_valid():
            transport = form.save()

            # ✅ Log creation activity
            user = get_logged_in_user(request)
            log_activity(user, 'created', transport)

            return redirect('transport_form_list')
    else:
        form = TransportForm()
    return render(request, 'master/transport_form.html', {'form': form})



from django.shortcuts import render, get_object_or_404, redirect
from .models import Transport
from .forms import TransportForm

# ✅ View Transport (Read-only)
def transport_form_view(request, pk):
    transport = get_object_or_404(Transport, pk=pk)

    if request.method == 'POST':
        # Just in case someone manually sends a POST request, prevent saving
        return redirect('transport_form_list')
    else:
        form = TransportForm(instance=transport)
        for field in form.fields.values():
            field.disabled = True  # Disable fields for read-only view

    return render(request, 'master/transport_form.html', {
        'form': form,
        'is_view': True  # Template uses this to hide Save button
    })

# ✅ Edit Transport
from core.utils import get_logged_in_user, log_activity  # ✅ Ensure these are imported

def transport_form_edit(request, pk):
    transport = get_object_or_404(Transport, pk=pk)
    if request.method == 'POST':
        form = TransportForm(request.POST, instance=transport)
        if form.is_valid():
            form.save()

            # ✅ Log update activity
            user = get_logged_in_user(request)
            log_activity(user, 'updated', transport)

            return redirect('transport_form_list')
    else:
        form = TransportForm(instance=transport)

    return render(request, 'master/transport_form.html', {
        'form': form,
        'is_view': False  # Allow saving
    })


# Delete View
def transport_form_delete(request, pk):
    transport = get_object_or_404(Transport, pk=pk)
    transport.delete()
    user = get_logged_in_user(request)
    log_activity(user, 'deleted', transport)

    return redirect('transport_form_list')


# views.py
from django.shortcuts import render
from django.utils import timezone
from .models import AcademicEvent
import calendar
from datetime import date

def calendar_form(request):
    today = timezone.localdate()

    # Get month/year from query params or default to current
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    cal = calendar.Calendar(firstweekday=6)
    month_days = list(cal.monthdayscalendar(year, month))
    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    # All future events
    future_events_qs = AcademicEvent.objects.filter(date__gte=today).order_by('date', 'time')
    future_events = list(future_events_qs.values('id', 'title', 'date', 'time', 'description', 'event_type'))

    # Calculate previous/next month/year
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

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

