import datetime

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

    def get_url(self):
        if not self.url:
            raise Exception('url not defined in the class')
        return self.url

    def get_model(self):
        if not self.model:
            raise Exception('model not defined in the class')
        return self.model

    def fetch(self):
        url = self.get_url()
        response = requests.get(url)
        return response.json()

    def store(self, data):
        session = db_helper.session

        model = self.get_model()
        instance = model(
            scraped_at=datetime.datetime.now(),
            data=data
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
        data = self.fetch()
        self.store(data)
