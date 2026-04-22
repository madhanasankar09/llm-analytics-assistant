from sklearn.feature_extraction.text import TfidfVectorizer


def create_embeddings(texts):
    """
    Convert text data into vector form
    """
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform(texts)

    return vectorizer, vectors