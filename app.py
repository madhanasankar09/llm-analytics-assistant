import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import importlib.util

# ================== LOAD MODULES (FIXED) ==================

# 🔹 Load SQL module
spec_sql = importlib.util.spec_from_file_location(
    "nl_to_sql", "nl_to_sql.py"
)
sql_module = importlib.util.module_from_spec(spec_sql)
spec_sql.loader.exec_module(sql_module)

generate_sql = sql_module.generate_sql
run_sql = sql_module.run_sql
explain_result = sql_module.explain_result


# 🔹 Load RAG embedder
spec_embed = importlib.util.spec_from_file_location(
    "embedder", "embedder.py"
)
embed_module = importlib.util.module_from_spec(spec_embed)
spec_embed.loader.exec_module(embed_module)

create_embeddings = embed_module.create_embeddings


# 🔹 Load RAG retriever
spec_ret = importlib.util.spec_from_file_location(
    "retriever", "retriever.py"
)
ret_module = importlib.util.module_from_spec(spec_ret)
spec_ret.loader.exec_module(ret_module)

retrieve_reviews = ret_module.retrieve_reviews


# ================== PAGE CONFIG ==================
st.set_page_config(page_title="LLM Analytics Assistant", layout="wide")

st.title("📊 LLM-Powered Analytics Assistant with RAG")

# ================== LOAD REVIEWS ==================
@st.cache_data
def load_reviews():
    conn = sqlite3.connect("olist.db")
    data = conn.execute("""
        SELECT review_comment_message 
        FROM order_reviews 
        WHERE review_comment_message IS NOT NULL 
        LIMIT 500
    """).fetchall()
    conn.close()
    return [row[0] for row in data]


# ================== QUERY TRANSLATION ==================
def translate_query(query):
    query = query.lower()

    if "shipping" in query or "delivery" in query:
        return "entrega atraso demora"
    if "product" in query:
        return "produto qualidade"
    if "cancel" in query:
        return "cancelamento"

    return query


# ================== SENTIMENT ==================
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

        if "erro" in text:
            issues.append("Wrong Product")

        if "cancelamento" in text:
            issues.append("Cancellation Issue")

    if pos > neg:
        sentiment = "Positive"
    elif neg > pos:
        sentiment = "Negative"
    else:
        sentiment = "Mixed"

    return sentiment, list(set(issues))


# ================== ROUTER ==================
def classify_query(query):
    query = query.lower()

    if "review" in query or "customer" in query or "complaint" in query:
        return "RAG"
    else:
        return "SQL"


# ================== UI ==================
query = st.text_input("🔍 Ask your question:")

if query:
    route = classify_query(query)
    st.info(f"🔀 Route Selected: {route}")

    # ================= SQL =================
    if route == "SQL":
        sql_query = generate_sql(query)
        df = run_sql(sql_query)
        explanation = explain_result(query, df)

        st.subheader("📌 SQL Query")
        st.code(sql_query)

        st.subheader("📊 Data")
        st.dataframe(df, use_container_width=True)

        st.subheader("🧠 Explanation")
        st.write(explanation)

        # 🔥 Chart
        if df.shape[1] >= 2 and df.shape[0] <= 20:
            try:
                fig = px.bar(df, x=df.columns[0], y=df.columns[1])
                st.subheader("📊 Visualization")
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.warning("Chart not supported")

    # ================= RAG =================
    else:
        reviews = load_reviews()
        vectorizer, vectors = create_embeddings(reviews)

        translated_query = translate_query(query)
        top_reviews = retrieve_reviews(translated_query, vectorizer, vectors, reviews)

        sentiment, issues = analyze_reviews(top_reviews)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📌 Top Relevant Reviews")
            for r in top_reviews:
                st.write("-", r)

        with col2:
            st.subheader("📊 Sentiment")

            if sentiment == "Positive":
                st.success("Positive 😊")
            elif sentiment == "Negative":
                st.error("Negative 😞")
            else:
                st.warning("Mixed 😐")

            st.subheader("⚠️ Top Issues")
            if issues:
                for issue in issues:
                    st.write("•", issue)
            else:
                st.write("No major issues")

        st.subheader("📌 Summary")
        st.write(f"Customers show **{sentiment} sentiment**.")
        if issues:
            st.write(f"Main issues: {', '.join(issues)}")
