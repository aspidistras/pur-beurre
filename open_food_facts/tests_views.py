"""views pages testing module"""

from django.test import TestCase
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

from open_food_facts.models import Product, Category, Substitute

# Create your tests here.


class IndexPageTestCase(TestCase):
    """tests index page"""

    def test_index_page(self):
        """checks that index page returns status code 200"""

        # get response
        response = self.client.get(reverse('open_food_facts:index'))
        self.assertEqual(response.status_code, 200)


class LegalNoticesPageTestCase(TestCase):
    """tests legal notices pages"""

    def test_legal_notices_page(self):
        """checks that legal notices page returns status code 200"""

        # get response
        response = self.client.get(reverse('open_food_facts:legal_notices'))
        self.assertEqual(response.status_code, 200)


class ThanksPageTestCase(TestCase):
    """tests thanks for creating an account page"""

    def test_thanks_page(self):
        response = self.client.get(reverse('open_food_facts:thanks'))
        self.assertEqual(response.status_code, 200)


class UserPagesTestCase(TestCase):
    """tests user related pages"""

    def setUp(self):
        """creates needed objects for following tests (user and client) and logs client in"""

        self.user = User.objects.create_user(username="test", last_name="test", first_name="test",
                                             email="test@hotmail.fr", password="test")
        self.client = Client()
        self.client.login(username='test', password='test')

    def test_user_is_signed_in(self):
        """checks that thanks page returns status code 200 which means user created his account"""
        response = self.client.post(reverse('open_food_facts:get_new_user'),
                                    {'username': 'username', 'first_name': 'first_name',
                                     'last_name': 'last_name', 'email': 'email',
                                     'password': 'password'})
        self.assertEqual(response.status_code, 200)

    def test_user_is_logged_in(self):
        """checks that account page returns status code 200 which means user is logged in"""

        # get response
        response = self.client.post(reverse('open_food_facts:account'))
        self.assertEqual(response.status_code, 200)

    def test_user_is_logged_out(self):
        """checks that login page returns status code 200
        which means user is not logged in anymore"""

        self.client.logout()
        # get response
        response = self.client.post(reverse('open_food_facts:login'))
        self.assertEqual(response.status_code, 200)

    def test_user_access_to_substitutes(self):
        """checks that saved substitutes page returns status code 200"""

        # get response
        response = self.client.post(reverse('open_food_facts:user_products'))
        self.assertEqual(response.status_code, 200)


class SubstitutePagesTestCase(TestCase):
    """tests substitute related pages"""

    def setUp(self):
        """creates needed objects for following tests
        (category, product, substitute, user and client) and logs client in"""

        self.category = Category.objects.create(tag="foods")
        self.product = Product.objects.create(name="Nutella", score="c", url="p")
        self.product.categories.add(self.category)
        self.substitute = Product.objects.create(name="Pâte à tartiner aux noisettes", score="a",
                                                 url="s")
        self.substitute.categories.add(self.category)
        self.user = User.objects.create_user(username="test", last_name="test", first_name="test",
                                             email="test@hotmail.fr", password="test")
        self.client = Client()
        self.client.login(username='test', password='test')
        self.saved_substitute = Substitute.objects.create(user=self.user, product=self.substitute)

    def test_product_details_page(self):
        """checks that product's details page returns status code 200"""

        product_id = self.product.id
        # get response
        response = self.client.get(reverse('open_food_facts:details', args=(product_id,)))
        self.assertEqual(response.status_code, 200)

    def test_search_products(self):
        """checks that product searching page returns status code 200"""

        search = "Nutella"
        # get response
        response = self.client.post(reverse('open_food_facts:search'), {'search': search})
        self.assertEqual(response.status_code, 200)

    def test_search_substitutes(self):
        """checks that substitute searching page returns status code 200"""

        product_id = self.product.id
        # get response
        response = self.client.get(reverse('open_food_facts:search_substitutes',
                                           args=(product_id,)))
        self.assertEqual(response.status_code, 200)

    def test_save_substitute(self):
        """checks that substitute saving page returns status code 200"""

        product_id = self.substitute.id
        # get response
        response = self.client.get(reverse('open_food_facts:save_substitute',
                                           args=(product_id, )))
        self.assertEqual(response.status_code, 200)

    def test_unsave_substitute(self):
        """checks that substitute unsaving page returns status code 200"""

        product_id = self.saved_substitute.product.id
        # get response
        response = self.client.get(reverse('open_food_facts:unsave',
                                           args=(product_id,)))
        self.assertEqual(response.status_code, 200)
