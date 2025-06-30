# master/context_processors.py

from .models import UserCustom

def permissions_context(request):
    user_id = request.session.get('user_id')
    allowed_forms = []
    can_access_all = False
    user = None

    if user_id:
        try:
            user = UserCustom.objects.get(id=user_id)
            can_access_all = user.can_access_all

            if user.can_access_message_form:
                 allowed_forms.append('message_history_view')
                 allowed_forms.append('compose_message')
                 allowed_forms.append('student_data_view')
            if user.can_access_admission_form:
                allowed_forms.append('admission_form')
                allowed_forms.append('admission_list')
            if user.can_access_enquiry_form_view:
                allowed_forms.append('enquiry1_create') 
                allowed_forms.append('master_student_list')
                allowed_forms.append('enquiry_list')
                allowed_forms.append('enquiry_print_form')

            if user.can_access_dashboard2:
                allowed_forms.append('dashboard_view2')

                

           
            if user.can_access_shortlisted_students_view:
                allowed_forms.append('shortlisted_students_view')
            if user.can_access_shortlist_display:
                allowed_forms.append('shortlist_display')
            if user.can_access_degree_admission_form:
                allowed_forms.append('degree_admission_form')
                allowed_forms.append('degree_admission_list')
            

        except UserCustom.DoesNotExist:
            user = None

    return {
        'allowed_forms': allowed_forms,
        'user': user,
        'can_access_all': can_access_all,
    }


