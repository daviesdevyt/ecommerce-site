from flask import Blueprint, render_template, jsonify, request
from flask.helpers import flash, url_for
from flask_login import login_required,  current_user
from werkzeug.utils import redirect, secure_filename
from flask import json
from werkzeug.wrappers import response
from .models import CartProduct, Message, Order, Product, User
from .libs import *
from . import error_msg
import os
from cryptography.fernet import Fernet
views = Blueprint('views', __name__)


key = b'hTZPyOG_RqawMEjiZtKtAJPy6OfLqGnoxc7-uHGbVUM='
def encrypt(text, is_byte=False):
    if not is_byte:
        text = text.encode()
    f = Fernet(key)
    encrypted = f.encrypt(text)
    v =  encrypted.decode()
    return v

def decrypt(text, is_byte=False):
    if not is_byte:
        text = text.encode()
    f = Fernet(key)
    decrypted = f.decrypt(text)
    v =  decrypted.decode()
    return v

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_pic(pic):
    filename = secure_filename(pic.filename)
    pic.save(os.path.join("website/static/imgs", filename))
    return filename

@views.route('/')
def home():
    return render_template('index.html', user=current_user, products=Product.query.all())

@views.route('/contact-us', methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        message = request.form['message']
        for i in message:
            if i != " ":
                msg = Message(msg=encrypt(message))
                db.session.add(msg)
                db.session.commit()
                flash("Message sent", category="success")
                break
    return render_template('contact.html', user=current_user)

@views.route('/add-to-cart', methods=["POST"])
@login_required
def add_to_cart():
    data = loads(request.data)
    product_id = data['product_id']
    product = Product.query.get(product_id)
    if product:
        new_cart_product = CartProduct(product, current_user.id)
        db.session.add(new_cart_product)
        db.session.commit()
    return jsonify({})

@views.route('/remove-from-cart', methods=["POST"])
@login_required
def remove_from_cart():
    data = loads(request.data)
    product_id = data['product_id']
    product = CartProduct.query.get(product_id)
    if product:
        if product.user_id == current_user.id:
            db.session.delete(product)
            db.session.commit()
    return jsonify({})


@views.route('/edit-quantity', methods=["POST"])
@login_required
def edit_quantity():
    data = loads(request.data)
    product_id = data['product_id']
    op = data['operation']
    product = CartProduct.query.get(product_id)
    if product:
        if product.user_id == current_user.id:
            if op == 1:
                product.quantity += 1
            elif op == 0 and product.quantity > 1:
                product.quantity -= 1
            db.session.commit()
    return jsonify({})

@views.route('/cart', methods=["GET", "POST"])
@login_required
def cart():
    if request.method == "POST":
        email = request.form.get('email')
        phone = request.form.get('phone')
        if not (phone or email):
            flash("You must give at least one contact info", category="danger")
        else:
            if phone:
                phone = encrypt(phone)
            if email:
                email = encrypt(email)
            cart = CartProduct.query.filter_by(user_id=current_user.id).all()
            new_order = Order(phone=phone, email=email, cart=cart)
            db.session.add(new_order)
            db.session.commit()
            flash("Order sent successfully. We will contact you  as soon as possible", category="success")
    return render_template('cart.html', user=current_user)

@views.route('/admin', methods=["GET", "POST"])
@login_required
def admin():
    if not (current_user.id == 1 and current_user.username == 'admin' and current_user.password == hash_password("password", current_user.salt)):
        return redirect(url_for("views.home"))
    if request.method == "POST":
        _type = request.form['type']
        if _type == "order_completed":
            order_id = request.form['order_id']
            order = Order.query.get(int(order_id))
            db.session.delete(order)
            db.session.commit()
            return redirect(request.url)
        elif _type == "delete_message":
            msg_id = request.form['msg_id']
            msg = Message.query.get(int(msg_id))
            db.session.delete(msg)
            db.session.commit()
            return redirect(request.url)
        elif _type == "read_messages":
            messages = []
            for i in Message.query.all():
                msg = decrypt(i.msg)
                new_msg = {"msg": msg, "id": i.id}
                messages.append(new_msg)
            return render_template('admin-messages.html', user=current_user, msgs=messages)
        elif _type == "view_orders":
            orders = []
            for order in Order.query.all():
                items = []
                try:
                    phone = decrypt(order.phone)
                except:
                    phone = None
                try:
                    email = decrypt(order.email)
                except:
                    email = None
                for item in order.cart:
                    items.append({"q": item.quantity, 'name': item.name})
                orders.append({"id": order.id, "phone": phone, "email": email, "items": items})
            print(orders)
            return render_template("admin-orders.html", user=current_user, orders=orders)
        elif _type != "delete":
            pic = request.files['photo']
            price = request.form['price']
        name = request.form['name']
        product = Product.query.filter_by(name=name).first()
        if _type == 'add':
            if product:
                flash("Product already exisits", category="danger")
            else:
                if pic and allowed_file(pic.filename):
                    filename = save_pic(pic)
                    new_product = Product(name=name, price=int(price), img=filename)
                    db.session.add(new_product)
                    db.session.commit()
                    flash("Product is added successfully", category="success")
                else:
                    flash("Only image files are suppported", category="danger")
        elif _type == "update":
            new_name = request.form['new_name']
            if product:
                if pic and allowed_file(pic.filename):
                    filename = save_pic(pic)
                    product.img = filename
                if price:
                    product.price = int(price)
                if new_name:
                    product.name = new_name
                db.session.commit()
                flash("Product updated", category="success")
            else:
                flash("Product doesnt exisit", category="danger")
        elif _type == "delete":
            if product:
                os.remove(os.path.join("website/static/imgs", product.img))
                db.session.delete(product)
                db.session.commit()
                flash("Product deleted", category="success")
    return render_template("admin.html", user=current_user)
