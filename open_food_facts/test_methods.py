from django.test import TestCase
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

from open_food_facts.models import Product, Category, Substitute

# Create your tests here.


class GetDataTestCase(TestCase):

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

    def test_get_products_search(self):
        search = "Nutella"
        response = self.client.post(reverse('open_food_facts:search'), {'search': search})
        self.assertEqual(response.context['products'].object_list[0].name, "Nutella")

    def test_get_substitutes(self):
        product_id = self.product.id
        response = self.client.get(reverse('open_food_facts:search_substitutes',
                                           args=(product_id,)))
        self.assertEqual(response.context['products'].object_list[0].name,
                         "Pâte à tartiner aux noisettes")

    def test_save_substitute(self):
        old_substitutes = Substitute.objects.count()
        product_id = self.substitute.id
        user_id = self.user.id
        self.client.get(reverse('open_food_facts:save_substitute', args=(product_id, user_id,)))
        new_substitutes = Substitute.objects.count()
        self.assertEqual(new_substitutes, old_substitutes + 1)
