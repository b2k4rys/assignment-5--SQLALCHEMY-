from fastapi import FastAPI, HTTPException, Depends, status, Form, Cookie, Response
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from attrs import asdict
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session 
from typing import Literal
from sqlalchemy.orm import sessionmaker
import jwt
import json
from sqlalchemy import inspect

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
db_dependecy = Annotated[Session, Depends(get_db)]

class UserBase(BaseModel):
  username: str
  email: str
  password: str

class FlowerBase(BaseModel):
  name: str
  count: int
  price: int

@app.post('/signup')
async def signup(user: UserBase, db: db_dependecy):
  db_user = models.Users(username= user.username, email = user.email, password = user.password)
  db.add(db_user)
  db.commit()

@app.post('/flowers')
async def post_flower(flower: FlowerBase, db: db_dependecy):
  db_flower = models.Flower(name=flower.name, count = flower.count, price = flower.price)
  db.add(db_flower)
  db.commit()
  return db_flower.id

@app.get('/flowers')
async def post_flower():
  result = []
  flowers = session.query(models.Flower).all()

  for flower in flowers:
    result.append(flower)
  return result

@app.put('/flowers/{flower_id}')
async def update_flower(flower_id: int, name: str, count: int, price: int):
  db = SessionLocal()
  db_item = db.query(models.Flower).filter(models.Flower.id == flower_id).first()
  db_item.name = name
  db_item.count = count
  db_item.price = price
  db.commit()
  return db_item
  
@app.delete('/flowers/{flower_id}')
async def delete_flower(flower_id: int):
  db = SessionLocal()
  db_item = db.query(models.Flower).filter(models.Flower.id == flower_id).first()
  db.delete(db_item)
  db.commit()
  return {"message": "Item deleted successfully"}



@app.post('/cart/items')
async def add_flower(response: Response, flower_id: int = Form(), items: str = Cookie(default='[]'), price: int = Cookie(default=0)):
  db = SessionLocal()
  items_json = json.loads(items)
  flower = db.query(models.Flower).filter(models.Flower.id == flower_id).first()

  def object_as_dict(obj):
    return {
        c.key: getattr(obj, c.key)
        for c in inspect(obj).mapper.column_attrs
    }
  d = object_as_dict(flower)

  
  if flower:
      items_json.append(d)
      price += d['price']
      new_items = json.dumps(items_json)
      response.set_cookie(key='items', value=new_items)
      response.set_cookie(key='price', value=price)
      return {'items': items_json,'price': price}

  else:
    raise HTTPException(status_code=404, detail="Item not found")


@app.delete('/cart/delete_items')
async def delete_items(response: Response):
  response.delete_cookie(key='items')
  return response.status_code



def create_access_token(id: int):
  to_encode = {'user_id': id}
  encoded_jwt = jwt.encode(to_encode, 'super-secret', 'HS256')
  return encoded_jwt



@app.post('/login')
async def login(username:str = Form(), password: str = Form()):
  db = SessionLocal()
  db_item = db.query(models.Users).filter(models.Users.username == username).first()
  if password == db_item.password:
    token = create_access_token(db_item.id)
    return {'access_token': token}
  
@app.get('/profile')
async def get_info(username: str, token: str = Depends(oauth2_scheme)):
  db = SessionLocal()

  temp =  db.query(models.Users).filter(models.Users.username == username).first()

  return {
    'username': temp.username,
    'email': temp.email,
    'id': temp.id
  }

