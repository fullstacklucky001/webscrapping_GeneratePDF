from sqlalchemy import *
from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
 
engine = create_engine('sqlite:///user.db?check_same_thread=False', echo=True)
Base = declarative_base()
 
class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    rfc = Column(String)
    password = Column(String)
    data = Column(JSON)
    created_date = Column(Date)
    def __init__(self, rfc, password, data, created_date):
        self.rfc = rfc
        self.password = password
        self.data = data
        self.created_date = created_date
 
Base.metadata.create_all(engine)