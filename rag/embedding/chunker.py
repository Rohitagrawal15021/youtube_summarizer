import json
import re


# --------------------------------------------------
# Configuration
# --------------------------------------------------

MAX_CHUNK_WORDS = 500
MIN_CHUNK_WORDS = 80


# --------------------------------------------------
# Basic text cleaning
# --------------------------------------------------

def clean_text(text):
    """
    Clean unnecessary whitespace from text.
    """

    if not text:
        return ""

    text = str(text)

    # Replace multiple spaces/newlines
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# --------------------------------------------------
# Split a long section into semantic-ish chunks
# --------------------------------------------------

def split_long_text(text, max_words=MAX_CHUNK_WORDS):
    """
    Split long text using sentence boundaries.

    We don't blindly cut at a character position.
    We try to keep complete sentences together.
    """

    text = clean_text(text)

    if not text:
        return []

    words = text.split()

    # Section is already small enough
    if len(words) <= max_words:
        return [text]

    # Split into sentences
    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    chunks = []
    current_chunk = []
    current_words = 0

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        sentence_words = len(sentence.split())

        # If adding this sentence exceeds the limit
        if (
            current_words + sentence_words > max_words
            and current_chunk
        ):
            chunks.append(
                " ".join(current_chunk).strip()
            )

            current_chunk = []
            current_words = 0

        current_chunk.append(sentence)
        current_words += sentence_words

    # Add remaining text
    if current_chunk:
        chunks.append(
            " ".join(current_chunk).strip()
        )

    return chunks


# --------------------------------------------------
# Create RAG documents from one section
# --------------------------------------------------

def create_section_chunks(
    heading,
    content,
    note_id,
    title
):
    """
    Convert one detailed-note section into
    RAG-ready documents.
    """

    heading = clean_text(heading)
    content = clean_text(content)

    if not content:
        return []

    text_chunks = split_long_text(content)

    documents = []

    for index, chunk in enumerate(text_chunks):

        # Include heading inside the actual document.
        # This helps retrieval understand the context.
        document_text = (
            f"Topic: {heading}\n\n"
            f"{chunk}"
        )

        documents.append({
            "text": document_text,

            "metadata": {
                "note_id": str(note_id),
                "title": title,
                "section": heading,
                "chunk_index": index,
                "source_type": "section"
            }
        })

    return documents


# --------------------------------------------------
# Create RAG chunks from JSON
# --------------------------------------------------

def create_rag_chunks(
    json_file="json_txt.json",
    note_id="default_note"
):
    """
    Read detailed notes JSON and convert it into
    structure-aware RAG documents.
    Supports passing a file path or an already-parsed JSON dictionary.
    """

    if isinstance(json_file, dict):
        notes = json_file
    else:
        with open(
            json_file,
            "r",
            encoding="utf-8"
        ) as file:
            notes = json.load(file)

    title = notes.get(
        "title",
        "Untitled Lecture"
    )

    rag_documents = []

    # --------------------------------------------------
    # 1. Overview
    # --------------------------------------------------

    overview = clean_text(
        notes.get("overview", "")
    )

    if overview:

        rag_documents.append({
            "text": (
                f"Topic: Overview\n\n"
                f"{overview}"
            ),

            "metadata": {
                "note_id": str(note_id),
                "title": title,
                "section": "Overview",
                "chunk_index": 0,
                "source_type": "overview"
            }
        })

    # --------------------------------------------------
    # 2. Main sections
    # --------------------------------------------------

    sections = notes.get(
        "sections",
        []
    )

    for section in sections:

        heading = section.get(
            "heading",
            ""
        )

        content = section.get(
            "content",
            ""
        )

        section_chunks = create_section_chunks(
            heading=heading,
            content=content,
            note_id=note_id,
            title=title
        )

        rag_documents.extend(
            section_chunks
        )

    # --------------------------------------------------
    # 3. Definitions
    # --------------------------------------------------

    definitions = notes.get(
        "definitions",
        []
    )

    for index, definition in enumerate(definitions):

        term = clean_text(
            definition.get("term", "")
        )

        meaning = clean_text(
            definition.get("meaning", "")
        )

        if not term or not meaning:
            continue

        document_text = (
            f"Definition: {term}\n\n"
            f"{meaning}"
        )

        rag_documents.append({
            "text": document_text,

            "metadata": {
                "note_id": str(note_id),
                "title": title,
                "section": "Definitions",
                "term": term,
                "chunk_index": index,
                "source_type": "definition"
            }
        })

    # --------------------------------------------------
    # 4. Important terms
    # --------------------------------------------------

    important_terms = notes.get(
        "important_terms",
        []
    )

    if important_terms:

        terms_text = ", ".join(
            clean_text(term)
            for term in important_terms
            if term
        )

        if terms_text:

            rag_documents.append({
                "text": (
                    "Important Terms:\n\n"
                    + terms_text
                ),

                "metadata": {
                    "note_id": str(note_id),
                    "title": title,
                    "section": "Important Terms",
                    "chunk_index": 0,
                    "source_type": "important_terms"
                }
            })

    # --------------------------------------------------
    # 5. Key takeaways
    # --------------------------------------------------

    key_takeaways = notes.get(
        "key_takeaways",
        []
    )

    for index, takeaway in enumerate(
        key_takeaways
    ):

        takeaway = clean_text(takeaway)

        if not takeaway:
            continue

        rag_documents.append({
            "text": (
                "Key Takeaway:\n\n"
                + takeaway
            ),

            "metadata": {
                "note_id": str(note_id),
                "title": title,
                "section": "Key Takeaways",
                "chunk_index": index,
                "source_type": "key_takeaway"
            }
        })

    # --------------------------------------------------
    # 6. Exam tips
    # --------------------------------------------------

    exam_tips = notes.get(
        "exam_tips",
        []
    )

    for index, tip in enumerate(exam_tips):

        tip = clean_text(tip)

        if not tip:
            continue

        rag_documents.append({
            "text": (
                "Exam Tip:\n\n"
                + tip
            ),

            "metadata": {
                "note_id": str(note_id),
                "title": title,
                "section": "Exam Tips",
                "chunk_index": index,
                "source_type": "exam_tip"
            }
        })

    # --------------------------------------------------
    # 7. Final summary
    # --------------------------------------------------

    summary = clean_text(
        notes.get("summary", "")
    )

    if summary:

        rag_documents.append({
            "text": (
                "Lecture Summary:\n\n"
                + summary
            ),

            "metadata": {
                "note_id": str(note_id),
                "title": title,
                "section": "Summary",
                "chunk_index": 0,
                "source_type": "summary"
            }
        })

    return rag_documents


# --------------------------------------------------
# Testing
# --------------------------------------------------

if __name__ == "__main__":
    chunks = create_rag_chunks(
        json_file="json_txt.json",
        note_id="test_note_001"
    )
    print(f"\nTotal RAG documents: {len(chunks)}\n")

    # Generate embeddings for each chunk text
    from rag.embedding.embedder import create_embeddings
    texts = [chunk["text"] for chunk in chunks]
    embeddings = create_embeddings(texts)

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        print("=" * 70)
        print(f"Chunk {i + 1}")
        print("\nMetadata:")
        print(chunk["metadata"])
        print("\nText (first 500 chars):")
        print(chunk["text"][:500])
        print("\nEmbedding (first 5 values):")
        print(embedding[:5])
        print()