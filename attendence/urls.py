# urls.py
from django.urls import path
from . import views
from .views import student_attendance_form_view ,student_attendance_list

urlpatterns = [
   
    path('add-period/', views.add_period, name='add_period'),
    path('periods/', views.period_list, name='period_list'),
         path('attendance_list/', views.attendance_list, name='attendance_list'),
         path('delete/<int:id>/', views.attendance_delete, name='attendance_delete'),

    path('attendance/form/', views.attendance_entry, name='attendance_entry'),
    path('attendance/view/<int:pk>/', views.attendance_view, name='attendance_view'),
    path('attendance/edit/<int:pk>/', views.attendance_edit, name='attendance_edit'),
 path('attendance/delete/<int:pk>/', views.attendance_delete, name='attendance_delete'),


    path('api/employee/<int:pk>/', views.employee_detail_api),
    path('attendance/settings/', views.attendance_settings_view, name='attendance_settings_view'),
     path('attendance-dashboard', views.attendance_dashboard, name='attendance_dashboard'),
     path('reports/', views.attendance_report, name='attendance_report'),

     
     path('attendance/list/', views.student_attendance_list, name='student_attendance_list'),
    path('student-attendance/form/', views.student_attendance_form_view, name='student_attendance_form'),
]

