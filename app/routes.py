from flask import flash, get_flashed_messages, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector as sql

from app import app, conn, cur
from .helpers import login_required

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Render Home page"""
    if request.method == "POST":
        
        return render_template("index.html")
    else:
        return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    if request.method == "POST":
        # Ensure username and password were submitted
        if not request.form.get("username") or not request.form.get("password"):
            flash("You should fill all the fields!", "fields_error")
            return redirect("/login")
        
        # Query database for username
        cur.execute(
            "SELECT * FROM users_logs WHERE username = %s", (request.form.get("username"), )
        )
        rows = cur.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0][2], request.form.get("password")
        ):
            flash("Invalid username and/or password!", "login_error")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0][1]

        return redirect("/")
        
    else:
        # Show message is registered successfully
        try:
            get_flashed_messages()[0][1]
            session.clear()
        except IndexError:
            session.clear()
        
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            flash("You should fill all the fields!", "fields_error")
            return redirect("/register")
        
        if request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords do not match!", "password_match_error")
            return redirect("/register")
        
        try:
            cur.execute("INSERT INTO users_logs (username, password_hash) VALUES (%s,%s)", 
                    (request.form.get("username"), 
                    generate_password_hash(request.form.get("password")))
            )
            conn.commit()
        except sql.Error as e:
            if e.errno == sql.errorcode.ER_DUP_ENTRY: 
                flash("Username already exists!", "username_error")
            return redirect("/register")
        except Exception as e:
            flash(f"An unexpected error occurred: {e}", "error")
            return redirect("/register")

        flash("Registered successfully!", "success")
        return redirect("/")
    else:
        return render_template("register.html")