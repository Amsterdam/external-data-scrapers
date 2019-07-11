import requests
from django.conf import settings


class BaseScraper:
    """
    BaseScraper for scraping an api.

    Due to the multiple reuse of the same logic when scraping
    for every datasource, this class has been created.

    Override the methods for custom logic.
    """
    url = None
    auth_url = None
    model = None

    params = None
    headers = {}
    verify_ssl = settings.VERIFY_SSL
    session = None

    @property
    def requests(self):
        if not self.session:
            self.session = requests.Session()
            self.session.verify = self.verify_ssl
        return self.session

    def get_url(self):
        if not self.url:
            raise Exception('url not defined in the class')
        return self.url

    def get_model(self):
        if not self.model:
            raise Exception('model not defined in the class')
        return self.model

    def authenticate(self):
        raise NotImplementedError

    def fetch(self):
        response = self.requests.get(self.url, params=self.params, headers=self.headers)
        return response.json()

    def store(self, data):
        self.model.objects.create(data=data)

    def start(self):
        if self.auth_url:
            self.authenticate()
        data = self.fetch()
        self.store(data)
