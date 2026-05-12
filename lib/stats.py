from lib.connect_db import connect_db

def get_product_stats(product_id):
    conn = connect_db()
    cur = conn.cursor()

    # Total IN
    cur.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM inventory_transactions
        WHERE product_id = %s AND transaction_type = 'IN'
    """, (product_id,))
    total_in = cur.fetchone()[0]

    # Total OUT
    cur.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM inventory_transactions
        WHERE product_id = %s AND transaction_type = 'OUT'
    """, (product_id,))
    total_out = cur.fetchone()[0]

    # Revenue (from sales table if you use it, fallback logic here)
    cur.execute("""
        SELECT COALESCE(SUM(total_price), 0)
        FROM sales_analytics
        WHERE product_id = %s
    """, (product_id,))
    revenue = cur.fetchone()[0]

    # Product price + stock
    cur.execute("""
        SELECT unit_price, current_stock
        FROM products
        WHERE product_id = %s
    """, (product_id,))
    product = cur.fetchone()

    conn.close()

    unit_price = product[0]
    stock = product[1]

    return {
        "total_in": total_in,
        "total_out": total_out,
        "revenue": revenue,
        "valuation": unit_price * stock
    }