from sqlalchemy import Table, Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

from database import Base


class Recipe(Base):
    __tablename__ = 'recipe_table'
    id = Column(Integer, primary_key=True, index=True)
    dish_name = Column(String, index=True)
    views_number = Column(Integer)
    cooking_time = Column(Integer)
    description = Column(String)
    ingredients = relationship("Ingredient", )


class Ingredient(Base):
    __tablename__ = "ingredient_table"
    id = Column(Integer, primary_key=True)
    name = Column(String)


association_table = Table(
    "association_table",
    Base.metadata,
    Column("recipe_id", ForeignKey("recipe_table.id"),
    Column("ingredient_id", ForeignKey("ingredient_table.id")))
)