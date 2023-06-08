import bcrypt

from models.user import User
from sqlalchemy import event
from .database import db


@event.listens_for(User.__table__, 'after_create')
def create_user(*args, **kwargs):
    db.session.add(User(username='user', password=bcrypt.hashpw('user'.encode('utf-8'),bcrypt.gensalt(10))))
    db.session.commit()