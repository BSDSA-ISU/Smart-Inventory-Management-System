from lib.connect_db import connect_db
from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user

# Updated Blueprints
stock_list_bp = Blueprint("stock_list", __name__)
add_product_bp = Blueprint("add_product", __name__)
delete_product_bp = Blueprint("delete_product", __name__)
product_view_bp = Blueprint("product_view", __name__)
edit_product_bp = Blueprint("edit_product", __name__)

# Stock webpage
@stock_list_bp.route("/inventory")
@login_required
def stock_list():
    search = request.args.get("search", "")

    conn = connect_db()
    cur = conn.cursor()

    # Querying the 'products' table from our refactored SQL
    if search:
        cur.execute("""
            SELECT product_id, product_name, sku_code, current_stock, min_stock_level
            FROM products
            WHERE product_name LIKE %s OR sku_code LIKE %s
        """, (f"%{search}%", f"%{search}%"))
    else:
        cur.execute("""
            SELECT product_id, product_name, sku_code, current_stock, min_stock_level
            FROM products
        """)

    products = cur.fetchall()
    conn.close()

    return render_template("stock_list.html", products=products, search=search, title="Inventory Stock")

# Add Product to Inventory
@add_product_bp.route("/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    # Keep your security check!
    if not current_user.role in ['admin', 'owner']:
        flash("🚫 Restrict Access: Warehouse Managers only!", "error")
        return redirect(url_for('login'))
    
    if request.method == "POST":
        # Mapping your athlete fields to business fields
        name = request.form["product_name"]
        sku = request.form["sku_code"]
        category = request.form["category"]
        price = request.form["unit_price"]
        stock = request.form["current_stock"]
        threshold = request.form["min_stock_level"]

        conn = connect_db()
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO products (product_name, sku_code, category, unit_price, current_stock, min_stock_level)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, sku, category, price, stock, threshold))
            conn.commit()
            flash("✅ Product vaulted successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"❌ Error: {str(e)}", "error")
        finally:
            conn.close()

        return redirect("/inventory")

    return render_template("add_product.html", title="Vault New Item")

@edit_product_bp.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    conn = connect_db()
    cur = conn.cursor()

    if request.method == "POST":
        try:
            # 1. Capture Core Product Info from form
            name = request.form["product_name"]
            sku = request.form["sku_code"]
            category = request.form["category"]
            price = request.form["unit_price"]
            stock = request.form["current_stock"]
            threshold = request.form["min_stock_level"]

            # 2. UPDATE the main product record first
            cur.execute("""
                UPDATE products 
                SET product_name=%s, sku_code=%s, category=%s, unit_price=%s, current_stock=%s, min_stock_level=%s
                WHERE product_id=%s
            """, (name, sku, category, price, stock, threshold, product_id))

            # 3. HANDLE STOCK IN (Restocks)
            quantities_in = request.form.getlist("qty_in[]")
            reasons_in = request.form.getlist("reason_in[]")
            dates_in = request.form.getlist("date_in[]")

            for i in range(len(quantities_in)):
                if quantities_in[i].strip():
                    cur.execute("""
                        INSERT INTO inventory_transactions (product_id, user_id, transaction_type, quantity, reason, transaction_date)
                        VALUES (%s, %s, 'IN', %s, %s, %s)
                    """, (product_id, current_user.id, quantities_in[i], reasons_in[i], dates_in[i]))
                    # Auto-increment the stock in the master table
                    cur.execute("UPDATE products SET current_stock = current_stock + %s WHERE product_id = %s", (quantities_in[i], product_id))

            # 4. HANDLE STOCK OUT (Sales/Orders)
            quantities_out = request.form.getlist("qty_out[]")
            reasons_out = request.form.getlist("reason_out[]")
            dates_out = request.form.getlist("date_out[]")

            for i in range(len(quantities_out)):
                if quantities_out[i].strip():
                    cur.execute("""
                        INSERT INTO inventory_transactions (product_id, user_id, transaction_type, quantity, reason, transaction_date)
                        VALUES (%s, %s, 'OUT', %s, %s, %s)
                    """, (product_id, current_user.id, quantities_out[i], reasons_out[i], dates_out[i]))
                    # Auto-decrement the stock in the master table
                    cur.execute("UPDATE products SET current_stock = current_stock - %s WHERE product_id = %s", (quantities_out[i], product_id))

            conn.commit()
            flash("✅ Vault Inventory Synchronized!", "success")
            return redirect(f"/product/{product_id}")

        except Exception as e:
            conn.rollback()
            flash(f"❌ Error: {str(e)}", "error")
            return redirect(url_for("edit_product.edit_product", product_id=product_id))
        finally:
            conn.close()

    cur.execute("""
        SELECT product_name, sku_code, category, unit_price, current_stock, min_stock_level 
        FROM products WHERE product_id=%s
    """, (product_id,))
    product = cur.fetchone()
    conn.close()

    if not product:
        flash("Product not found!", "error")
        return redirect("/inventory")

    return render_template("edit_product.html", product=product, product_id=product_id, title="Edit Vault Item")

# Delete product from the vault
@delete_product_bp.route("/delete_product/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    
    # Security check: Only Admins or Owners can remove assets
    if current_user.role not in ['admin', 'owner']:
        flash("🚫 Access Denied: You do not have permission to decommission assets.", "error")
        return redirect(url_for('stock_list.stock_list'))

    conn = connect_db()
    cur = conn.cursor()

    try:
        # Thanks to 'ON DELETE CASCADE' in our SQL, this will also 
        # automatically delete related transactions and analytics!
        cur.execute("DELETE FROM products WHERE product_id=%s", (product_id,))
        conn.commit()
        flash("📦 Product decommissioned and removed from vault.", "success")

    except Exception as e:
        conn.rollback()
        flash(f"❌ System Error: {str(e)}", "error")

    finally:
        conn.close()

    return redirect("/inventory")

@product_view_bp.route("/product/<int:product_id>")
@login_required
def product_details(product_id):
    conn = connect_db()
    cur = conn.cursor()

    # 1. Fetch Core Product Specs
    cur.execute("""
        SELECT product_name, sku_code, category, unit_price, current_stock, min_stock_level 
        FROM products WHERE product_id = %s
    """, (product_id,))
    product = cur.fetchone()

    # 2. Fetch Transaction History (The "Logs")
    cur.execute("""
        SELECT transaction_type, quantity, reason, transaction_date 
        FROM inventory_transactions 
        WHERE product_id = %s 
        ORDER BY transaction_date DESC
    """, (product_id,))
    history = cur.fetchall()

    # 3. Calculate Business Analytics (Replacing Athlete Stats)
    # Total Stock In
    cur.execute("SELECT SUM(quantity) FROM inventory_transactions WHERE product_id = %s AND transaction_type = 'IN'", (product_id,))
    total_in = cur.fetchone()[0] or 0  # pyright: ignore[reportOptionalSubscript]

    # Total Stock Out
    cur.execute("SELECT SUM(quantity) FROM inventory_transactions WHERE product_id = %s AND transaction_type = 'OUT'", (product_id,))
    total_out = cur.fetchone()[0] or 0  # pyright: ignore[reportOptionalSubscript]

    # Valuation (Price * Stock)
    vault_value = product[3] * product[4]  # pyright: ignore[reportOptionalSubscript]

    conn.close()

    return render_template(
        "product_view.html",
        product=product,
        history=history,
        total_in=total_in,
        total_out=total_out,
        valuation=vault_value,
        product_id=product_id,
        title="Product Intelligence"
    )