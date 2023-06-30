from models.database import db


class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')  # Add the 'role' column with a default value of 'user'

    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

    # Convert, forward, store for readable
    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'role': self.role
        }
