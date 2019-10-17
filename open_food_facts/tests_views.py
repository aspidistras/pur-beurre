from django.test import TestCase
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

from open_food_facts.models import Product, Category, Substitute

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

    def test_user_access_to_substitutes(self):
        response = self.client.post(reverse('open_food_facts:user_products'))
        self.assertEqual(response.status_code, 200)


class SubstitutePagesTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Foods", tag="foods")
        self.product = Product.objects.create(name="Nutella", score="c")
        self.product.categories.add(self.category)
        self.substitute = Product.objects.create(name="Pâte à tartiner aux noisettes", score="a")
        self.substitute.categories.add(self.category)
        self.user = User.objects.create_user(username="test", last_name="test", first_name="test",
                                             email="test@hotmail.fr", password="test")
        self.client = Client()
        self.client.login(username='test', password='test')

    def test_product_details_page(self):
        product_id = self.product.id
        response = self.client.get(reverse('open_food_facts:details', args=(product_id,)))
        self.assertEqual(response.status_code, 200)

    def test_save_substitute(self):
        product_id = self.substitute.id
        user_id = self.user.id
        response = self.client.get(reverse('open_food_facts:save_substitute',
                                           args=(product_id, user_id,)))
        self.assertEqual(response.status_code, 200)

    def test_search_substitutes(self):
        product_id = self.product.id
        response = self.client.get(reverse('open_food_facts:search_substitutes',
                                           args=(product_id,)))
        self.assertEqual(response.status_code, 200)

    def test_search_products(self):
        search = "Nutella"
        response = self.client.post(reverse('open_food_facts:search'), {'search': search})
        self.assertEqual(response.status_code, 200)
