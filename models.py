from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base

class Users(Base):
  __tablename__ = "users"


  id = Column(Integer, primary_key=True, autoincrement=True)
  username = Column(String, unique=True)
  email = Column(String, unique=True)
  password = Column(String)

class Flower(Base):
  __tablename__ = 'flower'

  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String)
  count = Column(Integer)
  price = Column(Integer)