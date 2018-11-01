import os

from collections import OrderedDict

import raven
from copy import deepcopy
from utils.shortcuts import get_env

production_env = get_env("OJ_ENV", "dev") == "production"

DEBUG = get_env('DEBUG', False)

BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = "/data"


# Applications
VENDOR_APPS = (
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'raven.contrib.django.raven_compat',
    'corsheaders',

    # The following is added for DGUTOJ.
    'django_filters',
    'mptt',
    'django_extensions',
    'markdown',
)
LOCAL_APPS = (
    'account',
    'announcement',
    'conf',
    'problem',
    'contest',
    'utils',
    'submission',
    'options',
    'judge',

    # The following is added for DGUTOJ.
    'apps.xproblem',
    'apps.collection',
    'apps.vote',
    'apps.user',
    'apps.comment',
    'apps.delegation',
)

INSTALLED_APPS = VENDOR_APPS + LOCAL_APPS

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'account.middleware.APITokenAuthMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'account.middleware.AdminRoleRequiredMiddleware',
    'account.middleware.SessionRecordMiddleware',
    # 'account.middleware.LogSqlMiddleware',
)
ROOT_URLCONF = 'dgutoj.urls'

CORS_ORIGIN_ALLOW_ALL = True

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
WSGI_APPLICATION = 'dgutoj.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/public/'

AUTH_USER_MODEL = 'account.User'

TEST_CASE_DIR = os.path.join(DATA_DIR, "test_case")
LOG_PATH = os.path.join(DATA_DIR, "log")

AVATAR_URI_PREFIX = "/public/avatar"
AVATAR_UPLOAD_DIR = f"{DATA_DIR}{AVATAR_URI_PREFIX}"

UPLOAD_PREFIX = "/public/upload"
UPLOAD_DIR = f"{DATA_DIR}{UPLOAD_PREFIX}"

LOGGING_HANDLERS = ['console', 'sentry'] if production_env else ['console']
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] - [%(levelname)s] - [%(name)s:%(lineno)d]  - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'formatter': 'standard'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': LOGGING_HANDLERS,
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': LOGGING_HANDLERS,
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': LOGGING_HANDLERS,
            'level': 'WARNING',
            'propagate': True,
        }
    },
}

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'apps.utils.views.custom_exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'apps.utils.pagination.MyPagination',
    'PAGE_SIZE': 10,
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': get_env("POSTGRES_HOST", "oj-postgres"),
        'PORT': get_env("POSTGRES_PORT", "5432"),
        'NAME': get_env("POSTGRES_DB"),
        'USER': get_env("POSTGRES_USER"),
        'PASSWORD': get_env("POSTGRES_PASSWORD")
    }
}

REDIS_CONF = {
    "host": get_env("REDIS_HOST", "oj-redis"),
    "port": get_env("REDIS_PORT", "6379")
}

ALLOWED_HOSTS = ['*']

if DEBUG:
    STATICFILES_DIRS = [os.path.join(DATA_DIR, "public")]
else:
    STATIC_ROOT = os.path.join(DATA_DIR, "public")

REDIS_URL = "redis://%s:%s" % (REDIS_CONF["host"], REDIS_CONF["port"])


def redis_config(db):
    def make_key(key, key_prefix, version):
        return key

    return {
        "BACKEND": "utils.cache.MyRedisCache",
        "LOCATION": f"{REDIS_URL}/{db}",
        "TIMEOUT": None,
        "KEY_PREFIX": "",
        "KEY_FUNCTION": make_key
    }


CACHES = {
    "default": redis_config(db=1)
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CELERY_RESULT_BACKEND = f"{REDIS_URL}/2"
BROKER_URL = f"{REDIS_URL}/3"
CELERY_TASK_SOFT_TIME_LIMIT = CELERY_TASK_TIME_LIMIT = 180
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
RAVEN_CONFIG = {
    'dsn': 'https://b200023b8aed4d708fb593c5e0a6ad3d:1fddaba168f84fcf97e0d549faaeaff0@sentry.io/263057'
}

IP_HEADER = "HTTP_X_REAL_IP"


SECRET_KEY = get_env('SECRET_KEY')

# Validate or delete problem base on votes count.
VOTE_SCORE_INVALID_TO_VALID = get_env('VOTE_SCORE_INVALID_TO_VALID')
VOTE_SCORE_INVALID_TO_DELETE = get_env('VOTE_SCORE_INVALID_TO_DELETE')
VOTE_SCORE_VALID_TO_DELETE = get_env('VOTE_SCORE_VALID_TO_DELETE')
MAX_VOTES_BEFORE_TRIGGER = get_env('MAX_VOTES_BEFORE_TRIGGER')

# Dynamically update difficulty of problem.
DIFFICULTY_BASE_SUBMISSIONS_COUNT = get_env(
    'DIFFICULTY_BASE_SUBMISSIONS_COUNT')
DIFFICULTY_RATE_MAP = OrderedDict({
    'Low': get_env('DIFFICULTY_RATE_MAP_LOW'),
    'Mid': get_env('DIFFICULTY_RATE_MAP_MID'),
    'High': get_env('DIFFICULTY_RATE_MAP_HIGH'),
})

# Regular user can only create a problem if she haven't run out of her
# invalid problems quota.
INVALID_PROBLEMS_QUOTA = get_env('INVALID_PROBLEMS_QUOTA')

# Authentication for DGUT
OJ_DOMAIN = get_env('OJ_DOMAIN')
APP_ID = get_env('APP_ID')
DGUT_LOGIN = get_env('DGUT_LOGIN')
DGUT_CHECK_TOKEN = get_env('DGUT_CHECK_TOKEN')
DGUT_LOGOUT = get_env('DGUT_LOGOUT')
DGUT_USER_INFO = get_env('DGUT_USER_INFO')
DGUT_APP_SECRET = get_env('DGUT_APP_SECRET')

# Vote Rank Algorithm
# Use 1.96 for a confidence level of 0.95.
VOTE_RANK_Z_SCORE = get_env('VOTE_RANK_Z_SCORE')
