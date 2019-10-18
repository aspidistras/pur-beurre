"""views pages testing module"""

from django.test import TestCase
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

from open_food_facts.models import Product, Category

# Create your tests here.


class IndexPageTestCase(TestCase):
    """tests index page"""

    def test_index_page(self):
        """checks that index page returns status code 200"""

        response = self.client.get(reverse('open_food_facts:index'))
        self.assertEqual(response.status_code, 200)


class LegalNoticesPageTestCase(TestCase):
    """tests legal notices pages"""

    def test_legal_notices_page(self):
        """checks that legal notices page returns status code 200"""

        response = self.client.get(reverse('open_food_facts:legal_notices'))
        self.assertEqual(response.status_code, 200)


class UserPagesTestCase(TestCase):
    """tests user related pages"""

    def setUp(self):
        """creates needed objects for following tests (user and client) and logs client in"""

        self.user = User.objects.create_user(username="test", last_name="test", first_name="test",
                                             email="test@hotmail.fr", password="test")
        self.client = Client()
        self.client.login(username='test', password='test')

    def test_user_is_logged_in(self):
        """checks that account page returns status code 200 which means user is logged in"""

        response = self.client.post(reverse('open_food_facts:account'))
        self.assertEqual(response.status_code, 200)

    def test_user_is_logged_out(self):
        """checks that login page returns status code 200
        which means user is not logged in anymore"""

        self.client.logout()
        response = self.client.post(reverse('open_food_facts:login'))
        self.assertEqual(response.status_code, 200)

    def test_user_access_to_substitutes(self):
        """checks that saved substitutes page returns status code 200"""

        response = self.client.post(reverse('open_food_facts:user_products'))
        self.assertEqual(response.status_code, 200)


class SubstitutePagesTestCase(TestCase):
    """tests substitute related pages"""

    def setUp(self):
        """creates needed objects for following tests
        (category, product, substitute, user and client) and logs client in"""

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
        """checks that product's details page returns status code 200"""

        product_id = self.product.id
        response = self.client.get(reverse('open_food_facts:details', args=(product_id,)))
        self.assertEqual(response.status_code, 200)

    def test_search_products(self):
        """checks that product searching page returns status code 200"""

        search = "Nutella"
        response = self.client.post(reverse('open_food_facts:search'), {'search': search})
        self.assertEqual(response.status_code, 200)

    def test_search_substitutes(self):
        """checks that substitute searching page returns status code 200"""

        product_id = self.product.id
        response = self.client.get(reverse('open_food_facts:search_substitutes',
                                           args=(product_id,)))
        self.assertEqual(response.status_code, 200)

    def test_save_substitute(self):
        """checks that substitute saving page returns status code 200"""

        product_id = self.substitute.id
        user_id = self.user.id
        response = self.client.get(reverse('open_food_facts:save_substitute',
                                           args=(product_id, user_id,)))
        self.assertEqual(response.status_code, 200)
