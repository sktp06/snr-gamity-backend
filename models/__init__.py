import bcrypt
from models.user import User
from sqlalchemy import event

from .bookmark import Bookmark
from .database import db


@event.listens_for(User.__table__, 'after_create')
def create_user(*args, **kwargs):
    db.session.add(User(username='admin', password=bcrypt.hashpw('testadmin'.encode('utf-8'), bcrypt.gensalt(10)), role='admin'))
    db.session.add(User(username='user', password=bcrypt.hashpw('testuser'.encode('utf-8'), bcrypt.gensalt(10)), role='user'))
    db.session.add(User(username='kantaporn', password=bcrypt.hashpw('testkantaporn'.encode('utf-8'), bcrypt.gensalt(10)), role='user'))
    db.session.add(User(username='nitipoom', password=bcrypt.hashpw('testnitipoom'.encode('utf-8'), bcrypt.gensalt(10)), role='user'))
    db.session.add(User(username='gamer', password=bcrypt.hashpw('testgamer'.encode('utf-8'), bcrypt.gensalt(10)), role='user'))
    db.session.commit()


@event.listens_for(Bookmark.__table__, 'after_create')
def create_bookmark(*args, **kwargs):
    db.session.add(Bookmark(user_id=2, game_id=21874))
    db.session.add(Bookmark(user_id=2, game_id=22713))
    db.session.add(Bookmark(user_id=2, game_id=115286))
    db.session.add(Bookmark(user_id=2, game_id=194662))
    db.session.add(Bookmark(user_id=3, game_id=115286))
    db.session.add(Bookmark(user_id=3, game_id=194662))
    db.session.add(Bookmark(user_id=4, game_id=132769))
    db.session.add(Bookmark(user_id=4, game_id=143239))
    db.session.commit()
