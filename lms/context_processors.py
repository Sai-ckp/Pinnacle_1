
from admission.models import ConfirmedAdmission

def student_context(request):
    student_id = request.COOKIES.get('student_id')
    student = None

    if student_id:
        try:
            student = ConfirmedAdmission.objects.get(id=student_id)
        except ConfirmedAdmission.DoesNotExist:
            pass

    return {
        'logged_in_student': student
    }

