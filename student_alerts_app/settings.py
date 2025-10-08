"""
Django settings for student_alerts_app project.

Based on 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import posixpath


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', default='')  # Use environment variable for security 
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False




ALLOWED_HOSTS = ['192.168.10.221', 'localhost', '127.0.0.1', '122.166.213.68',
                os.getenv('WEBSITE_HOSTNAME', 'pinnaclecollege-c4evf7g2afg2hrfj.centralindia-01.azurewebsites.net'),]

# Application references
# https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-INSTALLED_APPS
INSTALLED_APPS = [
    'master',
    'admission',
    'license',
    'attendence',
    'timetable',
    # Add your apps here to enable them
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'student_alerts_app',
    'core',
     'fees',
     'transport',
     'lms',

   

]

# Middleware framework
# https://docs.djangoproject.com/en/2.1/topics/http/middleware/
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For multilingual support'
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'license.middleware.check_license.LicenseCheckMiddleware',
]

ROOT_URLCONF = 'student_alerts_app.urls'

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Template configuration
# https://docs.djangoproject.com/en/2.1/topics/templates/
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'student_alerts_app','templates')], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'master.context_processors.user_form_permissions',
                 'lms.context_processors.student_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'student_alerts_app.wsgi.application'
# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
import os

print("Testing environment variables:")
print("DB_NAME =", os.getenv('DB_NAME'))
print("DB_USER =", os.getenv('DB_USER'))
print("DB_PASSWORD =", os.getenv('DB_PASSWORD'))
print("DB_HOST =", os.getenv('DB_HOST'))
print("DB_PORT =", os.getenv('DB_PORT'))


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),      # Azure environment variable for database name
        'USER': os.getenv('DB_USER'),      # Azure environment variable for username
        'PASSWORD': os.getenv('DB_PASSWORD'),  # Azure environment variable for password
        'HOST': os.getenv('DB_HOST'),      # Azure environment variable for host, e.g. yourserver.postgres.database.azure.com
        'PORT': os.getenv('DB_PORT', '5432'),  # Azure environment variable for port, default to 5432
        'OPTIONS': {
            'sslmode': 'require',          # Required for secure connection to Azure PostgreSQL
        },
    }
}



# Default to BigAutoField to avoid migration warnings
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Optional: For debugging to verify variables are loaded correctly, remove in production
print("Database Configurations:")
print("DB_NAME:", os.getenv('DB_NAME'))
print("DB_USER:", os.getenv('DB_USER'))
print("DB_HOST:", os.getenv('DB_HOST'))
print("DB_PORT:", os.getenv('DB_PORT', '5432'))




# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
# settings.py

LOGIN_REDIRECT_URL = 'license_check_view'
LOGOUT_REDIRECT_URL = 'login'





import os

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = '/static/'
# Use Whitenoise Storage backend that skips decoding binaries
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
TIME_ZONE = 'Asia/Kolkata'
USE_TZ = True

# Instruct Whitenoise to skip compression for binary static files
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = [
    '.jpg', '.jpeg', '.png', '.gif', '.webp',
    '.woff', '.woff2', '.ttf', '.eot', '.otf',
    '.svg', '.ico', '.mp4', '.webm'
]



# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'AC5113cf0f0ca61f2492bc7855117717b7')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '2725a24faf3d85f4f9a690e32fd81152')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', '+14155238886')
TWILIO_SMS_NUMBER = os.getenv('TWILIO_SMS_NUMBER', '+12568573853')
 
EMAIL_PROVIDERS = {
    'postmark': {
        'API_TOKEN': '82d1585c-84b7-4250-a38c-2c10b97d6e3c ',
        'FROM_EMAIL': 'nischitha@ckpsoftware.com',
    },
    'sendgrid': {
        'API_TOKEN': 'your-sendgrid-api-key-here',
        'FROM_EMAIL': 'verified-email@yourdomain.com',
    },
}


# Choose which provider to use globally or per use case
EMAIL_PROVIDER_NAME = 'postmark'  # or 'sendgrid'



MSGKART_API_KEY = "3652fa38504b4d018052987ff493ea6e"
MSGKART_EMAIL = "pscm@ckpsoftware.com"
MSGKART_PHONE_ID = "677200268805951"
MSGKART_ACCOUNT_ID = "1079493607572130"
MSGKART_BASE_URL = "https://alb-backend.msgkart.com"


















