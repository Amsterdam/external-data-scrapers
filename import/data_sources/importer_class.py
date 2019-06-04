import logging

from shapely import wkb

import db_helper
import settings

log = logging.getLogger(__name__)


class Importer:
    """
    Importer class for importing a scraped endpoint.

    Due to the multiple reuse of the same logic in copy_to_model.py
    for every data source, this class has been created.

    Override the methods for custom logic.
    """
    clean_model = None
    raw_model = None
    stadsdeel_list = None
    buurt_code_list = None
    stadsdeel_query = None
    buurt_code_query = None

    def __init__(self):
        self.session = db_helper.session

    def store(self, raw_data):
        raise NotImplementedError

    def linestring_to_str(self, srid, coordinates):
        string = ''
        for pair in coordinates:
            string += '{} {},'.format(pair[0], pair[1])
        string = string.strip(',')
        return f'SRID={srid};LINESTRING({string})'

    def point_to_str(self, srid, coordinates):
        return f'SRID={srid};POINT({coordinates[0]} {coordinates[1]})'

    def get_stadsdeel_list(self):
        if not self.stadsdeel_list:
            query = self.session.execute(self.stadsdeel_query).fetchall()
            self.stadsdeel_list = [(x[0], wkb.loads(x[1], hex=True)) for x in query]
        return self.stadsdeel_list

    def get_buurt_code_list(self):
        if not self.buurt_code_list:
            query = self.session.execute(self.buurt_code_query).fetchall()
            self.buurt_code_list = [(x[0], wkb.loads(x[1], hex=True)) for x in query]
        return self.buurt_code_list

    def get_stadsdeel(self, geo_object):
        for instance in self.get_stadsdeel_list():
            if instance[1].contains(geo_object):
                return instance[0]

    def get_buurt_code(self, geo_object):
        for instance in self.get_buurt_code_list():
            if instance[1].contains(geo_object):
                return instance[0]

    def get_latest_query(self):
        """
        Returns raw model database query according to the last
        entry in the clean model. Only returns the query without
        fetching the data to allow further statements to be added
        like 'offset' and 'limit'
        """
        model = self.clean_model if isinstance(self.clean_model, str) else self.clean_model.__table__.name

        latest = self.session.execute(
            f'SELECT scraped_at FROM {model} ORDER BY scraped_at DESC LIMIT 1;'
        ).first()

        if latest:
            # update since api
            return (
                self.session.query(self.raw_model)
                    .order_by(self.raw_model.scraped_at.asc())
                    .filter(self.raw_model.scraped_at > latest.scraped_at)
            )
        # empty api.
        return self.session.query(self.raw_model)

    def start_import(self):
        """
        Importing the data is done in batches to avoid
        straining the resources.
        """
        self.session = db_helper.session
        query = self.get_latest_query()
        run = True

        offset = 0
        limit = settings.DATABASE_IMPORT_LIMIT

        while run:
            raw_data = query.offset(offset).limit(limit).all()
            if raw_data:
                log.info(
                    "Fetched {} raw {} entries".format(len(raw_data), self.raw_model)
                )
                self.store(raw_data)
                offset += limit
            else:
                run = False
