
from django.urls import path
from . import views

 
urlpatterns = [
   
    path('student-login/', views.student_login_view, name='student_login_view'),
    path('student/logout/', views.student_logout, name='student_logout'),
 path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
 path('student/set-password/', views.student_set_password, name='student_set_password'),
path('student/set-passcode/', views.student_set_passcode, name='student_set_passcode'),
path('student/password-reset/', views.student_password_reset_view, name='student_password_reset_view'),

    path('student/attendance/', views.my_attendance_view, name='my_attendance_view'),
    path('student/fees/',views.my_fees_view, name='my_fees_view'),
    path('student/profile/', views.student_profile_view, name='student_profile_view'),

    path('student/assignments/', views.my_assignments_view, name='my_assignments_view'),
    path('submit-assignment/<int:assignment_id>/', views.submit_assignment_view, name='submit_assignment'),

    #
    path('assignments/add/', views.create_assignment, name='create_assignment'),
    path('Assignments_List/', views.assignment_list, name='assignment_list'),
    path('assignments/delete/<int:pk>/', views.delete_assignment, name='delete_assignment'),
    path('assignments/<int:pk>/edit/', views.edit_assignment, name='edit_assignment'),
    path('assignments/<int:pk>/view/', views.view_assignment, name='view_assignment'),

    #lib
        path('library', views.book_list, name='book_list'),
    path('library/add', views.add_book, name='add_book'),
    path('library/view/<int:pk>', views.book_view, name='book_view'),
    path('library/edit/<int:pk>', views.book_update, name='book_update'),
    path('library/delete/<int:pk>', views.book_delete, name='book_delete'),

        path('books/<int:book_id>/borrow-details/', views.book_borrow_details, name='book_borrow_details'),

     path('borrow/new/', views.borrow_book_view, name='borrow_book'),
path('borrow/<int:record_id>/details/', views.borrow_record_details, name='borrow_record_details'),

    #this is pdf 
    # path('study-materials/', views.employee_study_material_list, name='employee_study_material_list'),
    # path('study-materials/create/', views.create_or_edit_study_material, name='create_or_edit_study_material'),
    # path('study-materials/edit/<int:pk>/', views.create_or_edit_study_material, name='create_or_edit_study_material'),
    # path('study-materials/delete/<int:pk>/', views.delete_employee_study_material, name='delete_employee_study_material'),

    path('study-material/create/', views.create_study_material, name='create_study_material'),
    path('study-material/edit/<int:pk>/', views.edit_study_material, name='edit_study_material'),
    # optionally: delete
    path('study-material/delete/<int:pk>/', views.delete_employee_study_material, name='delete_employee_study_material'),
    # optionally: list
    path('study-material/list/', views.employee_study_material_list, name='employee_study_material_list'),

    #This is exam
    path('exam/create/', views.create_exam, name='create_exam'),
    path('exam/', views.exam_list, name='exam_list'),
    path('exam/<int:pk>/edit/', views.edit_exam, name='edit_exam'),
    path('exam/<int:pk>/view/', views.view_exam, name='view_exam'),
    path('exam/<int:pk>/delete/', views.delete_exam, name='delete_exam'),

      path('calendar/form', views.student_calendar_form, name='student_calendar_form'),
   path('event', views.academic_events, name='academic_events'),

]



