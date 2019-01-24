class bulk_inserter(object):
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
        if len(self.batch) > 0:
            self.table.objects.bulk_create(self.batch, len(self.batch))
            self.batch.clear()
