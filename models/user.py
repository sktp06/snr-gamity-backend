from models.database import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    # Convert, forward, store for readable
    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
        }
