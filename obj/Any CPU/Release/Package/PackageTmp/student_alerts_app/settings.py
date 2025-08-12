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
SECRET_KEY = '6e470ba8-802a-428f-b168-40d4eadee009'
 
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True




ALLOWED_HOSTS = ['192.168.10.182', 'localhost', '127.0.0.1', '122.166.213.68']

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
     'fees'
   

]

# Middleware framework
# https://docs.djangoproject.com/en/2.1/topics/http/middleware/
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'student_alerts_app.wsgi.application'
# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
     'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'institute_db1',  # Replace with your actual database name
        'USER': 'root',     # Replace with your MySQL username
        'PASSWORD': 'root',  # Replace with your MySQL password
        'HOST': 'localhost',           # Keep as 'localhost' if running MySQL locally
        'PORT': '3306',                # Default MySQL port
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET NAMES 'utf8mb4'"
        },
    }
}

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

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = posixpath.join(*(BASE_DIR.split(os.path.sep) + ['static']))
TIME_ZONE = 'Asia/Kolkata'
USE_TZ = True




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




