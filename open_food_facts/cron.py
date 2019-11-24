from open_food_facts.utils import get_products
from sentry_sdk import capture_message


def update_db():
    get_products()
    capture_message("Database automatically updated")
