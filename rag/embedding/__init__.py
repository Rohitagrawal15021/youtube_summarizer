__all__ = ["create_embedding", "create_embeddings"]


def __getattr__(name):
    if name in ("create_embedding", "create_embeddings"):
        from rag.embedding.embedder import create_embedding, create_embeddings
        globals()["create_embedding"] = create_embedding
        globals()["create_embeddings"] = create_embeddings
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
