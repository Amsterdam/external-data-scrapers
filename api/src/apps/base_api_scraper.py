import requests
from django.conf import settings
from django.contrib.postgres.fields import JSONField


class InvalidDataField(Exception):
    '''RawModel missing jsonb 'data' field.'''


class BaseAPIScraper:
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
        Use this method to send an authentication request and update
        the session headers with the token. This method will be automatically
        called if the 'auth_url' variable is defined in the class.
        '''
        raise NotImplementedError

    def parse(self, response):
        '''Parses the response. Default is json, override to change it'''
        return response.json()

    def fetch(self):
        response = self.requests.get(self.url, params=self.params, headers=self.headers)
        return self.parse(response)

    def store(self, data):
        if not isinstance(self.model._meta.get_field('data'), JSONField):
            raise InvalidDataField
        self.model.objects.create(data=data)

    def start(self):
        '''
        Runs the scrape process:
        - Check if auth_url is in the class then calls the authenticate method
        - Fetches the data
        - Stores it in the db
        '''
        if self.auth_url:
            self.authenticate()
        data = self.fetch()
        self.store(data)
