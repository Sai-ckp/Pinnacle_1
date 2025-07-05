from django.urls import path
from . import views



urlpatterns = [
    
    path('timetable/', views.timetable_dashboard, name='timetable_dashboard'),

   path('daily/', views.daily_timetable, name='daily_timetable'),

    path('weekly/<int:course_id>/<int:semester_number>/', views.weekly_timetable_view, name='weekly_timetable'),
    # path('faculty/<int:faculty_id>/', views.faculty_timetable_view, name='faculty_timetable'),
   
     path('<int:course_id>/<int:semester_number>/weekly/', views.weekly_timetable_view, name='weekly_timetable'),
     path('get-faculty/', views.get_faculty_by_subject, name='get_faculty_by_subject'),
    path('timetable-entry-add/', views.timetable_form_add, name='timetable_form_add'),
  
   path('timetable-entry/edit/<int:entry_id>/', views.timetable_form_edit, name='timetable_form_edit'),
   path('timetable-entrye/delete/<int:substitution_id>/', views.timetable_form_delete, name='timetable_form_delete'),
     path('timetable-entry/view/<int:entry_id>/', views.timetable_form_view, name='timetable_form_view'),
    path('faculty-classes/', views.faculty_classes_table, name='faculty_classes_table'),

     # path('timetable/edit/<int:entry_id>/', views.edit_timetable_entry, name='edit_timetable_entry'),
  
]

