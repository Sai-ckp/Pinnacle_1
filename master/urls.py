from django.urls import path
from . import views
# from .views import send_whatsapp_message_view



urlpatterns = [
    path('login/', views.custom_login_view, name='login'),






    
    path('choose-passcode/', views.choose_passcode_view, name='choose_passcode_view'),
    path('password-reset/', views.password_reset_view, name='password_reset_view'),
    path('verify-passcode/', views.verify_passcode_view, name='verify_passcode_view'),

    # path('dashboard/', views.dashboard_router_view, name='dashboard_router_view'),
    path('dashboard/', views.dashboard_view, name='dashboard_view'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.custom_login_view, name='login'),  # Redirect root path to login
     path('student-data/', views.student_data_view, name='student_data_view'),

      path('Users/add/', views.add_user, name='add_user'),



           path('Users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
  path('Users/view/<int:user_id>/', views.view_user, name='view_user'),
path('Users/delete/<int:user_id>/', views.delete_user, name='delete_user'),

 path('Users/', views.user_list, name='user_list'),
 # ✅ Use query param instead (?user_id=3)
 path('User-rights/<int:user_id>/', views.user_rights_view, name='user_rights_view'),
        # path('send-message/', views.send_whatsapp_message_view, name='send_message'),  # Correct function name
    # path('send-whatsapp-message/', send_whatsapp_message_view, name='send_whatsapp_message'),
    # path('incoming-whatsapp/', views.incoming_whatsapp, name='incoming_whatsapp'), 
      path('messages/', views.compose_message, name='compose_message'),
      path('message-history/', views.message_history_view, name='message_history_view'),
       path('resend/<int:message_id>/', views.resend_message_view, name='resend_message'),

    path('student-database/', views.student_database, name='student_database'),
    path('students/form/<int:pk>/', views.master_student_view, name='master_student_view'),
    path('student/<int:pk>/edit/', views.master_student_edit, name='master_student_edit'),

         path("master-dashboard/", views.master_dashboard, name="master_dashboard"),


       #  path('Employees/', views.employee_list_view, name='employee_list_view'),
       # path('Employee/add/', views.employee_add_view, name='employee_add_view'),

    path('main/', views.blank_view, name='blank_view'),





     path('communication/', views.communication_dashboard, name='communication_dashboard'),


        path('transport/', views.transport_form_list, name='transport_form_list'),
    path('transport/add/', views.transport_form_add, name='transport_form_add'),
    path('transport/view/<int:pk>/', views.transport_form_view, name='transport_form_view'),
    path('transport/edit/<int:pk>/', views.transport_form_edit, name='transport_form_edit'),
    path('transport/delete/<int:pk>/', views.transport_form_delete, name='transport_form_delete'),



   


    path('semesters/', views.semester_form_list, name='semester_form_list'),
  path('semester-form/add/', views.semester_form_add, name='semester_form_add'),
  path('semester-form/edit/<int:pk>/', views.semester_form_edit, name='semester_form_edit'),
  path('semester-form/view/<int:pk>/', views.semester_form_view, name='semester_form_view'),
  path('semester-form/delete/<int:pk>/', views.semester_form_delete, name='semester_form_delete'),
   path('ajax/get_semester_numbers/', views.get_semester_numbers, name='get_semester_numbers'),



         path('program-types/', views.course_type_list, name='course_type_list'),
    path('program-types/add/', views.course_type_add, name='course_type_add'),
      
   path('program-types/<int:pk>/view/', views.course_type_view, name='course_type_view'),
        path('program-types/<int:pk>/edit/', views.course_type_edit, name='course_type_edit'),
   path('program-types/<int:pk>/delete/', views.course_type_delete, name='course_type_delete'),
   # path('program-types/<int:pk>/', views.course_type_detail, name='course_type_detail'),

    path('combinations/', views.course_form_list, name='course_form_list'),
    path('combinations/add/', views.course_form_add, name='course_form_add'),
  
    path('combinations/<int:pk>/view/', views.course_form_view, name='course_form_view'),

    path('combinations/edit/<int:pk>/', views.course_form_edit, name='course_form_edit'),
    path('combinations/delete/<int:pk>/', views.course_form_delete, name='course_form_delete'),


   

         path('employee-list', views.employee_list, name='employee_list'),
path('employee-add/', views.employee_form_add, name='employee_form_add'),
 path('employee/edit/<int:pk>/', views.employee_form_edit, name='employee_form_edit'),
  path('employee/delete/<int:pk>/', views.employee_form_delete, name='employee_form_delete'),
  path('employee/view/<int:pk>/', views.employee_form_view, name='employee_form_view'),

      path('calendar/', views.calendar_form, name='calendar_form'),
   path('add/', views.add_event_view, name='add_event'),



    path('subjects/', views.subject_form_list, name='subject_form_list'),
    path('subject/add/', views.subject_form_add, name='subject_form_add'),
    path('subject/get-faculties/', views.get_faculties_by_subject, name='get_faculties_by_subject'),
      path('subject/view/<int:pk>/', views.subject_form_view, name='subject_form_view'),

       path('subject/edit/<int:pk>/', views.subject_form_edit, name='subject_form_edit'),
    path('subject/delete/<int:pk>/', views.subject_form_delete, name='subject_form_delete'),

       path('upload/', views.upload_excel, name='upload_excel'),
path('send/<int:msg_id>/', views.send_message, name='send_message'),
path('delete/<int:contact_id>/', views.delete_contact, name='delete_contact'),
       # path('ajax/get_semester_options/', views.get_semester_options, name='get_semester_options'),


]
