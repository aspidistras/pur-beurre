from open_food_facts.utils import get_products
import logging

logger = logging.getLogger(__name__)


def update_db():
    get_products()
    logger.info("Database updated")
