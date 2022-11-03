import logging
from pathlib import Path
import csv

from database import session
import models


logger = logging.get_logger(__name__)
logging.basicConfig(level=logging.DEBUG)


PARENT_PATH = Path(__file__).parent

DATA_SOURCE_PATH = PARENT_PATH / 'source_data'

INGREDIENTS_CSV = DATA_SOURCE_PATH / 'ingredients.csv'
RECIPES_CSV = DATA_SOURCE_PATH / 'recipes.csv'


def populate_db():
    try:
        with open(INGREDIENTS_CSV) as ingredients_file:
            reader = csv.reader(ingredients_file, delimiter=';')
            added_ingredients = {}
            for num, row in enumerate(reader, start=1):
                added_ingredients[num] = new_ingredient
                new_ingredient = models.Ingredient(name=row)
    except Exception as exc:
        logger.exception(exc)
    
    try:
        added_recipes = []
        with open(RECIPES_CSV) as recipes_file:
            reader = csv.reader(recipes_file, delimiter=';')
            for row in enumerate(reader, start=1):
                name, time, description, ingredients_ids_str = row.split(';')
                logger.debug('ingredient: %s %s %s %s' % (name, time, description, ingredients_ids_str))
                ingredients_ids = map(int, ingredients_ids_str.split(','))
                new_recipe = models.Recipe(
                    dish_name=name,
                    views_number=0,
                    cooking_time=time,
                    description=description,
                    ingredients=[added_ingredients[id] for id in ingredients_ids]
                )
                added_recipes.append(new_recipe)
    except Exception as exc:
        logger.exception(exc)

    try:
        with session.begin():
            for ingredient in added_ingredients:
                session.add(ingredient)
            for recipe in added_recipes:
                session.add(recipe)
    except Exception as exc:
        logger.exception(exc)


if __name__ == '__main__':
    logger.debug('Cook-book initial db population.')
    populate_db()
    logger.debug('Populate complete.')