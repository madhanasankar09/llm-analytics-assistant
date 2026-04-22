import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os
import requests

# ================= DOWNLOAD CSV =================
def download_file(file_id, filename):
    if not os.path.exists(filename):
        url = f"https://drive.google.com/uc?id={file_id}"
        r = requests.get(url)
        with open(filename, "wb") as f:
            f.write(r.content)

# 🔥 YOUR FILES
download_file("1AA2rpV0x69Ucz3L9G6JYHAMEMrYm3lXy", "olist_orders_dataset.csv")
download_file("14t7fxwoWCAAWCu1ALyVpKCJ3Fung1WTU", "olist_customers_dataset.csv")
download_file("1PUsNWOm4nf2AInniInUNOM4sYmCav5E8", "olist_order_reviews_dataset.csv")

# ================= CREATE DATABASE =================
DB_PATH = "olist.db"

def create_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)

        orders = pd.read_csv("olist_orders_dataset.csv")
        customers = pd.read_csv("olist_customers_dataset.csv")
        reviews = pd.read_csv("olist_order_reviews_dataset.csv")

        orders.to_sql("orders", conn, if_exists="replace", index=False)
        customers.to_sql("customers", conn, if_exists="replace", index=False)
        reviews.to_sql("order_reviews", conn, if_exists="replace", index=False)

        conn.close()

create_db()

# ================= IMPORT MODULES =================
from nl_to_sql import generate_sql, run_sql, explain_result
from embedder import create_embeddings
from retriever import retrieve_reviews

# ================= UI =================
st.set_page_config(page_title="LLM Analytics Assistant", layout="wide")
st.title("📊 LLM-Powered Analytics Assistant with RAG")

# ================= LOAD REVIEWS =================
@st.cache_data
def load_reviews():
    conn = sqlite3.connect(DB_PATH)
    data = conn.execute("""
        SELECT review_comment_message 
        FROM order_reviews 
        WHERE review_comment_message IS NOT NULL 
        LIMIT 500
    """).fetchall()
    conn.close()
    return [row[0] for row in data]

# ================= ROUTER =================
def classify_query(query):
    query = query.lower()
    if "review" in query or "customer" in query or "complaint" in query:
        return "RAG"
    return "SQL"

# ================= SENTIMENT =================
def analyze_reviews(reviews):
    positive_words = ["good", "excellent", "great", "bom", "excelente"]
    negative_words = ["bad", "delay", "late", "ruim", "atraso", "demora"]

    pos, neg = 0, 0
    issues = []

    for review in reviews:
        text = review.lower()

        if any(w in text for w in positive_words):
            pos += 1
        if any(w in text for w in negative_words):
            neg += 1

        if "atraso" in text or "demora" in text:
            issues.append("Delivery Delay")

    sentiment = "Positive" if pos > neg else "Negative" if neg > pos else "Mixed"
    return sentiment, list(set(issues))

# ================= MAIN =================
query = st.text_input("🔍 Ask your question:")

if query:
    route = classify_query(query)
    st.info(f"🔀 Route Selected: {route}")

    if route == "SQL":
        sql_query = generate_sql(query)
        df = run_sql(sql_query)

        st.subheader("📊 Data")
        st.dataframe(df)

        if df.shape[1] >= 2 and df.shape[0] <= 20:
            fig = px.bar(df, x=df.columns[0], y=df.columns[1])
            st.plotly_chart(fig)

    else:
        reviews = load_reviews()
        vectorizer, vectors = create_embeddings(reviews)
        top_reviews = retrieve_reviews(query, vectorizer, vectors, reviews)

        st.subheader("📌 Reviews")
        for r in top_reviews:
            st.write("-", r)

        sentiment, issues = analyze_reviews(top_reviews)

        st.subheader("📊 Sentiment")
        st.write(sentiment)

        st.subheader("⚠️ Issues")
        st.write(issues)
