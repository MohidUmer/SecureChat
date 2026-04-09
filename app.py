# Mohid Umer
# 23i-2130
# SecureChat - A Flask-based Chat Application with Enhanced Security Features

from flask import Flask, render_template, request, redirect, session, flash, url_for, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import secrets
import os
import sys

# Ensure the root directory is in the path so imports like 'forms' work on Vercel
sys.path.append(os.path.dirname(__file__))

from forms import RegistrationForm, LoginForm, MessageForm

# Task 4: Environmental Secret Management
load_dotenv() # Loads variables from .env into the system

# Secure the Server Header (Customization)
try:
    from werkzeug.serving import WSGIRequestHandler
    # Override version_string() — the actual method Werkzeug calls to build the Server header.
    WSGIRequestHandler.version_string = lambda self: 'SecureChat'
except ImportError:
    pass

app = Flask(__name__)
# Task 4: Load secret key from environment
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(24))

# Task 1: Security Headers via Talisman
# Instructs the browser to block malicious behavior like clickjacking.
# force_https=False for local dev (no SSL cert required)
Talisman(app, force_https=False, content_security_policy=None)

# Task 2: Rate Limiting
# Stop "Bot" attacks from guessing passwords thousands of times.
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)



# Task 3: Secure Cookies
app.config.update(
    SESSION_COOKIE_SECURE=True, # Only sends cookie over HTTPS
    SESSION_COOKIE_HTTPONLY=True, # Prevents JS access to cookies
    SESSION_COOKIE_SAMESITE='Lax', # Mitigates CSRF
)

# Task 3: Secure File Uploads
# Ensure uploaded files cannot "trick" the server into running them as code.
# On Vercel, we must use /tmp for any writeable operations.
if os.environ.get('VERCEL'):
    UPLOAD_FOLDER = '/tmp/uploads'
else:
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'doc', 'docx', 'zip'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB limit
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Task 3: Enable CSRF Protection
app.config['WTF_CSRF_ENABLED'] = True
csrf = CSRFProtect(app)

# Task 5: Initialize Bcrypt
bcrypt = Bcrypt(app)

# Task 4: Database URI from environment
# On Vercel, sqlite must be in /tmp
database_url = os.getenv('DATABASE_URL')

# Fix for legacy 'postgres://' URLs which cause SQLAlchemy to crash
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

if os.environ.get('VERCEL') and (not database_url or database_url.startswith('sqlite')):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/securechat.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///securechat.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

# Ensure tables are created on startup (essential for transient /tmp sqlite)
with app.app_context():
    db.create_all()


# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # Task 5: RBAC Field
    is_admin = db.Column(db.Boolean, default=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    message = db.Column(db.String(500))
    attachments = db.relationship('FileAttachment', backref='message', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"{self.id} - {self.username}"

class FileAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # bytes

    def __repr__(self):
        return f"Attachment({self.original_name})"

# Task 5: Role-Based Access Control (RBAC) Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            abort(403)
        user = db.session.get(User, user_id)
        if not user or not user.is_admin:
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

# Routes for Registration and Login (Task 5)
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Task 5: Hash password during registration
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        try:
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Username or Email already exists.', 'danger')
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
@limiter.limit("5 per minute") # Task 2: Rate Limiting
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Task 5: Verify password during login
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('You have been logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

# Homepage
@app.route("/", methods=['GET', 'POST'])
def index():
    form = MessageForm()
    if 'username' in session and request.method == "GET":
        form.username.data = session['username']
        
    if form.validate_on_submit():
        new_message = Message(username=form.username.data, message=form.message.data)
        db.session.add(new_message)
        db.session.flush()  # get new_message.id before commit

        # Task 3: Secure File Upload logic
        uploaded_files = request.files.getlist('attachments')
        for f in uploaded_files:
            if f and f.filename and allowed_file(f.filename):
                # secure_filename removes paths like ../../etc/passwd
                filename = secure_filename(f.filename)
                # Prefix with message id to avoid collisions
                stored_name = f"{new_message.id}_{filename}"
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], stored_name))
                attachment = FileAttachment(
                    message_id=new_message.id,
                    original_name=f.filename,
                    stored_name=stored_name,
                    file_size=os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], stored_name))
                )
                db.session.add(attachment)

        db.session.commit()
        return redirect(url_for('index'))

    all_messages = Message.query.all()
    return render_template("index.html", messages=all_messages, form=form)

# Serve uploaded files
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    safe = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe)
    if not os.path.exists(file_path):
        abort(404)
    return send_from_directory(app.config['UPLOAD_FOLDER'], safe, as_attachment=True)

# Task 5: Role-Based Access Control (RBAC) Route
@app.route("/admin/delete_user/<int:user_id>", methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    # Only users with is_admin=True can reach this line
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user_id} deleted successfully.', 'success')
    return redirect(url_for('index'))

# Delete message with Security Verification
@app.route("/delete/<int:id>", methods=['GET', 'POST'])
@login_required
def delete(id):
    message = Message.query.get_or_404(id)

    # Ownership check: only the message author or an admin can delete
    current_user = db.session.get(User, session.get('user_id'))
    if current_user and message.username != current_user.username and not current_user.is_admin:
        abort(403)

    if request.method == "POST":
        user_code = request.form.get('security_code')
        actual_code = session.get('delete_code')

        if user_code == str(actual_code):
            # Delete associated uploaded files from disk
            for att in message.attachments:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], att.stored_name)
                if os.path.exists(filepath):
                    os.remove(filepath)
            db.session.delete(message)
            db.session.commit()
            flash('Message deleted successfully.', 'success')
            return redirect(url_for('index'))
        else:
            return render_template("confirm_delete.html", message=message, code=actual_code, error="SECURITY_CODE_MISMATCH: Access Denied.")

    # Generate cryptographically secure 4-digit security code
    code = secrets.randbelow(9000) + 1000
    session['delete_code'] = code

    return render_template("confirm_delete.html", message=message, code=code)

# Update message
@app.route("/update/<int:id>", methods=['GET', 'POST'])
@login_required
def update(id):
    message = Message.query.get_or_404(id)

    # Ownership check: only the message author or an admin can edit
    current_user = db.session.get(User, session.get('user_id'))
    if current_user and message.username != current_user.username and not current_user.is_admin:
        abort(403)

    form = MessageForm()
    
    if form.validate_on_submit():
        message.username = form.username.data
        message.message = form.message.data
        db.session.commit()
        flash('Message updated successfully.', 'success')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.username.data = message.username
        form.message.data = message.message

    return render_template("update.html", message=message, form=form)

# About page
@app.route("/about")
def about():
    return render_template("about.html")

# Task 4: Custom Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    # If we are debugging or on Vercel and want to see the error
    if os.environ.get('VERCEL'):
        import traceback
        error_details = traceback.format_exc()
        return f"Internal Server Error Traceback:\n{error_details}", 500
    return render_template('500.html'), 500

if __name__ == "__main__":
    # Task 4: Disable Debug Mode
    app.run(debug=False)
