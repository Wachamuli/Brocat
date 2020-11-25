from sqlalchemy import Column, String, Integer
from bcrypt import hashpw, gensalt

from brocat.database import Base

class Users(Base):
    __tablename__= 'users'

    id = Column(Integer, primary_key=True)
    e_mail = Column(String(30), nullable=False, unique=True)
    username = Column(String(16), nullable=False, unique=True)
    password = Column(String(16), nullable=False)

    def __init__(self, email, usr, psw):
        self.e_mail = email
        self.username = usr
        self.password = Users.hash_pw(psw)

    @classmethod
    def hash_pw(cls, psw):
        return hashpw(psw.encode('UTF-8'), gensalt(10))
