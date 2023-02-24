from typing import Tuple, List, Optional
import logging
from logging.config import dictConfig
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from config import LogConfig

import models
import schemas
from database import engine, async_session

dictConfig(LogConfig().dict())
logger = logging.getLogger('cookbook_api')


app = FastAPI()


def get_db():
    db = async_session()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    logger.debug('start server')
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown(session = Depends(get_db)):
    logger.debug('shutdown')
    await session.close()
    await engine.dispose()


@app.get("/recipe/{recipe_id}", response_model=schemas.RecipeOut)
async def recipes(recipe_id: int, session = Depends(get_db)) -> Optional[schemas.RecipeOut]:
    """
    Retrieve a recipe by ID.

    Arguments:
    - `recipe_id`: The ID of the recipe to retrieve.

    Returns:
    - A dictionary containing the retrieved recipe or a 404 response if the item is not found.
    """
    async with session.begin():
        result = await session.execute(select(models.Recipe).where(models.Recipe.id == recipe_id).options(selectinload(models.Recipe.ingredients)))
        recipe = result.scalar_one_or_none()
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        recipe.views_number += 1
        await session.commit()
        return schemas.RecipeOut(
            id=recipe_id,
            dish_name=recipe.dish_name,
            cooking_time=recipe.cooking_time,
            ingredients=[ingredient.name for ingredient in recipe.ingredients],
            description=recipe.description,
        )


@app.get("/titles", response_model=List[schemas.RecipeBrief])
async def get_titles(session = Depends(get_db)) -> List[schemas.RecipeBrief]:
    """
    Retrieve a list of recipe titles with their views number and cooking time.

    Returns:
    - A list of dictionaries of recipe titles.
    """
    result = await session.execute(select(models.Recipe).order_by(models.Recipe.views_number.desc(), models.Recipe.cooking_time.desc()))
    titles = result.scalars().all()
    logger.debug(titles)
    return [
        schemas.RecipeBrief(
        dish_name=title.dish_name,
        views_number=title.views_number,
        cooking_time=title.cooking_time) for title in titles]