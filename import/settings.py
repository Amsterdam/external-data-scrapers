import configparser
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config_auth = configparser.ConfigParser()
config_auth.read(os.path.join(BASE_DIR, "config.ini"))

TESTING = {"running": False}

ENVIRONMENT_OVERRIDES = [
    ('host', 'DATABASE_OVERRIDE_HOST'),
    ('port', 'DATABASE_OVERRIDE_PORT'),
    ('database', 'DATABASE_OVERRIDE_NAME'),
    ('username', 'DATABASE_OVERRIDE_USER'),
    ('password', 'DATABASE_OVERRIDE_PASSWORD'),
]

DATABASE_IMPORT_LIMIT = 1000
