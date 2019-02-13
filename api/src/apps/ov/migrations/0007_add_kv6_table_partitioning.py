from django.db import migrations, models
from datetime import datetime, timedelta
from apps.ov.partition_util import PartitionUtil
from apps.ov.models import OvKv6

class Migration(migrations.Migration):

    pu = PartitionUtil()
    tbl = OvKv6._meta.db_table
    initial = False

    dependencies = [ 
        ('ov', '0006_auto_20190131_1646'),
    ]   
    pdate = datetime.today().date()
 
    operations = [ 
        migrations.RunSQL("""
            alter table ov_ovkv6 drop constraint ov_ovkv6_pkey;
            alter table ov_ovkv6 add constraint ov_ovkv6_pkey 
                primary key (id, vehicle);
            alter table ov_ovkv6 rename to __old_kv6;
            create table ov_ovkv6(like __old_kv6 including all) 
                partition by range(vehicle);
            alter sequence if exists ov_ovkv6_id_seq owned by ov_ovkv6.id;
            drop table __old_kv6;
        """),
        migrations.RunSQL(
            pu.make_partition_query(tbl, pu.week_partition(pdate))
        )
    ]   
