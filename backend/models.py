from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base

class RecipeDB(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    ingredients = Column(ARRAY(String))
    instructions = Column(Text)
    cooking_time = Column(Integer)
    difficulty = Column(String(20))