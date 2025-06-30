from django.urls import path
from . import views



urlpatterns = [
    
    path('dashboard-timetable/', views.timetable_dashboard, name='timetable_dashboard'),

   path('timetable/daily/', views.daily_timetable_view, name='daily_timetable'),

    path('weekly/<int:course_id>/<int:semester_number>/', views.weekly_timetable_view, name='weekly_timetable'),
    # path('faculty/<int:faculty_id>/', views.faculty_timetable_view, name='faculty_timetable'),
   
     path('<int:course_id>/<int:semester_number>/weekly/', views.weekly_timetable_view, name='weekly_timetable'),
     path('get-faculty/', views.get_faculty_by_subject, name='get_faculty_by_subject'),
    path('entry/add/', views.add_timetable_entry, name='add_timetable_entry'),
    path('entry/edit/<int:entry_id>/', views.edit_timetable_entry, name='edit_timetable_entry'),
    path('entry/delete/<int:entry_id>/', views.delete_timetable_entry, name='delete_timetable_entry'),

    path('timetable/faculty-classes/', views.faculty_classes_table, name='faculty_classes_table'),
  
]

