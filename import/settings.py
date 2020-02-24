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

DATABASE_IMPORT_LIMIT = int(os.getenv('IMPORT_LIMIT', 1000))

OBJECTSTORE_CONF = dict(
    VERSION='2.0',
    AUTHURL='https://identity.stack.cloudvps.com/v2.0',
    TENANT_NAME=os.getenv('OS_TENANT_NAME'),
    TENANT_ID=os.getenv('OS_TENANT_ID'),
    USER=os.getenv('OS_USERNAME'),
    PASSWORD=os.getenv('OS_PASSWORD'),
    REGION_NAME='NL',
)

# The name of the shapefile changes every now and then.
# As a temporary solution, this constant is used and should be changed by developers -
# whenever the name on the server changes. Later a regex implementation would be nicer.
SHAPEFILE_NAME = ''
