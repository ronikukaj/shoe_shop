from shoe_shopping import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    role = db.Column(db.String(7), default='user')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"

class Product(db.Model):
    barcode = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # image_file = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Product('{self.name}', '{self.gender}', '{self.size}')"

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    product_barcode = db.Column(db.Integer)
