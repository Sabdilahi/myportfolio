# Backend: app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import os

app = Flask(__name__, template_folder="HTML")
app.secret_key = "your_secret_key"  # Required for flash messages

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///submissions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure email (Use environment variables for security)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Set in .env or terminal
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # App Password (Recommended)
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']  # Sender email

mail = Mail(app)

# Define the database model
class ContactSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

# Serve the main page
@app.route('/')
def home():
    return render_template('index.html')

# Handle contact form submission
@app.route('/contact', methods=['POST'])
def contact():
    try:
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Save to database
        submission = ContactSubmission(name=name, email=email, message=message)
        db.session.add(submission)
        db.session.commit()

        # Send email notification
        msg = Message("New Contact Form Submission",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[app.config['MAIL_USERNAME']])  # Send to yourself
        msg.body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        mail.send(msg)

        flash("Message sent successfully!", "success")
    except Exception as e:
        flash(f"Error sending message: {e}", "danger")

    return redirect(url_for('home'))

# Admin route to view submissions
@app.route('/admin/submissions')
def view_submissions():
    submissions = ContactSubmission.query.all()
    return render_template('submissions.html', submissions=submissions)

if __name__ == '__main__':
    app.run(debug=True)
