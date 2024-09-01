from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

app = Flask(__name__)

@app.route("/")
@login_required
def index():
    """Render Home page"""
    pass

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    pass

@app.route("/logout")
def logout():
    """Log user out"""
    
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    pass