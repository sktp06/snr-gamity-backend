from .database import db


class Bookmark(db.Model):
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)
    game = db.Column(db.Integer, nullable=False, primary_key=True)

    def __init__(self, user, game):
        self.user = user
        self.game = game

    @property
    def serialize(self):
        return {
            'user': self.user,
            'game': self.game
        }

    @staticmethod
    def serialize_list(list):
        return [m.serialize for m in list]
