from open_food_facts.utils import get_products
import logging


def update_db():
    get_products()
    logging.info("Database updated")
