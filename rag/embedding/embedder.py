from sentence_transformers import SentenceTransformer

# Multilingual embedding model (supports English, Hindi, and 50+ languages)
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

model = SentenceTransformer(MODEL_NAME)


def create_embedding(text):
    """
    Convert a single piece of text into an embedding vector.
    """
    embedding = model.encode(
        text,
        normalize_embeddings=True
    )
    return embedding.tolist()


def create_embeddings(texts):
    """
    Convert multiple texts into embedding vectors.
    """
    embeddings = model.encode(
        texts,
        normalize_embeddings=True
    )
    return embeddings.tolist()


if __name__ == "__main__":

    text = "Gradient descent is an optimization algorithm."

    vector = create_embedding(text)

    print("Vector type:", type(vector))
    print("Vector length:", len(vector))
    print("First 10 values:", vector[:10])