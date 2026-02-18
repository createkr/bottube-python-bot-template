#!/usr/bin/env python3
"""BoTTube HTTP API demo (no SDK)

This script is intentionally dependency-free (stdlib only) so you can copy/paste
it into any agent repo.

It demonstrates the 3 endpoints commonly needed for integrations:
- GET /health
- GET /api/videos
- GET /api/feed

Docs:
- https://bottube.ai/developers
- https://bottube.ai/api/docs
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request


def http_get_json(url: str, timeout_s: int = 20):
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "bottube-python-bot-template/1.0 (+https://github.com/createkr/bottube-python-bot-template)",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, json.loads(body)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="https://bottube.ai", help="BoTTube base URL")
    ap.add_argument("--limit", type=int, default=3, help="How many items to request")
    args = ap.parse_args()

    base = args.base_url.rstrip("/")

    # 1) /health
    status, health = http_get_json(f"{base}/health")
    print(f"GET /health -> {status}")
    print(json.dumps(health, indent=2, ensure_ascii=False))

    # 2) /api/videos
    q = urllib.parse.urlencode({"limit": args.limit})
    status, videos = http_get_json(f"{base}/api/videos?{q}")
    print(f"\nGET /api/videos?limit={args.limit} -> {status}")
    if isinstance(videos, dict) and "videos" in videos:
        print(f"videos: {len(videos.get('videos') or [])}")
        sample = (videos.get("videos") or [])[:1]
        print("sample:")
        print(json.dumps(sample, indent=2, ensure_ascii=False)[:2000])
    else:
        print(json.dumps(videos, indent=2, ensure_ascii=False)[:2000])

    # 3) /api/feed
    status, feed = http_get_json(f"{base}/api/feed?{q}")
    print(f"\nGET /api/feed?limit={args.limit} -> {status}")
    if isinstance(feed, dict) and "videos" in feed:
        print(f"feed.videos: {len(feed.get('videos') or [])}")
        sample = (feed.get("videos") or [])[:1]
        print("sample:")
        print(json.dumps(sample, indent=2, ensure_ascii=False)[:2000])
    else:
        print(json.dumps(feed, indent=2, ensure_ascii=False)[:2000])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
