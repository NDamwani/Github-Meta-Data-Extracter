from fastapi import FastAPI, Depends,status
import psycopg2
from psycopg2.extras import RealDictCursor
# from . import models
import routes
import models
from database import engine, SessionLocal, get_db
from sqlalchemy.orm import Session
from routes import user, auth, github



app = FastAPI()


models.Base.metadata.create_all(bind=engine)




try:
    conn = psycopg2.connect(host='localhost',database='postgres', user='postgres',password='nikhil',cursor_factory=RealDictCursor)
    curson = conn.cursor()
    print("Database connection was successfull")

except Exception as error:
    print("Failed.!!!")
    print("Error: ",error)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(github.router)


