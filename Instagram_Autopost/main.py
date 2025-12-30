import json
import os
from datetime import datetime
from instagrapi import Client
import instagrapi.extractors as extractors
import instagrapi.mixins.clip as clip_mixin
import config


_original_extract = extractors.extract_media_v1

def patched_extract_media_v1(media):
    clips = media.get("clips_metadata")
    if clips:
        original_sound = clips.get("original_sound_info")
        if original_sound and original_sound.get("audio_filter_infos") is None:
            original_sound["audio_filter_infos"] = []
    return _original_extract(media)

extractors.extract_media_v1 = patched_extract_media_v1
clip_mixin.extract_media_v1 = patched_extract_media_v1



BASE = "Instagram_Posts/Reels"
VIDEO_DIR = f"{BASE}/Video"
TEXT_DIR = f"{BASE}/Text"
POSTED_FILE = f"{BASE}/posted.json"

POST_TIMES = {"10:00", "13:00", "16:00", "18:00"}


def now_allowed():
    return datetime.now().strftime("%H:%M") in POST_TIMES


def load_posted():
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r") as f:
        return set(json.load(f))


def save_posted(posted):
    with open(POSTED_FILE, "w") as f:
        json.dump(sorted(posted), f, indent=2, ensure_ascii=False)


def get_next_reel(posted):
    videos = sorted(f for f in os.listdir(VIDEO_DIR) if f.endswith(".mp4"))

    for video in videos:
        if video in posted:
            continue

        text_path = os.path.join(TEXT_DIR, video.replace(".mp4", ".txt"))
        if os.path.exists(text_path):
            return video, text_path

    return None, None


def main():
    if not now_allowed():
        return

    posted = load_posted()
    video, text_path = get_next_reel(posted)

    if not video:
        print("Немає нового контенту")
        return

    with open(text_path, "r") as f:
        caption = f.read()

    client = Client()
    client.login(config.username, config.password)

    media = client.clip_upload(
        path=os.path.join(VIDEO_DIR, video),
        caption=caption
    )

    posted.add(video)
    save_posted(posted)

    print("Опубліковано:", video)
    print("https://www.instagram.com/reel/" + media.code)


if __name__ == "__main__":
    main()
