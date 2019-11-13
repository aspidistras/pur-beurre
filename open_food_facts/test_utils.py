"""data returned by methods testing module"""

from django.test import TestCase
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

from open_food_facts.models import Product, Category, Substitute
from open_food_facts.utils import access_url, create_products
from open_food_facts.constants import CATEGORIES_LIST_URL, PRODUCTS_LIST_URL

# Create your tests here.


class GetDataTestCase(TestCase):
    """tests data returned by methods"""

    def setUp(self):
        """creates needed objects for following tests
        (category, product, user and client) and logs client in"""

        self.products = access_url(PRODUCTS_LIST_URL.format("a", "1"), parameters=None)

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

    def test_access_url(self):
        """asserts that url is accessible"""

        response = access_url(CATEGORIES_LIST_URL, parameters=None)
        self.assertNotEqual(response, None)

    def test_product_creation(self):
        """asserts that product is created in database"""

        old_products = Product.objects.count()
        create_products(self.products['products'])
        new_products = Product.objects.count()
        self.assertNotEqual(old_products, new_products)

    def test_get_products_search(self):
        """asserts that searches give expected result"""

        # set search parameter
        search = "Nutella"
        # get response
        response = self.client.post(reverse('open_food_facts:search'), {'search': search})
        self.assertEqual(response.context['products'].object_list[1].name, "Nutella")

    def test_get_substitutes(self):
        """asserts that substitutes searching gives expected result"""

        product_id = self.product.id
        # get response
        response = self.client.get(reverse('open_food_facts:search_substitutes',
                                           args=(product_id,)))
        self.assertEqual(response.context['products'].object_list[0].name,
                         "Pâte à tartiner aux noisettes")

    def test_save_substitute(self):
        """checks that a substitutes is actually saved to database when supposed to"""

        # count substitutes number to be able to compare later to new substitutes number
        old_substitutes = Substitute.objects.count()
        product_id = self.substitute.id
        # get response
        self.client.get(reverse('open_food_facts:save_substitute', args=(product_id, )))
        new_substitutes = Substitute.objects.count()
        # if there's one more substitute in the database after calling the save_substitute view,
        # it means the substitute was saved
        self.assertEqual(new_substitutes, old_substitutes + 1)

    def test_unsave_substitute(self):
        """checks that a substitutes is actually removed from database when supposed to"""

        # count substitutes number to be able to compare later to new substitutes number
        old_substitutes = Substitute.objects.count()
        product_id = self.substitute.id
        self.client.get(reverse('open_food_facts:unsave', args=(product_id,)))
        new_substitutes = Substitute.objects.count()
        # if there's one less substitute in the database after calling the unsave view,
        # it means the substitute was deleted
        self.assertEqual(new_substitutes, old_substitutes - 1)
