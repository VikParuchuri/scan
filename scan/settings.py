from path import path
from datetime import timedelta
import os

DB_URL = 'sqlite:///scan.db'
DEBUG = True

ROOT_PATH = path(__file__).dirname()
REPO_PATH = ROOT_PATH.dirname()
ENV_ROOT = REPO_PATH.dirname()

DATA_PATH = os.path.join(REPO_PATH, "data")
TEST_DATA_PATH = os.path.join(DATA_PATH, "test")

MODEL_PATH = os.path.join(DATA_PATH, "models")

SECRET_KEY = "30y^$e7henbp@#_w+z9)o9f8tovjrhoq(%vw=%#*(1-1esrh!_"
USERNAME = "test"
EMAIL = "test@test.com"
PASSWORD = "test"

SQLALCHEMY_DATABASE_URI = DB_URL
SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False

SECURITY_PASSWORD_HASH = "bcrypt"
SECURITY_PASSWORD_SALT = SECRET_KEY

BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
BROKER_URL = 'redis://localhost:6379/3'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/3'
CELERY_IMPORTS = ('core.tasks.tasks',)

CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/4'
CACHE_REDIS_DB = 4

MAX_FEATURES = 500

MODEL_VERSION = 1

try:
    from scan.private import *
except:
    pass