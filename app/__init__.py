# Initialize Flask app and create MySQL tables

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
    database="CZ_Job_Aggregator",
)

cur = conn.cursor()

# TABLES

# USERS LOGS
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS users_logs (
        id INT AUTO_INCREMENT NOT NULL,
        username VARCHAR(255) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        PRIMARY KEY (id)
        )
        """
)

# ACTIVE JOBS
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS jobs_active(
        id INT AUTO_INCREMENT NOT NULL, 
        run_id INT,
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        title VARCHAR(255),
        link VARCHAR(1024),
        company VARCHAR(255),
        location VARCHAR(255),
        salary VARCHAR(255),
        published DATETIME,
        source VARCHAR(255),
        PRIMARY KEY (id)
    )
    """
)

# INACTIVE JOBS
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS jobs_inactive(
        id INT AUTO_INCREMENT NOT NULL, 
        run_id INT,
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        title VARCHAR(255),
        link VARCHAR(1024),
        company VARCHAR(255),
        location VARCHAR(255),
        salary VARCHAR(255),
        published DATETIME,
        source VARCHAR(255),
        PRIMARY KEY (id)
    )
    """
)

# Fovorite jobs
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS favorite_jobs(
        id INT AUTO_INCREMENT NOT NULL, 
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id INT,
        title VARCHAR(255),
        link VARCHAR(1024),
        company VARCHAR(255),
        location VARCHAR(255),
        salary VARCHAR(255),
        published VARCHAR(255),
        status VARCHAR(255),
        PRIMARY KEY (id),
        FOREIGN KEY (user_id) REFERENCES users_logs(id)
    )
    """
)

# Move jobs older than 30 days from jobs_active to jobs_inactive
cur.execute(
    """
    INSERT INTO jobs_inactive (run_id, time, title, link, company, location, salary, published, source)
    SELECT run_id, time, title, link, company, location, salary, published, source
    FROM jobs_active
    WHERE published < NOW() - INTERVAL 30 DAY
    """
)

cur.execute(
    """
    DELETE FROM jobs_active
    WHERE published < NOW() - INTERVAL 30 DAY
    """
)

conn.commit()


from app import routes
