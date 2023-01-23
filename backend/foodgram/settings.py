import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_ROOT = os.path.join(BASE_DIR, 'data')

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    default='tr61-8a=^d5nz=k!(4#!y_w*e$j7(1olf84%fz7^n5_@vak8)^'
)

DEBUG = os.getenv('IS_DEBUG', default=True)

ALLOWED_HOSTS = [os.getenv('ALLOWED_HOSTS', default='*')]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'users',
    'recipes',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'foodgram.wsgi.application'

if os.getenv('IS_SQLITE', default=False):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': os.getenv(
                'DB_ENGINE',
                default='django.db.backends.postgresql'),
            'NAME': os.getenv('DB_NAME', default='postgres'),
            'USER': os.getenv('POSTGRES_USER', default='postgres'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='postgres'),
            'HOST': os.getenv('DB_HOST', default='db'),
            'PORT': os.getenv('DB_PORT', default='5432')
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': ('django.contrib.auth.password_validation.' +
                 'UserAttributeSimilarityValidator'),
    },
    {
        'NAME': ('django.contrib.auth.password_validation.' +
                 'MinimumLengthValidator'),
    },
    {
        'NAME': ('django.contrib.auth.password_validation.' +
                 'CommonPasswordValidator'),
    },
    {
        'NAME': ('django.contrib.auth.password_validation.' +
                 'NumericPasswordValidator'),
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': ('recipes.pagination.' +
                                 'CustomPageNumberPagination'),
    'DEFAULT_FILTER_BACKENDS': [('django_filters.rest_framework.' +
                                'DjangoFilterBackend')]
}
DJOSER = {
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
    'PERMISSIONS': {
        'user': ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],
        'user_list': ['rest_framework.permissions.AllowAny'],
    },
    'SERIALIZERS': {
        'user': 'users.serializers.CustomUserSerializer',
        'current_user': 'users.serializers.CustomUserSerializer',
    },
}
AUTH_USER_MODEL = 'users.CustomUser'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

DUPLICATE_USERNAME_MESSAGE = {
    'errors': 'Пользователь с таким username уже зарегистрирован'
}
NAME_SLUG_LENGTH = 200
COLOR_FIELD_LENGTH = 7
USER_STRING_FIELD_LENGTH = 150
USER_EMAIL_FIELD_LENGTH = 254
TAG_SLUG_PATTERN = r'^[-a-zA-Z0-9_]+$'
TAG_SLUG_ERROR_MESSAGE = {
    'errors': f'Адрес тэга не соответствует шаблону: {TAG_SLUG_PATTERN}'
}

IS_AUTHOR_OR_ADMIN_ERROR_MESSAGE = {
    'errors': 'Изменять и удалять рецепт может его автор и администратор.'
}
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
BIG_FONT = 20
SMALL_FONT = 15
SIZE_BETWEEN_ROW = 40
PADDING_START_TEXT = 50
PADDING_START_NUMBER = 550
PADDING_BOTTOM_FIRST_ROW = 800
PADDING_BOTTOM_ROWS = 750
