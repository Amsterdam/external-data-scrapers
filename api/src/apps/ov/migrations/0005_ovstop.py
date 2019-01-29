# Generated by Django 2.1.5 on 2019-01-29 13:10

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ov', '0004_auto_20190128_1022'),
    ]

    operations = [
        migrations.CreateModel(
            name='OvStop',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('geo_location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
        ),
    ]
