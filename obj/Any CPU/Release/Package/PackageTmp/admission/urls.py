from django.urls import path
from .views import generate_qr_dynamic
from . import views

urlpatterns = [
      path('admission/form/', views.admission_form, name='admission_form'),  # for blank form
 path('admission/form/<str:enquiry_no>/', views.admission_form, name='admission_form'),  # for pre-filled form

     path('admission/list/', views.admission_list, name='admission_list'),

     path('admissions/pu/<int:pk>/edit/', views.edit_pu_admission, name='edit_pu_admission'),


       path('admission/degree/', views.degree_admission_form, name='degree_admission_form'),  # blank form
    path('admission/degree/<str:enquiry_no>/', views.degree_admission_form, name='degree_admission_form'),  # prefilled form\
    path('admissions/degree/<int:pk>/edit/', views.edit_degree_admission, name='edit_degree_admission'),    


path('enquiry/convert/<str:enquiry_no>/', views.convert_enquiry, name='convert_enquiry'),



      path('degree-admission-list/', views.degree_admission_list, name='degree_admission_list'),
     path('shortlisted/', views.shortlisted_students_view, name='shortlisted_students_view'),
    path('approve/<str:stream>/<int:student_id>/', views.approve_student, name='approve_student'),
     # path('enquiry/', views.enquiry_form_view, name='enquiry_form'),
    path('shortlist/', views.shortlist_display, name='shortlist_display'),

    path('pu-fee/<int:admission_id>/', views.pu_fee_detail_form, name='pu_fee_detail_form'),
    path('degree-fee/<int:admission_id>/', views.degree_fee_detail_form, name='degree_fee_detail_form'),


    #    path('enquiry1/new/', views.enquiry1_create, name='enquiry1_form'),
    # path('enquiry1/create/', views.enquiry1_create, name='enquiry1_create'),
    #   path('enquiries/', views.enquiry_list, name='enquiry_list'),
    path('ajax/load-courses/', views.load_courses, name='ajax_load_courses'),
     path('api/enquiry-lookup/', views.enquiry_lookup, name='enquiry_lookup'),
     path('degree-enquiry-lookup/', views.degree_enquiry_lookup, name='degree_enquiry_lookup'),


    # path('fee/view/<int:fee_id>/', views.view_fee_detail, name='view_fee_detail'),
       path('admission/send_bulk_emails/', views.send_bulk_emails, name='send_bulk_emails'),

   # path('admission/create-logins/',views. create_student_logins, name='create_student_logins'),

    path('admission/student-login/', views.student_login, name='student_login'),
    path('admissions/reset-password/', views.reset_password, name='reset_password'),


        #Fee
   
    path('get_student_details/', views.get_student_details, name='get_student_details'),
    path('generate_qr_dynamic', generate_qr_dynamic, name='generate_qr_dynamic'),
    path('receipt/<int:student_id>/pdf/', views.generate_fee_receipt_pdf, name='generate_fee_receipt_pdf'), # PDF Receipt

    path('save-payment/', views.save_payment, name='save_payment'),

    path('payment-history/', views.payment_history, name='payment_history'),
    path('receipt/student/<int:pk>/', views.download_student_receipt, name='download_student_receipt'),
    path('receipt/admin/<int:pk>/', views.download_admin_receipt, name='download_admin_receipt'),

   path('enquiry-print-form/', views.enquiry_print_form, name='enquiry_print_form'),

      path('export-payments/', views.export_payments_excel, name='export_payments_excel'),
 #export all payments getting total paid and pending fee
   path('export-payments/', views.export_payments_excel, name='export_payments_excel'),

   path('admission/dashboard/', views.admission_dashboard, name='admission_dashboard'),

       path('pending-admissions/', views.pending_admissions, name='pending_admissions'),
    path('confirmed-admissions/', views.confirmed_admissions, name='confirmed_admissions'),
    path('generate-userid/<str:admission_no>/', views.generate_student_userid, name='generate_student_userid'),
    # urls.py

            #Fee
    path('student/create/', views.student_create, name='student_create'),
    path('student/edit/<str:admission_no>/', views.student_edit, name='student_edit'),
    path('student/list/', views.student_list, name='student_list'),





       path('view-enquiry/<str:enquiry_no>/', views.view_enquiry, name='view_enquiry'),

      # path('enquiry1/new/', views.enquiry1_create, name='enquiry1_form'),

       # path('enquiry2/new/', views.enquiry2_create, name='enquiry2_form'),

   path('enquiry1/create/', views.enquiry1_create, name='enquiry1_create'),
    path('enquiry2/create/', views.enquiry2_create, name='enquiry2_create'),



     path('enquiries/', views.enquiry_list, name='enquiry_list'),


      path('confiremd-enquiries/', views.converted_enquiry_list, name='converted_enquiry_list'),



      path('schedule_follow_up_form/', views.schedule_follow_up_form, name='schedule_follow_up_form'),
path('follow-list/', views.follow_up_list, name='follow_up_list'),
path('followup/<int:id>/update-status/', views.update_followup_status, name='update_followup_status'),
 # path('dashboard_view_follow_up/', views.dashboard_view_follow_up, name='dashboard_view_follow_up'),

   path('enquiry/dashboard/', views.enquiry_dashboard, name='enquiry_dashboard'),
   path('ajax/load-courses/', views.load_courses, name='ajax_load_courses'),
   path('ajax/load-courses-degree/', views.load_courses_degree, name='ajax_load_courses_degree'),
    path("admissions/reports/", views.reports, name="reports"),


      path('list-enquiries/', views.enquiry_list1, name='enquiry_list1'),
]


