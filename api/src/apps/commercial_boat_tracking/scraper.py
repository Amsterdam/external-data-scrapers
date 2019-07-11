from django.conf import settings

from apps.base_scraper import BaseScraper
from apps.commercial_boat_tracking.models import CommercialBoatTrackingRaw

PARAMS = {'left': 4, 'top': 55, 'right': 8, 'bottom': 50, 'age': 10}


class MissingEnvVariables(Exception):
    """API username or password not found in env variables"""


class InvalidCredentials(Exception):
    """Could not authenticate with provided credentials"""


class ComBoatTrackingScraper(BaseScraper):
    url = 'https://waternet.globalguidesystems.com/api/v0/object'
    auth_url = 'https://waternet.globalguidesystems.com/api/v0/auth/login'
    model = CommercialBoatTrackingRaw

    params = PARAMS

    def get_credentials(self):
        credentials = {'userName': settings.WATERNET_USERNAME, 'password': settings.WATERNET_PASSWORD}
        if not all(credentials.values()):
            raise MissingEnvVariables
        return credentials

    def authenticate(self):
        response = self.requests.post(self.url, self.get_credentials())

        if response.status_code == 403:
            raise InvalidCredentials

        token = response.json().get('token')
        auth_header = {'Authorization': f'Bearer {token}'}
        self.headers.update(auth_header)
