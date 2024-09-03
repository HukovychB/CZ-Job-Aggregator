import os
from flask import Flask
from flask_session import Session
import mysql.connector as sql

# Flask app
app = Flask(__name__)

# Flask-Session
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# MySQL connection
conn = sql.connect(
    host="localhost",
    user="bohdan",
    password=os.getenv("MYSQL_PASSWORD"),
    database="CZ_Job_Aggregator"
)

cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS users_logs (
        id INT AUTO_INCREMENT NOT NULL,
        username VARCHAR(255) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        PRIMARY KEY (id)
        )
        """)

from app import routes