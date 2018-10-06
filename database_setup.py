import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# Category Table
class Category(Base) :
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

    @property
    def serialize(self) :
        return {
            'id' : self.id,
            'name' : self.name
        }

#Item Table
class Item(Base) :
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(200))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    @property
    def serialize(self) :
        return {
            'cat_id' : self.category_id,
            'description' : self.description,
            'id' : self.id,
            'title' : self.title
        }

engine = create_engine('sqlite:///catagory.db')

Base.metadata.create_all(engine)