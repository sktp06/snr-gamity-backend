import bcrypt
from models.user import User
from sqlalchemy import event

from .bookmark import Bookmark
from .database import db


@event.listens_for(User.__table__, 'after_create')
def create_user(*args, **kwargs):
    db.session.add(User(username='user', password=bcrypt.hashpw('user'.encode('utf-8'), bcrypt.gensalt(10)), role='user'))
    db.session.add(User(username='admin', password=bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt(10)), role='admin'))
    db.session.commit()


@event.listens_for(Bookmark.__table__, 'after_create')
def create_bookmark(*args, **kwargs):
    db.session.add(Bookmark(user_id=1, game_id=91778))
    db.session.commit()
