# VaultX — Password Manager

A secure, full-stack password manager built with Python Flask.

## Features
- 🔐 User registration and login
- 🔑 AES-256 encryption for all stored passwords
- ➕ Add, edit, and delete password entries
- 👁 Reveal passwords on demand
- 🗄️ SQLite database storage

## Tech Stack
- **Backend:** Python, Flask, SQLAlchemy
- **Database:** SQLite
- **Encryption:** Cryptography (Fernet)
- **Frontend:** HTML, CSS, JavaScript

## Setup
```bash
# Clone the repository
git clone https://github.com/Gauriivermaaa/password-manager.git
cd password-manager

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Project Structure
```
password_manager/
├── app.py           # Main Flask app & routes
├── models.py        # Database models
├── requirements.txt # Dependencies
├── templates/       # HTML pages
└── static/          # CSS styling
```

## Security
- Passwords encrypted with Fernet (AES-256)
- Master passwords hashed, never stored in plaintext
- Each user has a unique encryption key
