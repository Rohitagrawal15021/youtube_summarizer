from get_transcript import get_transcript
from classify_content import is_study_content
from translate import translate_into_english
from clean_transcript import clean_transcript

if __name__ == "__main__":
    url = input("paste url : ")
    transcript = get_transcript(url)
    if not is_study_content(transcript):
        print("It is noa s stude conten\n")
        exit()
    final_con = translate_into_english(transcript)
    cleaned = clean_transcript(final_con)

print("\n------ CLEANED TRANSCRIPT ------\n")
print(cleaned[:1000])