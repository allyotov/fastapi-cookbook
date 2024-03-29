import logging
import asyncio
from pathlib import Path
import csv

from database import session, engine
import models


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


PARENT_PATH = Path(__file__).parent

DATA_SOURCE_PATH = PARENT_PATH / 'source_data'

INGREDIENTS_CSV = DATA_SOURCE_PATH / 'ingredients.csv'
RECIPES_CSV = DATA_SOURCE_PATH / 'recipes.csv'


async def populate_db():
    try:
        with open(INGREDIENTS_CSV, encoding="utf8") as ingredients_file:
            reader = csv.reader(ingredients_file, delimiter=';')
            added_ingredients = {}
            for num, row in enumerate(reader, start=1):
                logger.debug(row[0])
                new_ingredient = models.Ingredient(name=row[0])
                added_ingredients[num] = new_ingredient

        added_recipes = []
        with open(RECIPES_CSV, encoding="utf8") as recipes_file:
            reader = csv.reader(recipes_file, delimiter=';')
            for name, time, description, ingredients_ids_str in reader:
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

        logger.debug(added_ingredients)

        async with session.begin():
            for recipe in added_recipes:
                session.add(recipe)
            for ingredient in added_ingredients.values():
                logger.debug(ingredient)
                logger.debug(ingredient.name)
                logger.debug(type(ingredient))
                session.add(ingredient)
                logger.debug('Added to db!')

    except Exception as exc:
        logger.exception(exc)

async def start_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    await populate_db()


if __name__ == '__main__':

    logger.debug('Cook-book initial db population.')
    asyncio.run(start_db())
    logger.debug('Populate complete.')