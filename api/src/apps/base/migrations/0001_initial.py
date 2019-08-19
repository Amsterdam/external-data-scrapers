# Generated by Django 2.2.2 on 2019-08-14 13:13

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('code', models.CharField(blank=True, max_length=255, null=True)),
                ('naam', models.CharField(blank=True, max_length=255, null=True)),
                ('display', models.CharField(blank=True, max_length=255, null=True)),
                ('type', models.CharField(blank=True, max_length=255, null=True)),
                ('uri', models.CharField(blank=True, max_length=255, null=True)),
                ('wkb_geometry', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='Neighbourhood',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('code', models.CharField(blank=True, max_length=255, null=True)),
                ('vollcode', models.CharField(blank=True, max_length=255, null=True)),
                ('naam', models.CharField(blank=True, max_length=255, null=True)),
                ('display', models.CharField(blank=True, max_length=255, null=True)),
                ('type', models.CharField(blank=True, max_length=255, null=True)),
                ('uri', models.CharField(blank=True, max_length=255, null=True)),
                ('wkb_geometry', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326)),
            ],
        ),
    ]