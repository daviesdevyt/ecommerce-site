from . import db
from flask_login import UserMixin

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    price = db.Column(db.Integer)
    img = db.Column(db.String(64))

class CartProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    price = db.Column(db.Integer)
    img = db.Column(db.String(64))
    quantity = db.Column(db.Integer, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    def __init__(self, product, user_id):
        self.name = product.name
        self.price = product.price
        self.img = product.img
        self.user_id = user_id

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), nullable=True)
    username = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))
    salt = db.Column(db.String(128))
    cart = db.relationship("CartProduct")
    
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    msg = db.Column(db.Text, unique=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(64), nullable=True)
    cart = db.Column(db.PickleType())
