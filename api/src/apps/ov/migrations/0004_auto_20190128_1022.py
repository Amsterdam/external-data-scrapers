# Generated by Django 2.1.5 on 2019-01-28 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ov', '0003_auto_20190124_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='ovkv6',
            name='journeynumber',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='ovkv6',
            name='numberofcoaches',
            field=models.SmallIntegerField(null=True),
        ),
    ]
