from typing import Tuple, List, Optional
import logging
from logging.config import dictConfig
from fastapi import FastAPI
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import update
from config import LogConfig

import models
import schemas
from database import engine, session

dictConfig(LogConfig().dict())
logger = logging.getLogger('cookbook_api')


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


@app.get("/recipe/{recipe_id}", response_model=schemas.RecipeOut)
async def recipes(recipe_id: int) -> Optional[schemas.RecipeOut]:
    #await session.execute(update(models.Recipe).where(models.Recipe.id == recipe_id).values({'views_number':1}))
    result = await session.execute(select(models.Recipe).where(models.Recipe.id == recipe_id).options(selectinload(models.Recipe.ingredients)))
    logger.debug(result)
    if result.scalars():
        await session.execute(models.Recipe.update(models.Recipe.id == recipe_id).values(views_number=models.Recipe.views_number + 1))
        recipe = result.scalars().first()
        return schemas.RecipeOut(
            id=recipe_id,
            dish_name=recipe.dish_name,
            cooking_time=recipe.cooking_time,
            ingredients=[ingredient.name for ingredient in recipe.ingredients],
            description=recipe.description)
    return {}


@app.get("/titles", response_model=List[schemas.RecipeBrief])
async def get_titles() -> List[schemas.RecipeBrief]:
    result = await session.execute(select(models.Recipe).order_by(models.Recipe.views_number, models.Recipe.cooking_time, reversed=True))
    titles = result.scalars().all()
    logger.debug(titles)
    return [
        schemas.RecipeBrief(
        dish_name=title.dish_name,
        views_number=title.views_number,
        cooking_time=title.cooking_time) for title in titles]