from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, login_required, LoginManager, logout_user, current_user, UserMixin
import random
from sqlalchemy.sql.expression import func

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///jk.db"
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

categories = [
    "accessories",
    "appliances",
    "bags & luggage",
    "beauty & health",
    "car & motorbike",
    "grocery & gourmet foods",
    "home & kitchen",
    "home, kitchen, pets",
    "industrial supplies",
    "kids' fashion",
    "men's clothing",
    "men's shoes",
    "music",
    "pet supplies",
    "sports & fitness",
    "stores",
    "toys & baby products",
    "tv, audio & cameras",
    "women's clothing",
    "women's shoes"
]

random.shuffle(categories)
categories=categories[0:5]

@login_manager.user_loader
def load_user(user_id):
    return Signup.query.get(int(user_id))

class Signup(UserMixin, db.Model):
    __tablename__ = 'login_info'
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    user_name = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    
    def get_id(self):
        return str(self.sno)

class user_product(db.Model):
    __tablename__='cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('login_info.sno'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    
    user = db.relationship('Signup', backref=db.backref('cart', lazy=True))


class Product(db.Model):
    __tablename__ = 'products_details_new'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    main_category = db.Column(db.String(255), nullable=False)
    sub_category = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    link = db.Column(db.String(255), nullable=True)
    ratings = db.Column(db.Float, nullable=True)
    no_of_ratings = db.Column(db.Integer, nullable=True)
    discount_price = db.Column(db.Float, nullable=False, default=0)
    actual_price = db.Column(db.Float, nullable=False, default=0)

@app.route('/')
def home():
    user_name = current_user.user_name if current_user.is_authenticated else None
    data = Product.query.filter_by(sub_category='Amazon Fashion').all()
    air = Product.query.filter_by(sub_category='Air Conditioners').all()
    electronics = Product.query.filter_by(sub_category='All Electronics').all()
    shoes = Product.query.filter_by(sub_category='All Home & Kitchen').all()
    
    random.shuffle(shoes)
    random.shuffle(electronics)
    random.shuffle(data)
    random.shuffle(air)
    
    shoes = shoes[0:4]
    electronics = electronics[0:4]
    air = air[:4]
    data = data[:4]
    
    return render_template('home.html',categories=categories,user_name=user_name, data=data, air=air, phones=electronics, shoes=shoes)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        user_name = request.form.get('user_name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not name or not user_name or not email or not password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('signup'))

        existing_user = Signup.query.filter_by(user_name=user_name).first()
        if existing_user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('signup'))

        new_user = Signup(name=name,categories=categories, user_name=user_name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/about')
def about():
    user_name = current_user.user_name if current_user.is_authenticated else None
    
    return render_template('about.html',user_name=user_name,categories=categories)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        user = Signup.query.filter_by(user_name=user_name).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html',categories=categories)



@app.route('/product_page/<int:product_id>', methods=['GET', 'POST'])
def product(product_id):
    user_name = current_user.user_name if current_user.is_authenticated else None
    product = Product.query.filter_by(id=product_id).first()
    recomended = Product.query.filter_by(sub_category=product.sub_category).all()
    random.shuffle(recomended)
    recomended=recomended[:4]
    all_products = Product.query.order_by(func.random()).limit(4).all()

    if request.method == 'POST':
        if 'add_to_cart' in request.form:
            if current_user.is_authenticated:
                existinng_product=user_product.query.filter_by(product_id=product.id).first()
                qt=request.form.get('quantity')
                if existinng_product:
                    existinng_product.quantity=qt
                    db.session.commit()
                    return redirect(url_for('product',product_id=product.id))
                new_cart_item = user_product(user_id=current_user.sno, product_id=product.id,quantity=qt)
                db.session.add(new_cart_item)
                db.session.commit()
                flash('Added to cart successfully!', 'success')

            else:
                flash('Please login to add items to your cart.', 'danger')

    return render_template('product_page.html',categories=categories, user_name=user_name, data=product, recomended=recomended, all_products=all_products)

@app.route('/products/<string:cat>',methods=['POST','GET'])
def products(cat):
    user_name = current_user.user_name if current_user.is_authenticated else None
    list_products=Product.query.filter_by(main_category=cat).all()
    return render_template('multiple_products.html',user_name=user_name,cat=cat,list=list_products,categories=categories)

@app.route('/cart',methods=['POST','GET'])
@login_required
def cart():
    user_name = current_user.user_name if current_user.is_authenticated else None
    cart_items = db.session.query(Product, user_product).join(user_product, Product.id == user_product.product_id).filter(user_product.user_id == current_user.sno).all()
    total = sum(item.discount_price * product.quantity for item, product in cart_items)
    if request.method == 'POST':
        if 'delete' in request.form :
            if current_user.is_authenticated:
                item_id=request.form.get('item_id')
                user=user_product.query.filter_by(product_id=item_id ,user_id=current_user.sno) .first()
                if user:
                    db.session.delete(user)
                    db.session.commit()
                    return redirect(url_for('cart'))

    
    return render_template('cart.html', cart_items=cart_items, user_name=user_name, total=total,categories=categories)



@app.route('/logout')
@login_required
def logout():
    flash('Thanks for using our website!')
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
