from sqlalchemy import Column, Integer,String,TIMESTAMP, text, Text
from database import Base



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, nullable=False)
    email = Column(String,nullable=False,unique = True)
    password = Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))






class Repo(Base):
    __tablename__ = 'repolink'
    id = Column(Integer, primary_key=True)  
    link = Column(String)


class Function(Base):
    __tablename__ = 'functions'

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    function_name = Column(String, index=True)
    class_name = Column(String, index=True, nullable=True)
    code = Column(Text)