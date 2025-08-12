from django.urls import path
from . import views
# from .views import send_whatsapp_message_view



urlpatterns = [
    path('login', views.custom_login_view, name='login'),






    
    path('choose-passcode', views.choose_passcode_view, name='choose_passcode_view'),
    path('password-reset', views.password_reset_view, name='password_reset_view'),
    path('verify-passcode', views.verify_passcode_view, name='verify_passcode_view'),

    # path('dashboard/', views.dashboard_router_view, name='dashboard_router_view'),
   path('dashboard', views.dashboard_view, name='dashboard_view'),
  path('dashboard2', views.dashboard_view2, name='dashboard_view2'),
  path('dashboard3', views.dashboard_view3, name='dashboard_view3'),
  path('dashboard4', views.dashboard_view4, name='dashboard_view4'),
    path('logout', views.logout_view, name='logout'),
    path('', views.custom_login_view, name='login'),  # Redirect root path to login
     path('student-data', views.student_data_view, name='student_data_view'),

      path('Users/add', views.add_user, name='add_user'),



           path('Users/edit/<int:user_id>', views.edit_user, name='edit_user'),
  path('Users/view/<int:user_id>', views.view_user, name='view_user'),
path('Users/delete/<int:user_id>', views.delete_user, name='delete_user'),

 path('Users', views.user_list, name='user_list'),
 # ✅ Use query param instead (?user_id=3)
 path('User-rights/<int:user_id>', views.user_rights_view, name='user_rights_view'),
        # path('send-message/', views.send_whatsapp_message_view, name='send_message'),  # Correct function name
    # path('send-whatsapp-message/', send_whatsapp_message_view, name='send_whatsapp_message'),
    # path('incoming-whatsapp/', views.incoming_whatsapp, name='incoming_whatsapp'), 
      path('messages', views.compose_message, name='compose_message'),
      path('message-history', views.message_history_view, name='message_history_view'),
       path('resend/<int:message_id>', views.resend_message_view, name='resend_message'),

       
      
      path('student/<int:student_id>/promote', views.promote_student, name='promote_student'),
path('student/profile/<int:student_id>', views.student_profile_view, name='student_profile'),
    path('student-database', views.student_database, name='student_database'),
    path('students/form/<int:pk>', views.master_student_view, name='master_student_view'),
    path('student/<int:pk>/edit', views.master_student_edit, name='master_student_edit'),

         path("master-dashboard", views.master_dashboard, name="master_dashboard"),


       #  path('Employees/', views.employee_list_view, name='employee_list_view'),
       # path('Employee/add/', views.employee_add_view, name='employee_add_view'),

    path('main', views.blank_view, name='blank_view'),





     path('communication', views.communication_dashboard, name='communication_dashboard'),


    path('transport', views.transport_form_list, name='transport_form_list'),
    path('transport/add', views.transport_form_add, name='transport_form_add'),
    path('transport/view/<int:pk>', views.transport_form_view, name='transport_form_view'),
    path('transport/edit/<int:pk>', views.transport_form_edit, name='transport_form_edit'),
    path('transport/delete/<int:pk>', views.transport_form_delete, name='transport_form_delete'),



   

    path('semesters', views.semester_form_list, name='semester_form_list'),
  path('semester-form/add', views.semester_form_add, name='semester_form_add'),
  path('semester-form/edit/<int:pk>', views.semester_form_edit, name='semester_form_edit'),
  path('semester-form/view/<int:pk>', views.semester_form_view, name='semester_form_view'),
  path('semester-form/delete/<int:pk>', views.semester_form_delete, name='semester_form_delete'),
   path('ajax/get_semester_numbers', views.get_semester_numbers, name='get_semester_numbers'),



         path('program-types', views.course_type_list, name='course_type_list'),
    path('program-types/add', views.course_type_add, name='course_type_add'),
      
   path('program-types/<int:pk>/view', views.course_type_view, name='course_type_view'),
        path('program-types/<int:pk>/edit', views.course_type_edit, name='course_type_edit'),
   path('program-types/<int:pk>/delete', views.course_type_delete, name='course_type_delete'),
   # path('program-types/<int:pk>/', views.course_type_detail, name='course_type_detail'),

    path('combinations', views.course_form_list, name='course_form_list'),
    path('combinations/add', views.course_form_add, name='course_form_add'),
  
    path('combinations/<int:pk>/view', views.course_form_view, name='course_form_view'),

    path('combinations/edit/<int:pk>', views.course_form_edit, name='course_form_edit'),
    path('combinations/delete/<int:pk>', views.course_form_delete, name='course_form_delete'),
     path('validate-course', views.validate_course, name='validate_course'),


    path('employee-list', views.employee_list, name='employee_list'),
      path('ajax/get_subjects_by_course_and_semester', views.get_subjects_by_course_and_semester, name='get_subjects_by_course_and_semester'),
         path('employee-dashbaord', views.employee_dashboard, name='employee_dashboard'),
path('employee-add', views.employee_form_add, name='employee_form_add'),
 path('employee/edit/<int:pk>', views.employee_form_edit, name='employee_form_edit'),
  path('employee/delete/<int:pk>', views.employee_form_delete, name='employee_form_delete'),
  path('employee/view/<int:pk>', views.employee_form_view, name='employee_form_view'),

      path('calendar', views.calendar_form, name='calendar_form'),
   path('add', views.add_event_view, name='add_event'),


   
    path('get-semesters-by-course', views.get_semesters_by_course, name='get_semesters_by_course'),
    path('subjects', views.subject_form_list, name='subject_form_list'),
    path('subject/add', views.subject_form_add, name='subject_form_add'),
    # path('subject/get-faculties/', views.get_faculties_by_subject, name='get_faculties_by_subject'),
      path('subject/view/<int:pk>', views.subject_form_view, name='subject_form_view'),

       path('subject/edit/<int:pk>', views.subject_form_edit, name='subject_form_edit'),
    path('subject/delete/<int:pk>', views.subject_form_delete, name='subject_form_delete'),

       path('upload', views.upload_excel, name='upload_excel'),
path('send/<int:msg_id>', views.send_message, name='send_message'),
path('delete/<int:contact_id>', views.delete_contact, name='delete_contact'),
       # path('ajax/get_semester_options/', views.get_semester_options, name='get_semester_options'),

       path('ajax/check-program-type', views.check_program_type_name, name='check_program_type_name'),





        path('academic-year', views.academic_year_list, name='academic_year_list'),
 path('academic-year/add', views.academic_year_create, name='academic_year_add'),
 path('academic-year/edit/<int:pk>', views.academic_year_edit, name='academic_year_edit'),
 path('academic-year/delete/<int:pk>', views.academic_year_delete, name='academic_year_delete'),


 
  path('fees', views.fee_detail_list, name='fee_detail_list'),
    path('fees/<int:pk>/view', views.fee_detail_view, name='fee_detail_view'),
    path('fees/add', views.fee_detail_create, name='fee_detail_create'),
    path('fees/<int:pk>/edit', views.fee_detail_edit, name='fee_detail_edit'),
    path('fees/<int:pk>/delete', views.fee_detail_delete, name='fee_detail_delete'),
    path('ajax/get-program-type', views.get_program_type_by_combination, name='ajax_get_program_type'),
path('ajax/load-combinations', views.load_combinations, name='ajax_load_combinations'),


  path('promotion-history', views.promotion_history_list, name='promotion_history_list'),
    path('promotion-history/edit/<int:pk>', views.promotion_history_edit, name='promotion_history_edit'),
    path('promotion-history/delete/<int:pk>', views.promotion_history_delete, name='promotion_history_delete'),


    # fee type
  path('fee-types', views.fee_type_list, name='fee_type_list'),
      path('check-fee-type-name', views.check_fee_type_name, name='check_fee_type_name'),
  path('fee-types/add', views.fee_type_add, name='fee_type_add'),
  path('fee-types/<int:pk>/edit', views.fee_type_edit, name='fee_type_edit'),
  path('fee-types/<int:pk>/view', views.fee_type_view, name='fee_type_view'),
  path('fee-types/<int:pk>/delete', views.fee_type_delete, name='fee_type_delete'),
]
