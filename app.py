import streamlit as st
from sql.nl_to_sql import generate_sql, run_sql, explain_result
from rag.embedder import create_embeddings
from rag.retriever import retrieve_reviews
import sqlite3
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="LLM Assistant", layout="wide")


@st.cache_data
def load_reviews():
    conn = sqlite3.connect("olist.db")
    df = conn.execute("""
        SELECT review_comment_message 
        FROM order_reviews 
        WHERE review_comment_message IS NOT NULL 
        LIMIT 500
    """).fetchall()
    conn.close()
    return [row[0] for row in df]


def translate_query(query):
    query = query.lower()

    if "shipping" in query or "delivery" in query:
        return "entrega atraso demora"

    if "product" in query:
        return "produto qualidade"

    if "cancel" in query:
        return "cancelamento"

    return query


def analyze_reviews(reviews):
    positive_words = ["bom", "excelente", "ótimo", "good", "great"]
    negative_words = ["ruim", "atraso", "demora", "erro", "bad"]

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

        if "erro" in text:
            issues.append("Wrong Product")

        if "cancelamento" in text:
            issues.append("Cancellation Issue")

    sentiment = "Positive" if pos > neg else "Negative" if neg > pos else "Mixed"

    return sentiment, list(set(issues))


def classify_query(query):
    if "review" in query or "customer" in query or "complaint" in query:
        return "RAG"
    return "SQL"


# 🔥 TITLE FIXED
st.title("📊 LLM-Powered Analytics Assistant with RAG")

query = st.text_input("Ask your question:")

if query:
    route = classify_query(query)

    st.info(f"Route Selected: {route}")

    # ================= SQL =================
    if route == "SQL":
        sql_query = generate_sql(query)
        df = run_sql(sql_query)
        explanation = explain_result(query, df)

        st.subheader("SQL Query")
        st.code(sql_query)

        st.subheader("Data")
        st.dataframe(df)

        st.subheader("Explanation")
        st.write(explanation)

        # 🔥 CHART ADDITION
        if len(df.columns) >= 2:
            st.subheader("📊 Auto Chart")

            try:
                fig = px.bar(df, x=df.columns[0], y=df.columns[1])
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.write("Chart not supported for this query")

    # ================= RAG =================
    else:
        reviews = load_reviews()
        vectorizer, vectors = create_embeddings(reviews)

        translated_query = translate_query(query)

        top_reviews = retrieve_reviews(translated_query, vectorizer, vectors, reviews)
        sentiment, issues = analyze_reviews(top_reviews)

        st.subheader("Top Reviews")
        for r in top_reviews:
            st.write("-", r)

        st.subheader("Sentiment")
        st.write(sentiment)

        st.subheader("Issues")
        for issue in issues:
            st.write("-", issue)

        st.subheader("Summary")
        st.write(f"Customers show {sentiment} sentiment")