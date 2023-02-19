from typing import Tuple, List
import logging
from fastapi import FastAPI
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

import models
import schemas
from database import engine, session


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

app = FastAPI()


@app.on_event("startup")
async def startup():
    logger.debug('start server')
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    logger.debug('shutdown')
    await session.close()
    await engine.dispose()


@app.get("/recipe/{recipe_id}", response_model=List[schemas.RecipeOut])
async def recipes(recipe_id: int) -> List[schemas.RecipeOut]:
    result = await session.execute(select(models.Recipe).where(models.Recipe.id == recipe_id).options(selectinload(models.Recipe.ingredients)))
    recipes = result.scalars().all()
    return [
        schemas.RecipeOut(
        id=recipe_id,
        dish_name=recipe.dish_name,
        cooking_time=recipe.cooking_time,
        ingredients=[ingredient.name for ingredient in recipe.ingredients],
        description=recipe.description) for recipe in recipes]


@app.get("/titles", response_model=List[schemas.RecipeBrief])
async def get_titles() -> List[schemas.RecipeBrief]:
    result = await session.execute(select(models.Recipe).order_by(models.Recipe.views_number, models.Recipe.cooking_time, reversed=True))
    titles = result.scalars().all()
    return [
        schemas.RecipeBrief(
        dish_name=title.dish_name,
        views_number=title.views_number,
        cooking_time=title.cooking_time) for title in titles]