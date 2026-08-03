from config import client
from google.genai import types


def detailed_notes_chunk(chunk):
    """
    Generates detailed notes for one chunk (or a group of chunks).
    """

    prompt = f"""
You are an expert educator and professional study note writer.

Your task is to convert the following educational lecture transcript into comprehensive study notes.

The goal is NOT to summarize aggressively.

The goal is to rewrite the lecture into clean, structured, easy-to-study notes while preserving all important educational content.

Instructions:

1. Preserve every important concept explained by the instructor.
2. Remove greetings, filler words, jokes and repeated sentences.
3. Keep the original order of topics.
4. Rewrite explanations in simple and professional English.
5. Explain concepts clearly but DO NOT invent new information.
6. Keep all technical terms exactly as used.
7. Preserve important formulas, equations and algorithms.
8. Preserve important code snippets.
9. Preserve examples used by the instructor.
10. Use headings and subheadings.
11. Use bullet points wherever appropriate.
12. Highlight important facts.
13. Mention common mistakes if discussed.
14. Make the notes suitable for self-study.
15. Do NOT shorten the lecture unnecessarily.
16. Return only the study notes.

Lecture Transcript:

{chunk}
"""
    try:
        response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2
        )
    )

        return response.text.strip() if response.text else ""

    except Exception as e:
        print(f"Error generating notes: {e}")
        return ""


def detail_notes_chunks(chunks):
    """
    Summarizes transcript chunks in groups of 4.
    """

    detailed_notes_list = []

    group_size = 4

    for i in range(0, len(chunks), group_size):

        # Take 4 chunks at a time
        group = chunks[i:i + group_size]

        # Combine them into one string
        combined_group = "\n\n".join(group)

        print(
    f"Generating notes for group {(i//group_size)+1}/{(len(chunks)-1)//group_size+1}"
)

        notes = detailed_notes_chunk(combined_group)

        detailed_notes_list.append(notes)

    return detailed_notes_list

def final_detailed_notes(combined_chunk):
    """
    Generates final detailed notes for the entire transcript.
    """

    print("Generating final detailed notes...")
    prompt = f"""
You are an expert technical educator.

The following text contains study notes generated from different chunks of the SAME lecture.

Your task is to merge them into one complete lecture note.

Instructions:

1. Merge all notes into one document.
2. Preserve every important concept.
3. Remove duplicate explanations.
4. Maintain the chronological order of topics.
5. Improve transitions between sections.
6. Keep headings and subheadings.
7. Keep definitions, examples, formulas and code.
8. Use bullet points whenever helpful.
9. Make the notes easy to study.
10. Do NOT summarize further.
11. Do NOT remove educational content.
12. Return only the final lecture notes.
13. Format the output using Markdown.

Lecture Notes:

{combined_chunk}
"""
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2
        )
    )
    return response.text.strip()
