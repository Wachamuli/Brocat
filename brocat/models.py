from sqlalchemy import Column, String, Integer
from bcrypt import hashpw, gensalt

from brocat.database import Base

class Users(Base):
    __tablename__= 'users'

    id = Column(Integer, primary_key=True)
    e_mail = Column(String(30), nullable=False, unique=True)
    username = Column(String(16), nullable=False, unique=True)
    password = Column(String(length=16, convert_unicode=True), nullable=False)

    def __init__(self, usr, email, psw):
        self.username = usr
        self.e_mail = email
        self.password = Users.hash_pw(psw)

    @classmethod
    def hash_pw(self, psw):
        return hashpw(psw.encode('UTF-8'), gensalt(10))
