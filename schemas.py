from typing import List
from pydantic import BaseModel


class RecipeIn(BaseModel):
    dish_name: str
    cooking_time: int
    description: str
    ingredients: List[int]


class RecipeBrief(BaseModel):
    dish_name: str
    views_number: int
    cooking_time: int


class RecipeDetails(BaseModel):
    dish_name: str
    cooking_time: int
    ingredients = List[str]
    description = str


class Ingredient(BaseModel):
    name: str
    recipes: List[int]