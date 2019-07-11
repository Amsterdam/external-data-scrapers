import requests
from django.conf import settings


class BaseScraper:
    '''
    BaseScraper for scraping an api.

    Due to the multiple reuse of the same logic when scraping
    for every datasource, this class has been created.

    Override the methods for custom logic.
    '''
    url = None
    auth_url = None
    model = None

    params = None
    headers = {}
    verify_ssl = settings.VERIFY_SSL
    session = None

    @property
    def requests(self):
        '''
        Retrieve Session or create new instance.
        Adds the ssl location if it has been added in the class
        '''
        if not self.session:
            self.session = requests.Session()
            self.session.verify = self.verify_ssl
        return self.session

    def authenticate(self):
        '''
        Some APIs require authentication but it is left to be defined by the user.
        '''
        raise NotImplementedError

    def fetch(self):
        response = self.requests.get(self.url, params=self.params, headers=self.headers)
        return response.json()

    def store(self, data):
        self.model.objects.create(data=data)

    def start(self):
        '''
        Runs the scrape process:
        - Check if auth_url is in the class then runs the authenticate method
        - Fetches the data
        - Stores it in the db
        '''
        if self.auth_url:
            self.authenticate()
        data = self.fetch()
        self.store(data)
