from .database import db

class TopGame(db.Model):
    __tablename__ = 'topGame'

    id = db.Column(db.Integer, primary_key=True)
    aggregated_rating = db.Column(db.Float)
    aggregated_rating_count = db.Column(db.Integer)
    cover = db.Column(db.String(2000))
    genres = db.Column(db.String(2000))
    name = db.Column(db.Text(collation='utf8mb4_unicode_ci'))
    rating = db.Column(db.Float)
    rating_count = db.Column(db.Integer)
    release_dates = db.Column(db.String(2000))
    summary = db.Column(db.Text(collation='utf8mb4_unicode_ci'))
    url = db.Column(db.String(2000))
    websites = db.Column(db.String(2000))
    main_story = db.Column(db.Float)
    main_extra = db.Column(db.Float)
    completionist = db.Column(db.Float)
    storyline = db.Column(db.Text(collation='utf8mb4_unicode_ci'))
    unclean_name = db.Column(db.Text(collation='utf8mb4_unicode_ci'))
    unclean_summary = db.Column(db.Text(collation='utf8mb4_unicode_ci'))
    popularity = db.Column(db.Float)

    def __init__(self, id, aggregated_rating, aggregated_rating_count, cover, genres, name, rating, rating_count, release_dates, summary, url, websites, main_story, main_extra, completionist, storyline, unclean_name, unclean_summary, popularity):
        self.id = id
        self.aggregated_rating = aggregated_rating
        self.aggregated_rating_count = aggregated_rating_count
        self.cover = cover
        self.genres = genres
        self.name = name
        self.rating = rating
        self.rating_count = rating_count
        self.release_dates = release_dates
        self.summary = summary
        self.url = url
        self.websites = websites
        self.main_story = main_story
        self.main_extra = main_extra
        self.completionist = completionist
        self.storyline = storyline
        self.unclean_name = unclean_name
        self.unclean_summary = unclean_summary
        self.popularity = popularity

    @property
    def serialize(self):
        return {
            'id': self.id,
            'aggregated_rating': self.aggregated_rating,
            'aggregated_rating_count': self.aggregated_rating_count,
            'cover': self.cover,
            'genres': self.genres,
            'name': self.name,
            'rating': self.rating,
            'rating_count': self.rating_count,
            'release_dates': self.release_dates,
            'summary': self.summary,
            'url': self.url,
            'websites': self.websites,
            'main_story': self.main_story,
            'main_extra': self.main_extra,
            'completionist': self.completionist,
            'storyline': self.storyline,
            'unclean_name': self.unclean_name,
            'unclean_summary': self.unclean_summary,
            'popularity': self.popularity,
        }
