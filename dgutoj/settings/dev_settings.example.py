import os
from collections import OrderedDict


BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '127.0.0.1',
        'PORT': 5432,
        'NAME': "onlinejudge",
        'USER': "<username>",
        'PASSWORD': '<password>'
    }
}

REDIS_CONF = {
    "host": "127.0.0.1",
    "port": "6379"
}


DEBUG = True

ALLOWED_HOSTS = ["*"]

DATA_DIR = f"{BASE_DIR}/data"

# Validate or delete problem base on votes count.
VOTES_TO_VALID = 20
VOTES_TO_DELETE = 10

# Dynamically update difficulty of problem.
DIFFICULTY_BASE_SUBMISSIONS_COUNT = 10
DIFFICULTY_RATE_MAP = OrderedDict({
    'Low': 1.00,
    'Mid': 0.50,
    'High': 0.25,
 })
