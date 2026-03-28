from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, User, PasswordEntry
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vaultx.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        confirm  = request.form.get('confirm_password')
        if not username or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return render_template('register.html')
        key  = Fernet.generate_key().decode()
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            encryption_key=key
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    entries = PasswordEntry.query.filter_by(user_id=session['user_id']).all()
    return render_template('dashboard.html', entries=entries)

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title    = request.form.get('title').strip()
        username = request.form.get('username').strip()
        password = request.form.get('password')
        url      = request.form.get('url').strip()
        notes    = request.form.get('notes').strip()
        user     = User.query.get(session['user_id'])
        cipher   = Fernet(user.encryption_key.encode())
        encrypted = cipher.encrypt(password.encode()).decode()
        entry = PasswordEntry(
            user_id=session['user_id'],
            title=title,
            username=username,
            encrypted_password=encrypted,
            url=url,
            notes=notes
        )
        db.session.add(entry)
        db.session.commit()
        flash(f'"{title}" saved!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_entry.html')

@app.route('/reveal/<int:entry_id>')
def reveal(entry_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    entry  = PasswordEntry.query.filter_by(id=entry_id, user_id=session['user_id']).first_or_404()
    user   = User.query.get(session['user_id'])
    cipher = Fernet(user.encryption_key.encode())
    plain  = cipher.decrypt(entry.encrypted_password.encode()).decode()
    return jsonify({'password': plain})

@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    entry = PasswordEntry.query.filter_by(id=entry_id, user_id=session['user_id']).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash(f'"{entry.title}" deleted.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    entry  = PasswordEntry.query.filter_by(id=entry_id, user_id=session['user_id']).first_or_404()
    user   = User.query.get(session['user_id'])
    cipher = Fernet(user.encryption_key.encode())
    if request.method == 'POST':
        entry.title    = request.form.get('title').strip()
        entry.username = request.form.get('username').strip()
        entry.url      = request.form.get('url').strip()
        entry.notes    = request.form.get('notes').strip()
        new_pw = request.form.get('password')
        if new_pw:
            entry.encrypted_password = cipher.encrypt(new_pw.encode()).decode()
        db.session.commit()
        flash(f'"{entry.title}" updated!', 'success')
        return redirect(url_for('dashboard'))
    decrypted = cipher.decrypt(entry.encrypted_password.encode()).decode()
    return render_template('edit_entry.html', entry=entry, decrypted_password=decrypted)

if __name__ == '__main__':
    app.run(debug=True)
