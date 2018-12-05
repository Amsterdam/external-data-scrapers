from django.urls import reverse
from rest_framework.test import APITestCase


class HealthViewTestCase(APITestCase):
    def test_health_ok(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 200)
