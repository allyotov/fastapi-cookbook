import logging
import asyncio
from sqlalchemy.future import select
from database import session, engine
from models import Recipe, Ingredient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def check_db():
    async with session.begin():
        result = await session.execute(select(Recipe).order_by(Recipe.id).limit(20))
        for recipe in result.scalars():
            logger.info(recipe.dish_name)
            logger.info(recipe.ingredients)

        result = await session.execute(select(Ingredient).order_by(Ingredient.id).limit(20))
        for ingredient in result.scalars():
            logger.info(ingredient.name)

if __name__ == '__main__':

    logger.debug('Cook-book initial db population.')
    asyncio.run(check_db())
    logger.debug('Populate complete.')