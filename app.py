from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, g
import time
import flask
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
import matplotlib
matplotlib.use("Agg")
import os
import sys
import pymysql
from dotenv import load_dotenv
from lib.nutrition import nutrition_bp, edit_nutrition_single_bp
from lib.recovery import recovery_bp, edit_recovery_single_bp
from lib.training import training_bp, edit_training_single_bp
from lib.athletes import athlete_list_bp, add_athlete_bp, delete_athlete_bp, edit_athlete_bp
from lib.graphs import generate_recovery_chart, generate_training_chart, generate_calorie_chart
from lib.goals import goals_bp, edit_goals_single_bp
from lib.line_count import get_loc as count
import platform
import psutil

load_dotenv()

# Dotenv stuffs
db_server = os.getenv("DB_SERVER", "localhost")
db_user = os.getenv("DB_USER", 'root')
db_password = os.getenv("DB_PASSWORD", "")
db_databasename = os.getenv("DB_DATABASE", "athlete_dashboard")
db_port = int(os.getenv("DB_PORT", 6969))

# adds error handling using secrert key
app = Flask(__name__)
app.secret_key = "Koishi11"

# Register components

# ADmin

## Managing athletes(CRUD)
app.register_blueprint(athlete_list_bp)
app.register_blueprint(add_athlete_bp)
app.register_blueprint(delete_athlete_bp)
app.register_blueprint(edit_athlete_bp)
## Edit nutritions
app.register_blueprint(nutrition_bp)
app.register_blueprint(edit_nutrition_single_bp)
## Edit recovery
app.register_blueprint(edit_recovery_single_bp)
app.register_blueprint(recovery_bp)
## Edit training
app.register_blueprint(edit_training_single_bp)
app.register_blueprint(training_bp)
## Edit goal
app.register_blueprint(goals_bp)
app.register_blueprint(edit_goals_single_bp)

# for login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # pyright: ignore[reportAttributeAccessIssue]


def connect_db():
    return pymysql.connect(
        host=db_server,
        user=db_user,
        password=db_password,
        database=db_databasename,
        cursorclass=pymysql.cursors.Cursor,
        autocommit=False
    )

# User class
class User(UserMixin):
    def __init__(self, id, username, password, role, name):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.name = name

    def is_admin(self):
        return self.role == "admin"


@login_manager.user_loader
def load_user(user_id):
    conn = connect_db()
    cur = conn.cursor()

    # Query the merged athletes table
    cur.execute("""
        SELECT athlete_id, username, password, role, name
        FROM athletes 
        WHERE athlete_id = %s
    """, (user_id,))
    
    user_data = cur.fetchone()
    conn.close()

    if user_data:
        # Assuming your User class accepts these parameters
        # You can now also pass 'name' if you want it available in current_user
        return User(user_data[0], user_data[1], user_data[2], user_data[3], name=user_data[4])
    return None

# login page landing
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = connect_db()
        cur = conn.cursor()

        # Check credentials in the athletes table
        cur.execute("""
            SELECT athlete_id, username, password, role, name
            FROM athletes
            WHERE username = %s
        """, (username,))
        
        user_data = cur.fetchone()
        conn.close()

        if user_data and user_data[2] == password:
            user_obj = User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
            login_user(user_obj)
            return redirect("/")
        else:
            flash("Invalid username or password", "error")

    return render_template("login.html")

# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

# Simple timer
@app.before_request
def start_timer():
    g.start_time = time.time()

# simple timer

@app.after_request
def add_latency(response):
    if hasattr(g, "start_time"):
        response.headers["X-Latency"] = str(round((time.time() - g.start_time) * 1000, 2)) + "ms"
    return response

# Landing pege
@app.route("/", methods=["GET"])
def index():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM athletes;")
    user_count = cur.fetchone()

    cur.execute("SELECT * FROM team_members")
    members = cur.fetchall()

    # default context (everyone gets this)
    context = {
        "usercount": user_count,
        "members": members
    }

    # 🔥 OWNER ONLY BLOCK (heavy stuff here)
    if current_user.is_authenticated and current_user.role == "owner":
        line_of_code = count()
        db_info = conn.get_host_info() if hasattr(conn, "get_host_info") else "unknown"

        cur.execute("SELECT VERSION();")
        mysql_version = cur.fetchone()

        context.update({
            "db_host": conn.host if hasattr(conn, "host") else "unknown",
            "db_user": conn.user if hasattr(conn, "user") else "unknown",
            "db_server_info": conn.get_server_info() if hasattr(conn, "get_server_info") else "pymysql",
            "mysql_version": mysql_version,
            "loc": line_of_code,
        
            # 🖥 OS INFO
            "os_name": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "arch": platform.machine(),
        
            # 🐍 PYTHON / FLASK
            "python_version": sys.version.split()[0],
            "flask_version": flask.__version__,  # pyright: ignore[reportAttributeAccessIssue]
        
            # ⚙️ SYSTEM USAGE
            "cpu_usage": psutil.cpu_percent(interval=0.2),
            "ram_usage": psutil.virtual_memory().percent,
        
            # ⏱ UPTIME
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
        })

    return render_template("index.html", **context)

@app.route("/athlete/<int:athlete_id>")
def athlete(athlete_id):
    conn = connect_db()
    cur = conn.cursor()

    # Fetch all Lists
    cur.execute("SELECT * FROM nutrition_logs WHERE athlete_id=%s ORDER BY log_date DESC", (athlete_id,))
    nutrition_logs = cur.fetchall()

    cur.execute("SELECT * FROM training_sessions WHERE athlete_id=%s ORDER BY session_date DESC", (athlete_id,))
    training_sessions = cur.fetchall()

    cur.execute("SELECT * FROM recovery_logs WHERE athlete_id=%s ORDER BY log_date DESC", (athlete_id,))
    recovery_logs = cur.fetchall()

    cur.execute("SELECT * FROM goals WHERE athlete_id=%s", (athlete_id,))
    goals = cur.fetchall()


    cur.execute("""SELECT name, age, weight, height
    FROM athletes WHERE athlete_id = %s
    """,
    (athlete_id,))
    
    athlete = cur.fetchone()

    cur.execute("""SELECT SUM(calories) FROM nutrition_logs
    WHERE athlete_id = %s""",
    (athlete_id,))
    
    total_calories = cur.fetchone()[0] or 0  # pyright: ignore[reportOptionalSubscript]

    cur.execute("""SELECT SUM(duration_minutes) FROM
    training_sessions WHERE athlete_id = %s""",
    (athlete_id,))
    
    total_training = cur.fetchone()[0] or 0  # pyright: ignore[reportOptionalSubscript]

    cur.execute("""SELECT AVG(recovery_score) FROM recovery_logs
    WHERE athlete_id = %s""",
    (athlete_id,))
    
    avg_recovery = cur.fetchone()[0] or 0  # pyright: ignore[reportOptionalSubscript]

    # 📊 charts
    calorie_chart = generate_calorie_chart(athlete_id)
    training_chart = generate_training_chart(athlete_id)
    recovery_chart = generate_recovery_chart(athlete_id)

    cur.execute("""
    SELECT goal_type, target_value, current_value, start_date, end_date
    FROM goals
    WHERE athlete_id = %s
    """, (athlete_id,))

    goals = cur.fetchall()

    cur.execute("""
    SELECT role
    FROM athletes
    WHERE athlete_id = %s
    """, (athlete_id,))

    role = cur.fetchall()

    conn.close()

    return render_template(
        "athlete.html",
        athlete=athlete,
        nutrition_logs=nutrition_logs,
        training_sessions=training_sessions,
        recovery_logs=recovery_logs,
        goals=goals,
        calories=total_calories,
        training=total_training,
        recovery=round(avg_recovery, 2),
        calorie_chart=calorie_chart,
        training_chart=training_chart,
        recovery_chart=recovery_chart,
        athlete_id=athlete_id,
        role=role[0][0]
    )

if __name__ == "__main__":
    app.run(debug=True, port=db_port, host="0.0.0.0")