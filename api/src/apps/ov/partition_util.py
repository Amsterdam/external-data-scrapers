from datetime import datetime, timedelta

from dateutil import relativedelta


class PartitionUtil(object):
    def __init__(self):
        pass

    def today(self):
        return datetime.today()

    def day_partition(self, d=None):
        d = d if d is not None else self.today()
        return (d, d + timedelta(1))

    def week_number(self, d=None):
        d = d if d is not None else self.today()
        return d.isocalendar()[1]

    def week_partition(self, d=None):
        d = d if d is not None else self.today()
        start = datetime.strptime(
            f"{d.year}-{self.week_number(d)}-1", '%G-%V-%u')
        end = start + timedelta(7)
        return (start, end)

    def month_partition(self, d=None):
        d = d if d is not None else self.today()
        start = d.replace(day=1)
        return (start, start + relativedelta.relativedelta(months=+1))

    def make_partition_query(self, tbl, dt):
        pstart = dt[0].strftime("%Y%m%d")
        pend = dt[1].strftime("%Y%m%d")
        q = f"create table if not exists {tbl}_{pstart} partition"\
            f" of {tbl} for values from ('{pstart}') to ('{pend}');"
        return q
