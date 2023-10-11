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

    def __init__(self, game_id, recommended_game_id, composite_score):
        self.game_id = game_id
        self.recommended_game_id = recommended_game_id
        self.composite_score = composite_score

    @property
    def serialize(self):
        return {
            'id': self.id,
            'game_id': self.game_id,
            'recommended_game_id': self.recommended_game_id,
            'composite_score': self.composite_score,
        }
