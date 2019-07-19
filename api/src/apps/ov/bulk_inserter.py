import logging

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)


class BulkInserter:
    def __init__(self, table, batch_size=1000):
        self.batch_size = batch_size
        self.table = table
        self.batch = []

    def __del__(self):
        self.flush()

    def add(self, obj):
        self.batch.append(obj)
        if len(self.batch) >= self.batch_size:
            self.flush()

    def flush(self):
        if not self.batch:
            return

        try:
            self.table.objects.bulk_create(self.batch, len(self.batch))
        except Exception as e:
            log.error("Exception occured when bulk creating batch. Batch will be cleared")
            raise e
        finally:
            # Make sure batch is cleared even when an error
            # occurs to avoid the batch getting endlessly bigger.
            self.batch.clear()
