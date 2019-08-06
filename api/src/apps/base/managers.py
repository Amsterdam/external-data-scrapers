from django.db import models


class BaseRawManager(models.Manager):
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

    def get_query(self):
        '''
        Returns all records or records since last imported timestamp.
        '''
        latest = self.get_import_model().objects.values('scraped_at').last()

        if latest:
            return self.model.objects.filter(scraped_at__gt=latest['scraped_at'])
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
