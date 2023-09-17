# models.py

from .database import db

class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    aggregated_rating = db.Column(db.Float)
    aggregated_rating_count = db.Column(db.Integer)
    cover = db.Column(db.String(2000))
    genres = db.Column(db.String(2000))
    name = db.Column(db.String(2000))
    rating = db.Column(db.Float)
    rating_count = db.Column(db.Integer)
    release_dates = db.Column(db.String(2000))
    summary = db.Column(db.Text)
    url = db.Column(db.String(2000))
    websites = db.Column(db.String(2000))
    main_story = db.Column(db.Float)
    main_extra = db.Column(db.Float)
    completionist = db.Column(db.Float)
    storyline = db.Column(db.Text)
    unclean_summary = db.Column(db.Text)
    popularity = db.Column(db.Float)
