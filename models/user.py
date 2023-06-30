from models.database import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')
    game_id = db.Column(db.Integer, nullable= True)

    def __init__(self, username, password, game_id, role):
        self.username = username
        self.password = password
        self.game_id = game_id
        self.role = role

    # Convert, forward, store for readable
    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'role': self.role,
            'game_id': self.game_id,
        }
