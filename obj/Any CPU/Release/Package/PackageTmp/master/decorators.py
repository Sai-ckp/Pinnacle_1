
from django.shortcuts import redirect
from functools import wraps
from .models import User  # Change 'your_app' to the actual app name

def check_form_access(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_id = request.session.get('user_id')

            if not user_id:
                return redirect('login')  # Redirect to login if not authenticated

            user = User.objects.filter(id=user_id).first()
            if not user:
                return redirect('login')

            # Allow access if the user has all-access or specific permission
            if getattr(user, f'can_access_{permission_name}', False) or user.can_access_all:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('no_permission')  # You can create a "403" template
        return _wrapped_view
    return decorator


