# Generated by Django 2.1.4 on 2019-01-02 14:33

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GuidanceSign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_id', models.CharField(max_length=255, unique=True)),
                ('geometrie', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=20)),
                ('state', models.CharField(max_length=10)),
                ('pub_date', models.DateTimeField()),
                ('removed', models.NullBooleanField()),
                ('stadsdeel', models.CharField(max_length=1)),
                ('buurt_code', models.CharField(max_length=10)),
                ('scraped_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'importer_guidancesign',
                'ordering': ('pub_date',),
                'managed': settings.TESTING,
            },
        ),
        migrations.CreateModel(
            name='ParkingGuidanceDisplay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_id', models.CharField(max_length=255)),
                ('pub_date', models.DateTimeField()),
                ('description', models.TextField()),
                ('type', models.CharField(max_length=50)),
                ('output', models.CharField(max_length=100)),
                ('output_description', models.CharField(max_length=255)),
                ('scraped_at', models.DateTimeField()),
                ('guidance_sign', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='displays', to='parkeergarages.GuidanceSign', to_field='api_id')),
            ],
            options={
                'db_table': 'importer_parkingguidancedisplay',
                'ordering': ('pub_date',),
                'managed': settings.TESTING,
            },
        ),
        migrations.CreateModel(
            name='ParkingLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_id', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=20)),
                ('geometrie', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('state', models.CharField(max_length=10)),
                ('free_space_short', models.IntegerField()),
                ('free_space_long', models.IntegerField()),
                ('short_capacity', models.IntegerField()),
                ('long_capacity', models.IntegerField()),
                ('pub_date', models.DateTimeField()),
                ('stadsdeel', models.CharField(max_length=1)),
                ('buurt_code', models.CharField(max_length=10)),
                ('scraped_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'importer_parkinglocation',
                'ordering': ('pub_date',),
                'managed': settings.TESTING,
            },
        ),
    ]
