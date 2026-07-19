from config import client
from google.genai import types

# checking for the study content--- we make a function 
def is_study_content(transcript_text):
    sample = transcript_text[:2000] # we are taking only sample of 2000 character it is enoght to say it is educational content or not 
    prompt = f"""You are a content classifier for an educational notes app.
Determine if the following video transcript excerpt is STUDY/EDUCATIONAL content —
this includes lectures, tutorials, courses, explanations of academic or technical
concepts, skill-building content, or exam preparation material.

It is NOT study content if it's entertainment, music, vlogs, gaming, comedy,
news/commentary, or general lifestyle content.

The transcript may be in any language — read and judge it regardless of language.

Respond with ONLY one word, in English: YES or NO.

Transcript excerpt:
{sample}
"""
    
# response from the llm ---
    response = client.models.generate_content(
       model="gemini-3.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=5
        )
    )   
    answer = response.text.strip().upper()
    return answer.startswith("YES")


if __name__ == "__main__":
    from get_transcript import get_transcript
    url = input("Paste youtube url")
    transcript = get_transcript(url)
    if is_study_content(transcript):
        print(" ✅ Study content detected — would proceed to summarize.")
    else:
        print("❌ Only study/educational videos are supported. This video was not accepted.")    