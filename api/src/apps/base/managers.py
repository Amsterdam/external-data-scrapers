from django.db import models


class BaseSnapshotManager(models.Manager):
    '''
    RawModels Manager. Used to add query iterator with limit-offset feature.
    This feature allows querying the whole table in batches without loading all the rows
    in memory.
    '''

    def get_import_model(self):
        '''
        Should return the import_model
        '''
        raise NotImplementedError

    def get_latest_timestamp(self):
        latest = self.get_import_model().objects.order_by('scraped_at').last()
        if latest:
            return latest.scraped_at
        return None

    def get_query(self):
        '''
        Returns all records or records since last imported timestamp.
        '''
        latest_timestamp = self.get_latest_timestamp()
        if latest_timestamp:
            return self.model.objects.filter(scraped_at__gt=latest_timestamp)
        return self.model.objects.all()

    def query_iterator(self, limit):
        '''
        Iterates over all records and returns
        them in sets. The size of the sets is defined
        by the limit parameter.
        '''
        queryset = self.get_query()

        index = limit
        offset = 0

        while True:
            query = queryset[offset:index]

            if not query:
                break
            yield query

            offset += limit
            index += limit

    def limit_offset_iterator(self, chunk):
        '''
        Iterates over all records and returns
        them one by one, using limit and offset instead of a db cursor.

        The default .iterator() Uses db cursor which forces the db
        load all the records in memory at the db server. We want to avoid that here
        because it is expected for the raw models to have millions of records

        Attributes:
        ----------
        chunk: int
            The amount of records to retrieve from the db at one time
        '''
        queryset = self.get_query()

        limit = chunk
        index = limit
        offset = 0

        while True:
            query = queryset[offset:index]

            if not query:
                break

            for item in query:
                yield item

            offset += limit
            index += limit


class DistrictManager(models.Manager):
    '''
    This custom manager is created to simplify augmenting datasources
    with the district code. Simply using the `get_district` method
    checks if a geo point lies inside a certain district.
    The district list is retrieved only once from the db and is then cached.
    '''
    district_list = None

    def get_district_list(self):
        '''
        self.district_list is only generated one time
        '''
        if not self.district_list:
            self.district_list = self.values('wkb_geometry', 'code')
        return self.district_list

    def get_district(self, point):
        for district in self.get_district_list():
            if district['wkb_geometry'].contains(point):
                return district['code']


class NeighbourhoodManager(models.Manager):
    '''
    This custom manager is created to simplify augmenting datasources
    with the neighbourhood code. Simply using the `get_neighbourhood` method
    checks if a geo point lies inside a certain neighbourhood.
    The neighbourhood list is retrieved only once from the db and is then cached.
    '''
    neighbourhood_list = None

    def get_neighbourhood_list(self):
        '''
        self.neighbourhood_list is only generated one time
        '''
        if not self.neighbourhood_list:
            self.neighbourhood_list = self.values('wkb_geometry', 'code')
        return self.neighbourhood_list

    def get_neighbourhood(self, point):
        for neighbourhood in self.get_neighbourhood_list():
            if neighbourhood['wkb_geometry'].contains(point):
                return neighbourhood['code']
