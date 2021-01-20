from shoe_shopping import app, bcrypt, db, mail
import os, secrets
from shoe_shopping.forms import RegisterForm, LoginForm, ManagerForm, AddProductForm
from flask import render_template, url_for, redirect, flash, request, abort
from shoe_shopping.models import User, Product, Link
from flask_login import login_user, current_user, login_required, logout_user
from PIL import Image
from flask_mail import Message

@app.route('/')
@app.route('/intro', methods=['GET', 'POST'])
def intro():
    return render_template('intro.html', title="Welcome!")

@app.route('/home')
def home():
    return render_template('home.html', title="Home")

@app.route('/mens')
def mens():
    return render_template('mens.html', title="Men's shoes")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('You have been sccessfully logged in!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful, please check the email or password!', 'danger')
    return render_template('login.html', title="Login", form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You can login now!", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/manager_login', methods=['GET', 'POST'])
def manager_login():
    form = ManagerForm()
    if form.validate_on_submit():
        manager = User.query.filter_by(username=form.username.data).first()
        if manager and bcrypt.check_password_hash(manager.password, form.password.data) and manager.role == 'manager':
            login_user(manager, remember=False)
            flash('Welcome manager', 'success')
            return redirect(url_for('managment_page'))
    return render_template('manager_login.html', title="* Manager login", form=form)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_extention = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + file_extention
    picture_path = os.path.join(app.root_path, 'static/product_pictures', picture_filename)
    output_size = (125, 125)
    image = Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(picture_path)
    return picture_filename


@app.route('/managment_page', methods=['GET', 'POST'])
@login_required
def managment_page():
    form = AddProductForm()
    men_products = Product.query.filter_by(gender='male')
    female_products = Product.query.filter_by(gender='female')
    kids_products = Product.query.filter_by(gender='kids')
    if form.validate_on_submit():
        # image = save_picture(form.picture_file.data)
        product = Product(name=form.name.data, gender=form.gender.data, size=form.size.data, quantity=form.quantity.data, price=form.price.data)
        db.session.add(product)
        db.session.commit()
        flash('The product was added', 'success')
        return redirect(url_for('managment_page'))
    return render_template('managment_page.html', title='=== Manage ===', form=form, men_products=men_products, female_products=female_products, kids_products=kids_products)

@app.route('/managment_page/<int:product_barcode>/delete', methods=['POST'])
@login_required
def delete_product(product_barcode):
    product = Product.query.get_or_404(product_barcode)
    if current_user.role != 'manager':
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('The product has been removed from stock!', 'warning')
    return redirect(url_for('managment_page'))

@app.route('/managment_page/<int:product_barcode>/update', methods=['GET', 'POST'])
@login_required
def update_product(product_barcode):
    product = Product.query.get_or_404(product_barcode)
    form = AddProductForm()
    if request.method == 'GET':
        form.name.data = product.name
        form.gender.data = product.gender
        form.size.data = product.size
        form.quantity.data = product.quantity
        form.price.data = product.price
        form.submit.label.text = 'Update Post'
    if current_user.role != 'manager':
        abort(403)
    if form.validate_on_submit():
        product.name = form.name.data
        product.gender = form.gender.data
        product.size = form.size.data
        product.quantity = form.quantity.data
        product.price = form.price.data
        db.session.commit()
        flash('The product has been updated!', 'success')
        return redirect(url_for('managment_page'))
    return render_template('update_product.html', title='Update Product', form=form)

@app.route('/browse/<string:gender>')
@login_required
def browse(gender):
    products = Product.query.filter_by(gender=gender)
    return render_template('browse.html', title='Browse', products=products)

@app.route('/order/<int:product_barcode>')
@login_required
def order(product_barcode):
    product = Product.query.filter_by(barcode=product_barcode).first()
    if current_user.role == 'manager': abort(403)
    if product.quantity < 1:
        flash('There are no more products of this kind in stock!', 'danger')
        return redirect(url_for('home'))
    link = Link(user_id=current_user.id, product_barcode=product.barcode)
    product.quantity -= 1
    db.session.add(link)
    db.session.commit()
    flash('This product has been ordered!', 'success')
    return redirect(url_for('orders'))

@app.route('/orders')
@login_required
def orders():
    links = Link.query.filter_by(user_id=current_user.id)
    products = []
    for link in links:
        products.append(Product.query.filter_by(barcode=link.product_barcode).first_or_404())
    return render_template('orders.html', title='Your Orders', products=products)

@app.route('/order/<int:product_barcode>/cancel')
@login_required
def cancel(product_barcode):
    link = Link.query.filter_by(user_id=current_user.id, product_barcode=product_barcode).first_or_404()
    if current_user.id != link.user_id: abort(403)
    product = Product.query.filter_by(barcode=product_barcode).first_or_404()
    product.quantity += 1
    db.session.delete(link)
    db.session.commit()
    flash('The order has been cancelled!', 'warning')
    return redirect(url_for('orders'))

def send_product_email(product):
    msg = Message('Your Order in shoeshopping.com', sender='flask.user2020@gmail.com', recipients=[current_user.email])
    msg.body = f""" Thank you for choosing 'shoeshopping.com' to buy your shoes.


    Is there is anything wrong with the product, please don't hesitate to contact us!


    Product details: {product.name} that costs {product.price}.


    The product will arrive in three (3) days.

    Your's sincerely,
        The shoeshopping.com Team.
    """
    mail.send(msg)

@app.route('/order/<int:product_barcode>/finish')
@login_required
def finish(product_barcode):
    link = Link.query.filter_by(user_id=current_user.id, product_barcode=product_barcode).first_or_404()
    if current_user.id != link.user_id: abort(403)
    db.session.delete(link)
    db.session.commit()
    product = Product.query.filter_by(barcode=product_barcode).first()
    send_product_email(product)
    flash('The order has been made! Pleasure doing business with you!', 'success')
    return redirect(url_for('home'))
