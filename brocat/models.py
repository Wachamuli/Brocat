from sqlalchemy import Column, String, Integer
from flask_login import UserMixin
from bcrypt  import hashpw, checkpw, gensalt

from brocat.database import Base


class Users(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    e_mail = Column(String(30), nullable=False, unique=True)
    username = Column(String(16), nullable=False, unique=True)
    password = Column(String(16), nullable=False)

    def __init__(self, email, usr, psw):
        self.e_mail = email
        self.username = usr
        self.password = Users.hash_psw(psw)

    @staticmethod
    def hash_psw(psw):
        return hashpw(psw.encode(), gensalt())

    def check_psw(self, psw):
        return checkpw(psw.encode('UTF-8'), self.password)

    def __repr__(self):
        return self.username
