from fastapi import APIRouter, HTTPException, status
from config.db import con
from models.user import users
from schemas.userSchema import User
from cryptography.fernet import Fernet


user = APIRouter()

key = Fernet.generate_key()
func = Fernet(key)


@user.get('/')
def root():
    return {"welcome": "Welcome to my FastAPI"}


@user.get('/users', response_model=list[User], tags=["users"])
def get_users():
    return con.execute(users.select()).fetchall()


@user.post('/users', response_model=User, tags=["users"])
def create_user(user: User):
    newUser = {"name": user.name, "email": user.email}
    newUser["password"] = func.encrypt(user.password.encode("utf-8"))
    result = con.execute(users.insert().values(newUser))
    raise HTTPException(status_code=201, detail="User created successfully")


@user.get('/users/{id}', response_model=User, tags=["users"])
def get_user(id: str):
    return con.execute(users.select().where(users.c.id == id)).first()


@user.put('/users/{id}', response_model=User, tags=["users"])
def update_user(id: str, user: User):
    con.execute(users.update().values(name=user.name, email=user.email,
                password=func.encrypt(user.password.encode("utf-8"))).where(users.c.id == id))
    return con.execute(users.select().where(users.c.id == id)).first()

@user.delete('/users/{id}', status_code=status.HTTP_204_NO_CONTENT, tags=["users"])
def delete_user(id: str):
    con.execute(users.delete().where(users.c.id == id))
    raise HTTPException(status_code=204, detail="User deleted successfully")
