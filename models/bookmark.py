from .database import db


class Bookmark(db.Model):
    # db.ForeignKey('user.user_id') table column name
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False, primary_key=True)
    game_id = db.Column(db.Integer, nullable=False, primary_key=True)

    def __init__(self, user_id, game_id):
        self.user_id = user_id
        self.game_id = game_id

    @property
    def serialize(self):
        return {
            'user_id': self.user_id,
            'game_id': self.game_id
        }

    @staticmethod
    def serialize_list(list):
        return [m.serialize for m in list]
