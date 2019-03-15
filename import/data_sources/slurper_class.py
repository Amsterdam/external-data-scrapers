import datetime
import os

import requests

import db_helper


class Slurper:
    """
    Slurper class for scraping an endpoint.

    Due to the multiple reuse of the same logic in slurp.py
    for every datasource, this class has been created.

    Override the methods for custom logic.
    """
    url = None
    model = None
    fetch_json = True
    verify = os.getenv('ADP_USE_SSL_CERT', False)

    def get_url(self):
        if not self.url:
            raise Exception('url not defined in the class')
        return self.url

    def get_model(self):
        if not self.model:
            raise Exception('model not defined in the class')
        return self.model

    def get_data(self, response_data):
        try:
            data = dict(**response_data) if self.fetch_json else dict(data=response_data)
        except TypeError:
            raise Exception('Fetched data is not json. Set fetch_json flag to False')
        return dict(scraped_at=datetime.datetime.now(), **data)

    def fetch(self):
        """
        If fetch_json is set to True, this function will return
        response json, otherwise it will return the raw content.
        Sometimes the datasource return files not Json.
        """
        url = self.get_url()
        response = requests.get(url, verify=self.verify)
        if self.fetch_json:
            return response.json()
        return response.content

    def store(self, data):
        session = db_helper.session

        model = self.get_model()
        instance = model(
            **data
        )
        session.add(instance)
        session.commit()
        session.close()

    def setup_db(self, make_engine):
        if make_engine:
            self.engine = db_helper.make_engine(section='docker')
            db_helper.set_session(self.engine)

    def start_import(self, make_engine):
        self.setup_db(make_engine)
        response_data = self.fetch()
        data = self.get_data(response_data)
        self.store(data)
