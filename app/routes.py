# Defines routes for flask app

from flask import flash, get_flashed_messages, redirect, render_template, request, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector as sql
import time

from app import app, conn, cur
from .helpers import login_required
from app import helpers as h

# Auxilliary variables
run_id = 0
jobs_fetched = []
job_name = ""
location = ""
spider_time = 0

# HOW MANY SECONDS TO SCRAPE JOBS
SCRAPING_TIME = 60

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Render Home page"""

    global run_id, job_name, spider_time, location

    if request.method == "POST":
        if not request.form.get("job_name") or not request.form.get("location") or not request.form.getlist("sites"):
            flash("You should fill all the fields!", "fields_error")
            return redirect("/run")
        # Get form data
        job_name = request.form.get("job_name")
        location = request.form.get("location")
        sites = request.form.getlist("sites")
        run_id = int(time.time() * 1000) % 1000000
        spider_time = 0

        h.lookup_jobs(job_name, location, sites, run_id)

        return redirect("/run")
    else:
        return render_template("index.html")

@app.route("/run", methods=["GET", "POST"])
@login_required
def run():
    """Render Run page"""
    global job_name, run_id, spider_time, location

    if request.method == "POST":
        if not request.form.get("job_name") or not request.form.get("location") or not request.form.getlist("sites"):
            flash("You should fill all the fields!", "fields_error")
            return redirect("/run")
        
        # Get form data
        job_name = request.form.get("job_name")
        location = request.form.get("location")
        sites = request.form.getlist("sites")
        run_id = int(time.time() * 1000) % 1000000
        spider_time = 0

        h.lookup_jobs(job_name, location, sites, run_id)

        return redirect("/run")
    else:
        spider_time = 0
        # Fetch jobs from the database
        if job_name:
            jobs = h.fetch_jobs_from_db(job_name.strip(), location.strip())
            jobs = sorted(jobs, key=lambda job: job['published'], reverse=True)
        else:
            jobs = []
        return render_template("run.html", jobs=jobs, job_name=job_name, location=location)
    
@app.route('/api/jobs', methods=['GET'])
@login_required
def get_jobs():
    """Get newly added jobs from the database"""
    global jobs_fetched, spider_time, run_id, location

    # Stop all spiders after specified time
    spider_time += 2
    spiders_stopped = False
    if spider_time >= SCRAPING_TIME:
        h.stop_all_spiders()
        spiders_stopped = True

    jobs = h.fetch_new_jobs_from_db(run_id, location.strip())
    jobs = h.remove_duplicates(jobs, jobs_fetched)
    jobs_fetched.extend(jobs)

    return jsonify({
        'jobs': jobs,
        'spiders_stopped': spiders_stopped
    })

@app.route('/add_to_favorites', methods=['POST'])
@login_required
def add_to_favorites():
    """Add job to favorites"""
    job_data = request.json

    success = h.add_job_to_favorites(job_data)
    if success:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error'}), 500
    
@app.route('/remove_from_favorites', methods=['POST'])
@login_required
def remove_from_favorites():
    """Remove job from favorites"""
    job_data = request.json

    success = h.remove_job_from_favorites(job_data)
    if success:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error'}), 500

@app.route('/update_job_status', methods=['POST'])
@login_required
def update_job_status():
    """Update job status"""
    job_data = request.json
    success = h.update_job_status_in_db(job_data)
    if success:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error'}), 500
    
@app.route("/my_jobs", methods=["GET", "POST"])
@login_required
def my_jobs():
    """`Render My Jobs page"""
    if request.method == "POST":
        pass
    else:
        jobs = h.fetch_my_jobs_from_db()
        return render_template("my_jobs.html", jobs=jobs)


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