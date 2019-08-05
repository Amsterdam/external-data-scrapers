from django.conf import settings

from apps.base.base_api_scraper import BaseAPIScraper
from apps.boat_tracking.models import BoatTrackingRaw

PARAMS = {'left': 4, 'top': 55, 'right': 8, 'bottom': 50, 'age': 10}


class MissingEnvVariables(Exception):
    """API username or password not found in env variables"""


class InvalidCredentials(Exception):
    """Could not authenticate with provided credentials"""


class BoatTrackingScraper(BaseAPIScraper):
    url = 'https://waternet.globalguidesystems.com/api/v0/object'
    model = BoatTrackingRaw

    def __init__(self):
        super().__init__()
        self.auth_url = 'https://waternet.globalguidesystems.com/api/v0/auth/login'
        self.params = PARAMS

    def get_credentials(self):
        """Retrieve api Credentials"""
        credentials = {
            'userName': settings.WATERNET_USERNAME,
            'password': settings.WATERNET_PASSWORD
        }
        if not all(credentials.values()):
            raise MissingEnvVariables
        return credentials

    def authenticate(self):
        """Send authentication request and add token to headers"""
        response = self.requests.post(self.auth_url, self.get_credentials())

        if response.status_code != 200:
            raise InvalidCredentials

        token = response.json().get('token')
        auth_header = {'Authorization': f'Bearer {token}'}
        self.headers.update(auth_header)
