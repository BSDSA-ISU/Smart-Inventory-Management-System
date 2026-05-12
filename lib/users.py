from flask import Blueprint, Flask, render_template, request, redirect, flash, g, url_for
from flask_login import LoginManager, UserMixin, current_user, login_manager, login_user, login_required, logout_user
import matplotlib
matplotlib.use("Agg")
import os
from dotenv import load_dotenv
from lib.stocks import stock_list_bp, add_product_bp, edit_product_bp, delete_product_bp, product_view_bp
from lib.graphs import generate_category_distribution, generate_inventory_health_chart, generate_sales_trend_chart
from lib.line_count import get_loc as count
from lib.connect_db import connect_db
from werkzeug.security import check_password_hash, generate_password_hash
from lib.history import add_history

edit_user_bp = Blueprint("edit_user", __name__)
users_bp = Blueprint("users", __name__)
add_users_bp = Blueprint("add_user", __name__)

@edit_user_bp.route("/users/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    conn = connect_db()
    cur = conn.cursor()

    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]
            role = request.form["role"]
            full_name = request.form["full_name"]

            annual_salary = request.form["annual_salary"]
            department = request.form["department"]
            hire_date = request.form["hire_date"]

            # update without changing password if blank
            if password.strip():
                cur.execute("""
                    UPDATE users
                    SET username=%s,
                        password=%s,
                        role=%s,
                        full_name=%s,
                        annual_salary=%s,
                        department=%s,
                        hire_date=%s
                    WHERE user_id=%s
                """, (
                    username,
                    generate_password_hash(password),
                    role,
                    full_name,
                    annual_salary,
                    department,
                    hire_date,
                    user_id
                ))
            else:
                cur.execute("""
                    UPDATE users
                    SET username=%s,
                        role=%s,
                        full_name=%s,
                        annual_salary=%s,
                        department=%s,
                        hire_date=%s
                    WHERE user_id=%s
                """, (
                    username,
                    role,
                    full_name,
                    annual_salary,
                    department,
                    hire_date,
                    user_id
                ))

            # history log
            cur.execute("""
                INSERT INTO history_logs
                (user_id, action_type, description)
                VALUES (%s, %s, %s)
            """, (
                current_user.id,
                "UPDATE_PRODUCT",
                f"Updated account for {full_name}"
            ))

            conn.commit()

            flash("✅ User updated successfully", "success")
            return redirect(url_for("edit_user.edit_user", user_id=user_id))

        except Exception as e:
            conn.rollback()
            flash(f"❌ Error: {str(e)}", "error")

    cur.execute("""
        SELECT
            username,
            role,
            full_name,
            annual_salary,
            department,
            hire_date
        FROM users
        WHERE user_id=%s
    """, (user_id,))

    user = cur.fetchone()

    conn.close()

    return render_template(
        "edit_users.html",
        user=user,
        user_id=user_id,
        title="Edit User"
    )

@users_bp.route("/users")
@login_required
def users_list():
    search = request.args.get("search", "")

    conn = connect_db()
    cur = conn.cursor()

    if search:
        cur.execute("""
            SELECT user_id, full_name, username, role
            FROM users
            WHERE full_name LIKE %s OR username LIKE %s
        """, (f"%{search}%", f"%{search}%"))
    else:
        cur.execute("""
            SELECT user_id, full_name, username, role
            FROM users
        """)

    users = cur.fetchall()
    conn.close()

    return render_template("users.html", users=users, search=search, title="List of users")

@add_users_bp.route("/users/add", methods=["GET", "POST"])
@login_required
def add_user():
    if current_user.role not in ['admin', 'owner']:
        flash("🚫 Access Denied", "error")
        return redirect(url_for("users.users_list"))

    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]
            full_name = request.form["full_name"]
            role = request.form["role"]
            department = request.form["department"]
            annual_salary = request.form["annual_salary"]
            hire_date = request.form["hire_date"]

            conn = connect_db()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO users
                (username, password, full_name, role, department, annual_salary, hire_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                username,
                generate_password_hash(password),
                full_name,
                role,
                department,
                annual_salary,
                hire_date
            ))

            conn.commit()
            conn.close()

            add_history(
                current_user.id,
                "ADD_USER",
                f"Added new user: {full_name} ({role})"
            )

            flash("✅ Employee added successfully", "success")
            return redirect(url_for("users.users_list"))

        except Exception as e:
            flash(f"❌ Error: {str(e)}", "error")

    return render_template("add_user.html", title="Add Employee")