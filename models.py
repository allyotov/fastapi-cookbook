from sqlalchemy import Table, Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

from database import Base


association_table = Table(
    "recipe_ingredients",
    Base.metadata,
    Column("recipe_id", ForeignKey("recipes.id"), primary_key=True),
    Column("ingredient_id", ForeignKey("ingredients.id"), primary_key=True)
)


class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True, index=True)
    dish_name = Column(String, index=True)
    views_number = Column(Integer)
    cooking_time = Column(Integer)
    description = Column(String)
    ingredients = relationship("Ingredient", secondary='recipe_ingredients', back_populates='recipes')


class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    recipes = relationship("Recipe", secondary="recipe_ingredients", back_populates='ingredients')
