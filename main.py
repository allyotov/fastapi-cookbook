from typing import Tuple
from fastapi import FastAPI
from sqlalchemy.future import select

import models
import schemas
from database import engine, session

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await session.close()
    await engine.dispose()


@app.post("/recipes", response_model=schemas.RecipeIn)
async def recipes(recipe: schemas.RecipeIn) -> Tuple[models.Recipe, models.Ingredient]:
    ...