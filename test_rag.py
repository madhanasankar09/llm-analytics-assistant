import sqlite3
from rag.embedder import create_embeddings
from rag.retriever import retrieve_reviews


# 🔹 Load reviews from SQLite
def load_reviews():
    conn = sqlite3.connect("olist.db")

    query = """
    SELECT review_comment_message 
    FROM order_reviews 
    WHERE review_comment_message IS NOT NULL
    LIMIT 500
    """

    df = conn.execute(query).fetchall()
    conn.close()

    return [row[0] for row in df]


# 🔹 Simple Sentiment + Theme detection
def analyze_reviews(reviews):
    positive_words = ["good", "excellent", "fast", "great", "love",
                      "bom", "excelente", "ótimo"]

    negative_words = ["bad", "late", "delay", "poor", "broken", "worst",
                      "ruim", "atraso", "demora", "erro", "problema"]

    pos, neg = 0, 0
    issues = []

    for review in reviews:
        text = review.lower()

        # Sentiment scoring
        for word in positive_words:
            if word in text:
                pos += 1

        for word in negative_words:
            if word in text:
                neg += 1

        # Issue detection
        if "atraso" in text or "demora" in text:
            issues.append("Delivery Delay")

        if "erro" in text or "errada" in text:
            issues.append("Wrong Product Description")

        if "cancelamento" in text:
            issues.append("Cancellation Issue")

    # Improved sentiment logic
    if neg > pos:
        sentiment = "Negative"
    elif pos > neg:
        sentiment = "Positive"
    else:
        sentiment = "Mixed"

    return sentiment, list(set(issues))


# 🔹 MAIN FLOW
if __name__ == "__main__":

    print("🔄 Loading reviews...")
    reviews = load_reviews()

    print("🔄 Creating embeddings...")
    vectorizer, vectors = create_embeddings(reviews)

    # Sample query
    query = "Why are customers unhappy?"

    print("\n🔍 Query:", query)

    top_reviews = retrieve_reviews(query, vectorizer, vectors, reviews)

    print("\n📌 Top Relevant Reviews:")
    for r in top_reviews:
        print("-", r)

    sentiment, issues = analyze_reviews(top_reviews)

    print("\n📊 Sentiment:", sentiment)
    print("⚠️ Top Issues:", issues)