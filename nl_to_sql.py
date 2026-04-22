import sqlite3
import pandas as pd


# 🔹 Generate SQL
def generate_sql(query):
    query = query.lower()

    # ✅ Chart-friendly query
    if "orders by status" in query or "count orders by status" in query:
        return """
        SELECT order_status, COUNT(*) AS total_orders
        FROM orders
        GROUP BY order_status
        """

    elif "orders by state" in query:
        return """
        SELECT customer_state, COUNT(*) AS total_orders
        FROM customers
        GROUP BY customer_state
        """

    elif "how many orders" in query and "delivered" in query:
        return """
        SELECT COUNT(*) AS total_delivered_orders
        FROM orders
        WHERE order_status = 'delivered'
        """

    elif "total orders" in query:
        return "SELECT COUNT(*) AS total_orders FROM orders"

    elif "show orders" in query:
        return "SELECT * FROM orders LIMIT 5"

    else:
        return "SELECT * FROM orders LIMIT 5"


# 🔹 Run SQL
def run_sql(sql_query):
    conn = sqlite3.connect("olist.db")

    try:
        df = pd.read_sql(sql_query, conn)
    except Exception as e:
        df = pd.DataFrame({"error": [str(e)]})

    conn.close()
    return df


# 🔹 Explain result
def explain_result(query, df):
    if "error" in df.columns:
        return f"Error in query: {df['error'][0]}"

    return f"""
For your question: "{query}"

Here are the results:

{df.head().to_string(index=False)}
"""