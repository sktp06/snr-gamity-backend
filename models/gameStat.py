from .database import db

class GameStat(db.Model):
    __tablename__ = 'gameStat'

    id = db.Column(db.Integer, primary_key=True)
    update_date = db.Column(db.String(2000))
    total_games = db.Column(db.Integer)
    total_genres = db.Column(db.Integer)
    genre_count = db.Column(db.Text)
    total_upcoming_games = db.Column(db.Integer)

    def __init__(self, update_date, total_games, total_genres, genre_count, total_upcoming_games):
        self.update_date = update_date
        self.total_games = total_games
        self.total_genres = total_genres
        self.genre_count = genre_count
        self.total_upcoming_games = total_upcoming_games

    @property
    def serialize(self):
        return {
            'update_date': self.update_date,
            'total_games': self.total_games,
            'total_genres': self.total_genres,
            'genre_count': self.genre_count,
            'total_upcoming_games': self.total_upcoming_games
        }
