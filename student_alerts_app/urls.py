from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse
from master import views
from master.views import custom_login_view


# ✅ Safe root view (handles '/')
def home_view(request):
    return HttpResponse("Student Alerts Backend is running.")

# ✅ Health check endpoint (handles '/actuator/health/')
def actuator_health(request):
    return JsonResponse({"status": "UP"})

urlpatterns = [
    # ✅ Safe default homepage
    path('', views.custom_login_view, name='login'),

    # Admin route
    path('admin', admin.site.urls),

    # Include app routes
    path('', include('master.urls')),
    path('', include('admission.urls')),
    path('', include('attendence.urls')),
    path('', include('license.urls')),
    path('', include('timetable.urls')),  # ✅ removed duplicate
    path('', include('lms.urls')),
    path('', include('core.urls')),
    
    # Other routes
    path('fees', include('fees.urls')),
    path('healthz/', lambda r: HttpResponse("ok")),
    path('actuator/health/', actuator_health),
]

# ✅ Serve media files (only in development)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)






