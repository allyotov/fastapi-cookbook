from fastapi.testclient import TestClient
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app, get_db
from models import Ingredient, Recipe
from schemas import RecipeBrief

DATABASE_URL = 'sqlite+aiosqlite:///:memory:'

engine = create_async_engine(DATABASE_URL, echo=True)


testing_async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = testing_async_session()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db()


async def populate_db(session=override_get_db()):
    added_recipes = [
        Recipe(dish_name="Chicken Curry", cooking_time=30, description="A spicy Indian dish"),
        Recipe(dish_name="Spaghetti Bolognese", cooking_time=60, description="A classic Italian dish"),
        Recipe(dish_name="Shepherd's Pie", cooking_time=45, description="A hearty British dish"),
        Recipe(dish_name="Beef Stroganoff", cooking_time=45, description="A creamy Russian dish"),
    ]

    added_ingredients = [
        Ingredient(name="Pepper"),
        Ingredient(name='Solt'),
    ]

    async with session.begin():
        for recipe in added_recipes:
            session.add(recipe)
        for ingredient in added_ingredients.values():
            session.add(ingredient)


async def start_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await populate_db()


def create_db():
    asyncio.run(start_db())


def test_get_titles():
    create_db()
    client = TestClient(app)
    response = client.get("/titles")
    assert response.status_code == 200
    expected_result = [
        RecipeBrief(dish_name="Spaghetti Bolognese", views_number=0, cooking_time=60),
        RecipeBrief(dish_name="Shepherd's Pie", views_number=0, cooking_time=45),
        RecipeBrief(dish_name="Beef Stroganoff", views_number=0, cooking_time=45),
        RecipeBrief(dish_name="Chicken Curry", views_number=0, cooking_time=30),
    ]
    assert response.json() == expected_result