from django.test import TestCase
from django.urls import reverse
from django.contrib import auth
from django.test import Client

from django.contrib.auth.models import User
from .models import Product, Category, Substitute

# Create your tests here.


class IndexPageTestCase(TestCase):
    def test_index_page(self):
        response = self.client.get(reverse('open_food_facts:index'))
        self.assertEqual(response.status_code, 200)


class LegalNoticesPageTestCase(TestCase):
    def test_legal_notices_page(self):
        response = self.client.get(reverse('open_food_facts:legal_notices'))
        self.assertEqual(response.status_code, 200)


class UserPagesTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="test", last_name="test", first_name="test",
                                             email="test@hotmail.fr", password="test")
        self.client = Client()
        self.client.login(username='test', password='test')

    def test_user_is_logged_in(self):
        response = self.client.post(reverse('open_food_facts:account'))
        self.assertEqual(response.status_code, 200)

    def test_user_is_logged_out(self):
        self.client.logout()
        response = self.client.post(reverse('open_food_facts:login'))
        self.assertEqual(response.status_code, 200)







