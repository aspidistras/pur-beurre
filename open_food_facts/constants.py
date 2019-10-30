"""constants defining module"""

CATEGORIES_LIST_URL = "https://fr.openfoodfacts.org/categories.json"
PRODUCTS_INFO_URL = "https://fr.openfoodfacts.org/nutrition-grade/{}.json"
PRODUCTS_LIST_URL = "https://fr.openfoodfacts.org/nutrition-grade/{}/{}.json"
SEARCH_URL = "https://fr.openfoodfacts.org//cgi/search.pl?"

SCORES_LIST = ['a', 'b', 'c', 'd', 'e']

SCORE_IMAGES_LIST = {"a": "/static/img/nutriscore_a.png", "b": "/static/img/nutriscore_b.png",
                     "c": "/static/img/nutriscore_c.png", "d": "/static/img/nutriscore_d.png",
                     "e": "/static/img/nutriscore_e.png"}

# change to alter number of pages cruised to retrieve products from API
MAX_PAGES_NUMBER = 30
