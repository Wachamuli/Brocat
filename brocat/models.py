from sqlalchemy import Column, String, Integer
from werkzeug.security import check_password_hash, generate_password_hash

from brocat.database import Base


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    e_mail = Column(String(30), nullable=False, unique=True)
    username = Column(String(16), nullable=False, unique=True)
    password = Column(String(16), nullable=False)

    def __init__(self, email, usr, psw):
        self.e_mail = email
        self.username = usr
        self.password = Users.hash_pw(psw)

    @staticmethod
    def hash_pw(psw):
        return generate_password_hash(psw.encode('UTF-8'))

    def check_psw(self, psw):
        return check_password_hash(self.password, psw.encode('UTF-8'))

    def __repr__(self):
        return self.username
