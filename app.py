from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy 
from flask_mail import Mail,Message 
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__smarttourNE__)
app.config['SECRET_KEY'] = "your-secret-key"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///smarttour.db"
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(200), nullable=False)

# Home Page (Splash Screen)
@app.route('/')
def index():
    return render_template('index.html')

# KYC Registration Page
@app.route('/kyc', methods=['GET', 'POST'])
def kyc():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        unique_id = "UID" + str(User.query.count() + 1)

        hashed_password = generate_password_hash(password)

        new_user = User(unique_id=unique_id, name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Send email with unique ID
        try:
            msg = Message("Smart Tour Registration Successful",
                          recipients=[email])
            msg.body = f"Hello {name},\n\nYour registration was successful!\nYour Unique ID: {unique_id}\nPlease use this ID along with your password to login.\n\nThank you!"
            mail.send(msg)
        except Exception as e:
            print("Email failed:", e)

        flash(f"Registration successful! Your Unique ID: {unique_id}", "success")
        return redirect(url_for('login'))

    return render_template('kyc.html')


# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        unique_id = request.form['unique_id']
        password = request.form['password']

        user = User.query.filter_by(unique_id=unique_id).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['unique_id'] = user.unique_id
            return redirect(url_for('dashboard'))  
        else:
            flash("Invalid Unique ID or Password", "danger")

    return render_template('login.html')

# Dashboard Page
@app.route('dashboard.html')
def dashboard():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

# Logout
@app.route('login.html')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login.html'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
