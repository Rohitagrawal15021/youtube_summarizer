from langdetect import detect
import json
from pipeline.get_transcript import get_transcript
from pipeline.classify_content import is_study_content
from pipeline.translate import translate_chunks
from pipeline.clean_transcript import clean_transcript
from pipeline.chunking import chunk_text
# from summary import summarize_chunks
# from summary import final_summary
# from json_summary import change_to_json
from detailed_notes import detail_notes_chunks
from detailed_notes import final_detailed_notes
from pipeline.detailed_notes_json import detailed_notes_json


if __name__ == "__main__":

    # Step 1: Get YouTube URL
    url = input("Paste YouTube URL: ")

    # Step 2: Extract transcript
    transcript = get_transcript(url)

    # Step 3: Check whether the video is educational
    if not is_study_content(transcript):
        print("❌ This is not an educational video.")
        exit()

    # Step 4: Detect language only once
    language = detect(transcript)

    # Step 5: Clean transcript
    cleaned = clean_transcript(transcript)

    print("\n------ CLEANED TRANSCRIPT ------\n")
    print(cleaned[:500])

    # Step 6: Chunk the cleaned transcript
    chunks = chunk_text(cleaned)

    print(f"\nTotal Chunks: {len(chunks)}")

    # Step 7: Translate only if required
    if language == "en":
        print("\n✅ Transcript is already in English. Skipping translation.")
        translated_chunks = chunks
    else:
        print("\n🌍 Translating transcript...")
        translated_chunks = translate_chunks(chunks)

    # Step 8: Display translated chunks
    print("\n------ TRANSLATED CHUNKS ------")

    for i, chunk in enumerate(translated_chunks, start=1):
        print(f"\nChunk {i}")
        print("-" * 50)
        print(chunk[:30])

    # Step 9: Summarizing the chunks and adding into a final summary
    # chunk_summaries = summarize_chunks(translated_chunks)

    # combined_summary = "\n\n".join(chunk_summaries)

    # final_notes = final_summary(combined_summary)

    # print(final_notes)

    # Step 10: Generating detailed notes for each chunk
    detailed_notes_list = detail_notes_chunks(translated_chunks)
    Combined_detailed_notes = "\n\n".join(detailed_notes_list)
    final_notes = final_detailed_notes(Combined_detailed_notes)

    print("\n========== FINAL NOTES DEBUG ==========")
    print("Type:", type(final_notes))

    if final_notes:
        print("Length:", len(final_notes))
        print(final_notes[:1000])
    else:
        print("final_notes is EMPTY!")

    # changing the normal text file into the json format
    json_txt = detailed_notes_json(final_notes)
    if json_txt:
        print("\n✅ Detailed Notes JSON Generated Successfully.")

    with open("json_txt.json", "w", encoding="utf-8") as file:
        json.dump(json_txt, file, indent=4, ensure_ascii=False)

    print("✅ notes.json saved successfully.")
else:
        print("❌ Failed to generate notes JSON.")