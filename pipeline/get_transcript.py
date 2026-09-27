from youtube_transcript_api import YouTubeTranscriptApi

def get_video_id(url):
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    elif "v=" in url:
        return url.split("v=")[1].split("&")[0]
    else:
        raise ValueError("Couldn't parse video ID from URL")

def get_transcript(url):
    video_id = get_video_id(url)
    ytt_api = YouTubeTranscriptApi()
    
    try:
        fetched_transcript = ytt_api.fetch(video_id, languages=['en'])
    except Exception:
        # fallback: get whatever language IS available
        transcript_list = ytt_api.list(video_id)
        first_available = next(iter(transcript_list))
        fetched_transcript = first_available.fetch()
    
    full_text = " ".join([snippet.text for snippet in fetched_transcript])
    return full_text

if __name__ == "__main__":
    url = input("Paste a YouTube URL: ")
    try:
        text = get_transcript(url)
        print(f"\nTranscript length: {len(text)} characters\n")
        print(text[:1500] + "...")
    except Exception as e:
        print(f"Error: {e}")