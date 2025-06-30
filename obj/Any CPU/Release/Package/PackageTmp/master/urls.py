from django.urls import path
from . import views
# from .views import send_whatsapp_message_view
from .views import calendar_view


urlpatterns = [
    path('login/', views.custom_login_view, name='login'),
    # path('dashboard/', views.dashboard_router_view, name='dashboard_router_view'),
    path('dashboard/', views.dashboard_view, name='dashboard_view'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.custom_login_view, name='login'),  # Redirect root path to login
     path('student-data/', views.student_data_view, name='student_data_view'),
        # path('send-message/', views.send_whatsapp_message_view, name='send_message'),  # Correct function name
    # path('send-whatsapp-message/', send_whatsapp_message_view, name='send_whatsapp_message'),
    # path('incoming-whatsapp/', views.incoming_whatsapp, name='incoming_whatsapp'), 
      path('messages/', views.compose_message, name='compose_message'),
      path('message-history/', views.message_history_view, name='message_history_view'),
       path('resend/<int:message_id>/', views.resend_message_view, name='resend_message'),

    path('students/', views.student_list, name='master_student_list'),
    path('students/<int:pk>/edit/', views.student_edit, name='master_student_edit'),
    path('students/<int:pk>/view/', views.student_view, name='student_view'),

       #  path('Employees/', views.employee_list_view, name='employee_list_view'),
       # path('Employee/add/', views.employee_add_view, name='employee_add_view'),

    path('main/', views.blank_view, name='blank_view'),
    # path('subjects/', views.subject_list, name='subject_list'),
    # path('subjects/add/', views.add_subject, name='add_subject'),



    path('semesters/', views.semester_list, name='semester_list'),
    path('semesters/add/', views.semester_add, name='semester_add'),
     path('ajax/get_semester_numbers/', views.get_semester_numbers, name='get_semester_numbers'),



         path('course-types/', views.course_type_list, name='course_type_list'),
    path('course-types/add/', views.course_type_create, name='course_type_create'),

    path('courses/', views.course_list, name='course_list'),
    path('courses/add/', views.course_create, name='course_create'),
    path('courses/edit/<int:pk>/', views.course_edit, name='course_edit'),
    path('courses/delete/<int:pk>/', views.course_delete, name='course_delete'),




     path('dashboard2/', views.dashboard_view2, name='dashboard_view2'),

         path('transport/', views.transport_list, name='transport_list'),
    path('transport/add/', views.transport_create, name='transport_create'),
   

      path('employee-list', views.employee_list, name='employee_list'),
  path('employee-add/', views.add_employee, name='add_employee'),


    path('calendar/', calendar_view, name='calendar'),
    path('add/', views.add_event_view, name='add_event'),


    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    path('subjects/get-faculties/', views.get_faculties_by_subject, name='get_faculties_by_subject'),

       path('upload/', views.upload_excel, name='upload_excel'),
path('send/<int:msg_id>/', views.send_message, name='send_message'),
path('delete/<int:contact_id>/', views.delete_contact, name='delete_contact'),
       # path('ajax/get_semester_options/', views.get_semester_options, name='get_semester_options'),


]
