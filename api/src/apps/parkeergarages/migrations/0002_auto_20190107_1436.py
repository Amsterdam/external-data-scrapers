# Generated by Django 2.1.4 on 2019-01-07 13:36

from django.db import migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('parkeergarages', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='guidancesign',
            options={'managed': settings.TESTING, 'ordering': ('-pub_date',)},
        ),
        migrations.AlterModelOptions(
            name='parkingguidancedisplay',
            options={'managed': settings.TESTING, 'ordering': ('-pub_date',)},
        ),
        migrations.AlterModelOptions(
            name='parkinglocation',
            options={'managed': settings.TESTING, 'ordering': ('-pub_date',)},
        ),
    ]
