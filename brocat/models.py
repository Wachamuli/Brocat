from flask_login import UserMixin, current_user
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from bcrypt import hashpw, checkpw, gensalt
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from brocat.database import Base


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(30), nullable=False, unique=True)
    username = Column(String(16), nullable=False, unique=True)
    password = Column(String(16), nullable=False)

    brocats = relationship('Brocat', back_populates='author')

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = User.hash_psw(password)

    @staticmethod
    def hash_psw(psw):
        hashed_psw = hashpw(psw.encode('UTF-8'), gensalt())
        return hashed_psw

    def check_psw(self, psw):
        return checkpw(psw.encode('UTF-8'), self.password)

    def __repr__(self):
        return self.username


class Brocat(Base):
    __tablename__ = 'brocats'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    thumbnail = Column(String(200), nullable=False)
    audio = Column(String(200), nullable=False)
    description = Column(String(500))

    users_id = Column(Integer, ForeignKey('users.id'))
    author = relationship('User', back_populates='brocats')

    def __init__(self, title, thumbnail, audio, description, users_id=None, author=current_user):
        self.title = title
        self.thumbnail = thumbnail
        self.audio = audio
        self.description = description
        self.author = author      # Not recomendable to touch
        self.users_id = users_id  # these. Only throught API.


# * SCHEMAS

class UsersSchema(SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True

    id = auto_field()
    email = auto_field()
    username = auto_field()
    password = auto_field()

    brocats = auto_field()


user_schema = UsersSchema()
users_schema = UsersSchema(many=True)


class BrocatsSchema(SQLAlchemySchema):
    class Meta:
        model = Brocat
        load_instance = True

    id = auto_field()
    title = auto_field()
    thumbnail = auto_field()
    audio = auto_field()
    description = auto_field()

    users_id = auto_field()
    author = auto_field()


brocat_schema = BrocatsSchema()
brocats_schema = BrocatsSchema(many=True)
