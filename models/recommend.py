from sqlalchemy import Column, Integer, Float, PrimaryKeyConstraint
from .database import db

class Recommend(db.Model):
    __tablename__ = 'recommendation'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer)
    recommended_game_id = Column(Integer)
    composite_score = Column(Float)

    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )
