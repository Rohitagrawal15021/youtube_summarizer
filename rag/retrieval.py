"""Question-to-chunk retrieval backed by the persistent Chroma store."""

from typing import Any, Optional

from rag.vector_store import query_video_chunks


def retrieve_relevant_chunks(
    query: str,
    video_id: str,
    top_k: int = 5,
    min_similarity: Optional[float] = None,
) -> list[dict[str, Any]]:
    """Return the most relevant indexed chunks for one video's question."""
    return query_video_chunks(
        query=query,
        video_id=video_id,
        top_k=top_k,
        min_similarity=min_similarity,
    )
