from flask import Flask, render_template, request, redirect, flash, g
from flask_login import LoginManager, UserMixin, current_user, login_manager, login_user, login_required, logout_user
import matplotlib
from werkzeug.security import check_password_hash
matplotlib.use("Agg")
import os
from dotenv import load_dotenv
from lib.stocks import stock_list_bp, add_product_bp, edit_product_bp, delete_product_bp, product_view_bp
from lib.graphs import generate_category_distribution, generate_inventory_health_chart, generate_sales_trend_chart, generate_revenue_trend_chart
from lib.line_count import get_loc as count
from lib.connect_db import connect_db
from lib.users import add_users_bp, edit_user_bp, users_bp

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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # pyright: ignore[reportAttributeAccessIssue]

app.register_blueprint(stock_list_bp)
app.register_blueprint(add_product_bp)
app.register_blueprint(edit_product_bp)
app.register_blueprint(delete_product_bp)
app.register_blueprint(product_view_bp)
app.register_blueprint(edit_user_bp)
app.register_blueprint(users_bp)
app.register_blueprint(add_users_bp)

# Updated User class - Cleaner and matches the new 'users' table
class User(UserMixin):
    def __init__(self, id, username, role, name):
        self.id = id
        self.username = username
        self.role = role
        self.name = name

@login_manager.user_loader
def load_user(user_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, role, full_name FROM users WHERE user_id = %s", (user_id,))
    user_data = cur.fetchone()
    conn.close()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2], user_data[3])
    return None

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, username, password, role, full_name
            FROM users
            WHERE username = %s
        """, (username,))

        user = cur.fetchone()
        conn.close()

        # Simple password check (consider hashing later if you have time!)
        if user and check_password_hash(user[2], password):
            login_user(User(user[0], user[1], user[2], user[3]))
            return redirect("/")
        else:
            flash("❌ Invalid credentials", "error")
    return render_template("login.html")

# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route("/", methods=["GET"])
def index():
    conn = connect_db()
    cur = conn.cursor()

    # SMART INVENTORY STATS
    cur.execute("SELECT COUNT(*) FROM products;")
    product_count = cur.fetchone()[0]  # pyright: ignore[reportOptionalSubscript]

    cur.execute("SELECT COUNT(*) FROM products WHERE current_stock <= min_stock_level;")
    low_stock_count = cur.fetchone()[0]  # pyright: ignore[reportOptionalSubscript]

    cur.execute("SELECT * FROM team_members")
    members = cur.fetchall()
    cur.execute("""
        SELECT
            h.action_type,
            h.description,
            h.created_at,
            u.username
        FROM history_logs h
        JOIN users u ON h.user_id = u.user_id
        ORDER BY h.created_at DESC
        LIMIT 7
    """)

    recent_logs = cur.fetchall()

    conn.close()

    return render_template("index.html", 
    product_count=product_count, 
    low_stock_alert=low_stock_count, 
    members=members,
    recent_logs=recent_logs
    )


@app.route("/statistics")
@login_required
def statistics():
    # Trigger the graph generation (with your hashing/caching logic)
    sales_chart = generate_sales_trend_chart()
    dist_chart = generate_category_distribution()
    health_chart = generate_inventory_health_chart()
    revenue_chart = generate_revenue_trend_chart()
    
    # Get some quick raw numbers for the "Counter" boxes
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM products")
    total_items = cur.fetchone()[0]  # pyright: ignore[reportOptionalSubscript]
    
    cur.execute("SELECT SUM(current_stock * unit_price) FROM products")
    total_value = cur.fetchone()[0] or 0  # pyright: ignore[reportOptionalSubscript]
    conn.close()

    return render_template(
        "statistics.html",
        sales_chart=sales_chart,
        revenue_chart=revenue_chart,
        dist_chart=dist_chart,
        health_chart=health_chart,
        total_items=total_items,
        total_value=total_value,
        title="Vault Analytics"
    )

if __name__ == "__main__":
    app.run(debug=True, port=db_port, host="0.0.0.0")