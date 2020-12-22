from flask_login import UserMixin
from app_contents import login, db
from werkzeug.security import check_password_hash, generate_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), index=True, unique=True)
    phone_num = db.Column(db.String(15), index=True, unique=True)
    app_group = db.Column(db.String(20))
    garage_access = db.Column(db.Integer)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
