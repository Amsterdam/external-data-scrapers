from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import FieldDoesNotExist
from django.test import TestCase

from apps.base_api_scraper import BaseAPIScraper


class TestBaseAPIScraper(TestCase):
    def test_missing_model_attribute(self):
        class TestAPIScraper(BaseAPIScraper):
            url = 'test'

        with self.assertRaises(AssertionError):
            TestAPIScraper()

    def test_missing_url_attribute(self):
        class TestModel(models.Model):
            data = JSONField

            class Meta:
                app_label = 'apps.health'

        class TestAPIScraper(BaseAPIScraper):
            model = TestModel
        with self.assertRaises(AssertionError):
            TestAPIScraper()

    def test_missing_data_field_in_model(self):
        class TestModelNoData(models.Model):
            test = models.IntegerField()

            class Meta:
                app_label = 'apps.health'

        class TestAPIScraper(BaseAPIScraper):
            url = 'test'
            model = TestModelNoData

        with self.assertRaises(FieldDoesNotExist):
            TestAPIScraper()

    def test_data_not_json_field_in_model(self):
        class TestModelInteger(models.Model):
            data = models.IntegerField()

            class Meta:
                app_label = 'apps.health'

        class TestAPIScraper(BaseAPIScraper):
            url = 'test'
            model = TestModelInteger

        with self.assertRaises(AssertionError):
            TestAPIScraper()

    def test_ok(self):
        class TestModelOk(models.Model):
            data = JSONField()

            class Meta:
                app_label = 'apps.health'

        class TestAPIScraper(BaseAPIScraper):
            url = 'test'
            model = TestModelOk

        TestAPIScraper()
