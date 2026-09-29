"""Persistent Chroma storage for video chunks and their embeddings."""

from pathlib import Path
from typing import Any, Optional, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHROMA_PATH = PROJECT_ROOT / "data" / "chroma"
COLLECTION_NAME = "youtube_video_chunks"

_client = None
_collection = None


def get_collection():
    """Return the local persistent collection, creating it when needed."""
    global _client, _collection

    if _collection is None:
        import chromadb

        _client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=None,
            configuration={"hnsw": {"space": "cosine"}},
        )

    return _collection


def check_chroma(video_id: Optional[str] = None) -> dict[str, Any]:
    """Check that Chroma opens and report whether chunks are indexed.

    With ``video_id``, ``ready_for_retrieval`` means that video has chunks.
    Without it, that field means at least one chunk exists in the collection.
    """
    video_id = str(video_id).strip() if video_id is not None else None
    if video_id == "":
        video_id = None

    try:
        collection = get_collection()
        total_chunks = int(collection.count())
        video_chunks = None

        if video_id is not None:
            stored = collection.get(
                where={"video_id": video_id},
                include=["metadatas"],
            )
            video_chunks = len(stored["ids"])

        ready = video_chunks > 0 if video_chunks is not None else total_chunks > 0
        if video_id is not None:
            message = (
                f"Video {video_id} has {video_chunks} indexed chunks."
                if ready
                else f"Video {video_id} has no indexed chunks yet."
            )
        else:
            message = (
                f"Chroma is connected and has {total_chunks} indexed chunks."
                if ready
                else "Chroma is connected, but the collection has no indexed chunks yet."
            )

        return {
            "ok": True,
            "installed": True,
            "connected": True,
            "ready_for_retrieval": ready,
            "database_path": str(CHROMA_PATH),
            "collection": COLLECTION_NAME,
            "total_chunks": total_chunks,
            "video_id": video_id,
            "video_chunks": video_chunks,
            "message": message,
        }
    except ModuleNotFoundError as exc:
        if exc.name == "chromadb":
            return {
                "ok": False,
                "installed": False,
                "connected": False,
                "ready_for_retrieval": False,
                "database_path": str(CHROMA_PATH),
                "collection": COLLECTION_NAME,
                "message": "chromadb is not installed. Run: python -m pip install chromadb",
            }
        return {
            "ok": False,
            "installed": True,
            "connected": False,
            "ready_for_retrieval": False,
            "database_path": str(CHROMA_PATH),
            "collection": COLLECTION_NAME,
            "message": f"A required Python module is missing: {exc.name}",
        }
    except Exception as exc:
        return {
            "ok": False,
            "installed": True,
            "connected": False,
            "ready_for_retrieval": False,
            "database_path": str(CHROMA_PATH),
            "collection": COLLECTION_NAME,
            "message": f"Could not open or query Chroma: {exc}",
        }


def _chroma_metadata(chunk: dict[str, Any], video_id: str) -> dict[str, Any]:
    """Keep Chroma metadata to supported scalar values and add video scope."""
    metadata = chunk.get("metadata") or {}
    result = {
        key: value
        for key, value in metadata.items()
        if isinstance(value, (str, int, float, bool))
    }
    result["video_id"] = video_id
    return result


def index_video_chunks(
    video_id: str,
    chunks: Sequence[dict[str, Any]],
    embeddings: Sequence[Sequence[float]],
) -> int:
    """Persist precomputed chunk vectors under one YouTube video ID.

    ``embeddings`` must line up with ``chunks`` and come from the project's
    SentenceTransformer embedder. Reindexing the same video updates its chunk
    records and removes any old trailing chunks.
    """
    video_id = str(video_id or "").strip()
    if not video_id:
        raise ValueError("video_id must not be empty")
    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings must have equal lengths")
    if not chunks:
        return 0

    ids = [f"{video_id}:{index}" for index in range(len(chunks))]
    documents = []
    metadatas = []
    for chunk in chunks:
        text = str(chunk.get("text", "")).strip()
        if not text:
            raise ValueError("every indexed chunk must contain non-empty text")
        documents.append(text)
        metadatas.append(_chroma_metadata(chunk, video_id))

    collection = get_collection()

    # Upsert stable IDs so re-indexing a video updates existing records.
    collection.upsert(
        ids=ids,
        embeddings=[list(vector) for vector in embeddings],
        documents=documents,
        metadatas=metadatas,
    )

    # Remove records left over if the regenerated video has fewer chunks.
    existing = collection.get(
        where={"video_id": video_id},
        include=["metadatas"],
    )
    current_ids = set(ids)
    stale_ids = [record_id for record_id in existing["ids"] if record_id not in current_ids]
    if stale_ids:
        collection.delete(ids=stale_ids)

    return len(ids)


def query_video_chunks(
    query: str,
    video_id: str,
    top_k: int = 5,
    min_similarity: Optional[float] = None,
) -> list[dict[str, Any]]:
    """Find the closest chunks for a question, limited to one video."""
    query = (query or "").strip()
    video_id = str(video_id or "").strip()

    if not query:
        raise ValueError("query must not be empty")
    if not video_id:
        raise ValueError("video_id must not be empty")
    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    # Use exactly the same embedder as the one used to index the chunks.
    from rag.embedding.embedder import create_embedding

    result = get_collection().query(
        query_embeddings=[create_embedding(query)],
        n_results=top_k,
        where={"video_id": video_id},
        include=["documents", "metadatas", "distances"],
    )

    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]

    matches = []
    for text, metadata, distance in zip(documents, metadatas, distances):
        # With Chroma's cosine space, distance = 1 - cosine similarity.
        similarity = 1.0 - float(distance)
        if min_similarity is not None and similarity < min_similarity:
            continue

        matches.append({
            "text": text,
            "metadata": metadata or {},
            "similarity": similarity,
        })

    return matches


if __name__ == "__main__":
    import json

    print(json.dumps(check_chroma(), indent=2))
