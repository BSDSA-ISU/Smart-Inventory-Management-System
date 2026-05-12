import os
from matplotlib import pyplot as plt
from lib.connect_db import connect_db
import hashlib
import json
import textwrap


CHART_CONFIG = {
    "text_color": "#ffffff",
    "grid_color": "#444444",
    "axis_color": "#888888",
    "stock_line": "#10b981",  # Emerald Green
    "sales_line": "#38bdf8",  # Sky Blue
    "alert_color": "#ef4444", # Red
    
    "title_size": 20,
    "label_size": 10,
    "tick_size": 10
}


def wrap_label(text, width=25):
    return "\n".join(textwrap.wrap(text, width=width))

def get_data_hash(data):
    data_string = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(data_string.encode('utf-8')).hexdigest()

def apply_theme(ax):
    ax.patch.set_alpha(0.0) 
    ax.title.set_size(CHART_CONFIG["title_size"])
    ax.title.set_color(CHART_CONFIG["text_color"])
    ax.xaxis.label.set_size(CHART_CONFIG["label_size"])
    ax.xaxis.label.set_color(CHART_CONFIG["text_color"])
    ax.yaxis.label.set_size(CHART_CONFIG["label_size"])
    ax.yaxis.label.set_color(CHART_CONFIG["text_color"])
    ax.tick_params(axis='both', which='major', labelsize=CHART_CONFIG["tick_size"], colors=CHART_CONFIG["text_color"])
    for spine in ax.spines.values():
        spine.set_edgecolor(CHART_CONFIG["axis_color"])

def save_and_close(chart_type, data_hash):
    os.makedirs("static/graphs", exist_ok=True)
    path = f"static/graphs/{chart_type}_global.svg"
    hash_path = f"static/graphs/{chart_type}_global.hash"
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.subplots_adjust(left=0.35)
    plt.savefig(path, bbox_inches='tight', dpi=100, transparent=True)
    plt.close()
    
    with open(hash_path, "w") as f:
        f.write(data_hash)
    return path

def is_cache_valid(chart_type, current_hash):
    path = f"static/graphs/{chart_type}_global.svg"
    hash_path = f"static/graphs/{chart_type}_global.hash"
    if os.path.exists(path) and os.path.exists(hash_path):
        with open(hash_path, "r") as f:
            return f.read().strip() == current_hash
    return False

# --- NEW REFACTORED GRAPHS ---

def generate_sales_trend_chart():
    """Graphs total units sold per day (Stock Out)."""
    conn = connect_db()
    cur = conn.cursor()
    # Using DATE() to strip the time and group by day
    cur.execute("""
        SELECT DATE(transaction_date) as day, SUM(quantity)
        FROM inventory_transactions
        WHERE transaction_type = 'OUT'
        GROUP BY day
        ORDER BY day ASC
    """)
    data = cur.fetchall()
    conn.close()

    if not data: return None

    current_hash = get_data_hash(data)
    path = "static/graphs/sales_trend_global.svg"
    if is_cache_valid("sales_trend", current_hash): return path

    dates = [str(row[0]) for row in data]
    units = [row[1] for row in data]

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_alpha(0.0)
    ax.plot(dates, units, color=CHART_CONFIG["sales_line"], linewidth=3, marker='o')
    ax.set_title("Daily Sales Volume")
    ax.set_ylabel("Units Sold")
    apply_theme(ax)

    return save_and_close("sales_trend", current_hash)

def generate_category_distribution():
    """A Bar chart showing stock levels per category."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT category, SUM(current_stock) FROM products GROUP BY category")
    data = cur.fetchall()
    conn.close()

    if not data: return None

    current_hash = get_data_hash(data)
    path = "static/graphs/category_dist_global.svg"
    if is_cache_valid("category_dist", current_hash): return path

    categories = [row[0] for row in data]
    counts = [row[1] for row in data]

    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_alpha(0.0)
    ax.bar(categories, counts, color=CHART_CONFIG["stock_line"])
    ax.set_title("Stock by Category")
    ax.set_ylabel("Quantity in Vault")
    apply_theme(ax)

    return save_and_close("category_dist", current_hash)

def generate_inventory_health_chart():
    """Compares Current Stock vs Min Threshold for the top 5 products."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT product_name, current_stock, min_stock_level 
        FROM products 
        ORDER BY current_stock ASC 
    """)
    data = cur.fetchall()
    conn.close()

    if not data: return None

    current_hash = get_data_hash(data)
    path = "static/graphs/inv_health_global.svg"
    if is_cache_valid("inv_health", current_hash): return path

    names = [wrap_label(row[0], 25) for row in data]
    
    current = [row[1] for row in data]
    thresholds = [row[2] for row in data]

    # sets the height automatically
    n = len(names)
    fig_height = max(5, n * 0.6)

    fig, ax = plt.subplots(figsize=(10, fig_height))
    fig.patch.set_alpha(0.0)

    y = range(len(names))

    ax.barh(y, current, height=0.4,
            label='Current Stock',
            color=CHART_CONFIG["stock_line"])

    ax.barh([i + 0.4 for i in y], thresholds, height=0.4,
            label='Min Threshold',
            color=CHART_CONFIG["alert_color"])

    ax.set_yticks([i + 0.2 for i in y])
    ax.set_yticklabels(names)

    ax.set_title("Critical Stock Levels")
    ax.set_xlabel("Units")

    ax.legend()

    apply_theme(ax)

    return save_and_close("inv_health", current_hash)