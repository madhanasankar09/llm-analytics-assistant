from sklearn.metrics.pairwise import cosine_similarity


def retrieve_reviews(query, vectorizer, vectors, texts, top_k=5):
    """
    Retrieve top similar reviews based on query
    """
    query_vec = vectorizer.transform([query])

    similarities = cosine_similarity(query_vec, vectors).flatten()

    top_indices = similarities.argsort()[-top_k:][::-1]

    return [texts[i] for i in top_indices]