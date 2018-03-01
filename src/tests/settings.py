"""
Django settings file only for use in testing.

See:
    https://docs.djangoproject.com/en/dev/topics/testing/advanced/#using-the-django-test-runner-to-test-reusable-applications

"""

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'fake-key'


INSTALLED_APPS = [
    'django_createsuperwithpass',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'tests'
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'PASSWORD': 'tester',
        'PORT': '3306',
        'USER': 'tester',
    }
}


USE_TZ = False
TIME_ZONE = 'UTC'
