from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "smarttour_secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smarttour.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    unique_id = db.Column(db.String(50), unique=True)

# --------------------- ROUTES ---------------------

# Splash Screen
@app.route('/')
def index():
    return render_template('index.html')

# KYC Registration
@app.route('/kyc', methods=['GET', 'POST'])
def kyc():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Generate unique ID
        unique_id = "UID" + str(User.query.count() + 1)

        # Hash password
        hashed_password = generate_password_hash(password)

        # Save to DB
        new_user = User(name=name, email=email, password=hashed_password, unique_id=unique_id)
        db.session.add(new_user)
        db.session.commit()

        flash(f"Registration successful! Your Unique ID is {unique_id}", "success")
        return redirect('/login')

    return render_template('kyc.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        unique_id = request.form['unique_id']
        password = request.form['password']

        # Check if user exists
        user = User.query.filter_by(unique_id=unique_id).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect('/dashboard')
        else:
            flash("Invalid Unique ID or Password", "danger")

    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect('login.html')

    return render_template('dashboard.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect('login.html')

# ------------------ MAIN ------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
