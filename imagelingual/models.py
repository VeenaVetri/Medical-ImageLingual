from datetime import datetime
from imagelingual import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    preferred_lang = db.Column(db.String(5))
    country = db.Column(db.String(30))

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.preferred_lang}', '{self.country}')"
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_links = db.Column(db.String(800), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"   