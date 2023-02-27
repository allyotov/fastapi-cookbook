from fastapi.testclient import TestClient
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app, get_db
from models import Recipe, Base
from schemas import RecipeBrief


DATABASE_URL = 'sqlite+aiosqlite:///:memory:'

engine = create_async_engine(DATABASE_URL, echo=True)


async_session_for_tests = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def override_get_db():
    async with async_session_for_tests() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


async def populate_db(session = async_session_for_tests()):
    added_recipes = [
        Recipe(dish_name="Chicken Curry", cooking_time=30, description="A spicy Indian dish", views_number=0),
        Recipe(dish_name="Spaghetti Bolognese", cooking_time=60, description="A classic Italian dish", views_number=0),
        Recipe(dish_name="Shepherd's Pie", cooking_time=45, description="A hearty British dish", views_number=0),
        Recipe(dish_name="Beef Stroganoff", cooking_time=45, description="A creamy Russian dish", views_number=0),
    ]

    async with session.begin():
        for recipe in added_recipes:
            session.add(recipe)


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
