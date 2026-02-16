#!/usr/bin/env python3
import argparse
import json
import os
import time
from pathlib import Path

import schedule
from bottube import BoTTubeClient
from dotenv import load_dotenv


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def parse_tags(raw: str):
    return [x.strip() for x in raw.split(",") if x.strip()]


def load_personality(path: str, name: str):
    if not path or not name:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    return data.get(name, {})


def build_client() -> BoTTubeClient:
    api_key = env("BOTTUBE_API_KEY")
    if not api_key:
        raise SystemExit("BOTTUBE_API_KEY is required")
    return BoTTubeClient(api_key=api_key)


def ensure_agent(client: BoTTubeClient):
    agent_name = env("AGENT_NAME")
    if not agent_name:
        raise SystemExit("AGENT_NAME is required")

    profile = load_personality(env("PERSONALITIES_FILE", "personalities.json"), env("PERSONALITY", ""))
    display_name = env("DISPLAY_NAME") or profile.get("display_name") or agent_name
    bio = env("BIO") or profile.get("bio") or "BoTTube Python bot"

    try:
        me = client.whoami()
        print(f"whoami ok: {me}")
    except Exception:
        # If credentials are valid but not registered as an agent yet
        reg = client.register(agent_name=agent_name, display_name=display_name, bio=bio)
        print(f"registered agent: {reg}")


def upload_video(client: BoTTubeClient):
    video_path = env("VIDEO_PATH")
    if not video_path:
        print("VIDEO_PATH empty, skip upload")
        return None
    if not Path(video_path).exists():
        print(f"VIDEO_PATH not found: {video_path}, skip upload")
        return None

    title = env("VIDEO_TITLE", "Automated BoTTube post")
    description = env("VIDEO_DESCRIPTION", "Posted by BoTTube Python template")
    tags = parse_tags(env("VIDEO_TAGS", "bot,python"))
    result = client.upload(video_path=video_path, title=title, description=description, tags=tags)
    print(f"upload result: {result}")

    # Try common keys returned by API
    for key in ("id", "video_id", "videoId"):
        if isinstance(result, dict) and result.get(key):
            return str(result[key])
    return None


def engage(client: BoTTubeClient, video_id: str | None):
    target_video_id = env("TARGET_VIDEO_ID") or video_id
    if not target_video_id:
        print("No target video id for comment/vote; skip")
        return

    profile = load_personality(env("PERSONALITIES_FILE", "personalities.json"), env("PERSONALITY", ""))
    comment_text = env("COMMENT_TEXT") or profile.get("comment_text")
    if comment_text:
        try:
            r = client.comment(video_id=target_video_id, content=comment_text)
            print(f"comment result: {r}")
        except Exception as e:
            print(f"comment failed: {e}")

    action = env("VOTE_ACTION", "none").lower()
    try:
        if action == "like":
            print(f"like result: {client.like(target_video_id)}")
        elif action == "dislike":
            print(f"dislike result: {client.dislike(target_video_id)}")
        else:
            print("VOTE_ACTION=none, skip vote")
    except Exception as e:
        print(f"vote failed: {e}")


def run_once():
    client = build_client()
    ensure_agent(client)
    video_id = upload_video(client)
    engage(client, video_id)


def run_loop():
    every_hours = int(env("POST_EVERY_HOURS", "6") or "6")
    print(f"schedule: every {every_hours}h")
    schedule.every(every_hours).hours.do(run_once)

    # Kick one immediate run first
    run_once()

    while True:
        schedule.run_pending()
        time.sleep(10)


if __name__ == "__main__":
    load_dotenv()
    ap = argparse.ArgumentParser(description="BoTTube Python bot template")
    ap.add_argument("--once", action="store_true", help="Run one cycle then exit")
    args = ap.parse_args()

    if args.once:
        run_once()
    else:
        run_loop()
