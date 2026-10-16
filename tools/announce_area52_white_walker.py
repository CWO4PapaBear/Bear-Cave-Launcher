from pathlib import Path
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen
import argparse
import hashlib
import json
import os
import re
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tools")]
from launcher import updater

NOTES = ROOT / "docs/AREA52-2026-10-15-WHITE-WALKER.md"
IMAGE = ROOT / "docs/images/AREA52-2026-10-15-PROGRESS.png"
RECEIPT = ROOT / "discord-white-walker-receipt.json"
EXPECTED_PATCH = "041412788a8ee1f0425e5931a1b0a991789f7e197c15f2aa5b2eeeb248bf873c"
EXPECTED_SERVER = "4e5fd0b79237b1b2fcedc7e8e7c189d8140c45ac1dac237a19ef3a7c71a435d0"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def has_image(message):
    if any(item.get("filename") == IMAGE.name for item in message.get("attachments", [])):
        return True
    return any(
        unquote(urlsplit(item.get("image", {}).get("url", "")).path).rsplit("/", 1)[-1] == IMAGE.name
        for item in message.get("embeds", [])
    )


def message_url(message):
    if message.get("guild_id") and message.get("channel_id") and message.get("id"):
        return f'https://discord.com/channels/{message["guild_id"]}/{message["channel_id"]}/{message["id"]}'
    return None


def payload():
    notes = NOTES.read_text(encoding="utf-8-sig").split("\n![Making Progress]", 1)[0].strip()
    if len(notes) >= 3900 or not IMAGE.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError("Patch notes or image failed local validation")
    return {
        "username": "The Bear Cave - Updates",
        "content": "<@&1551989024833667072> **Area 52 White Walker is live. Close Ascension, reopen the launcher, and press Play to update before testing.**",
        "allowed_mentions": {"parse": [], "roles": ["1551989024833667072"]},
        "attachments": [{
            "id": 0,
            "filename": IMAGE.name,
            "description": "Area 52 verification and certification progress by category, including totals and percentages.",
        }],
        "embeds": [{
            "title": "Area 52 — White Walker Verification",
            "description": notes,
            "color": 0xD5A546,
            "url": "https://github.com/CWO4PapaBear/Bear-Cave-Launcher/blob/main/docs/AREA52-2026-10-15-WHITE-WALKER.md",
            "image": {"url": "attachment://" + IMAGE.name},
        }],
    }


def webhook():
    value = os.environ.get("DISCORD_PATCH_NOTES_WEBHOOK", "").strip()
    if not re.fullmatch(r"https://discord\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+", value):
        raise RuntimeError("Patch notes webhook unavailable")
    return value


def verify_public_release():
    manifest = updater.latest("area52")
    records = {row["path"]: row["sha256"] for row in manifest["baseline"]}
    if records.get("Data/area-52/patch-D.MPQ") != EXPECTED_PATCH or manifest.get("server_build") != EXPECTED_SERVER:
        raise RuntimeError("Matching White Walker client/server release is not publicly promoted")


def read_message(url, message_id):
    request = Request(url + "/messages/" + message_id, headers={"User-Agent": "BearCavePublisher/1.0"})
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verify-message")
    args = parser.parse_args()
    data = payload()
    if args.dry_run:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    verify_public_release()
    url = webhook()
    if args.verify_message:
        if not re.fullmatch(r"[0-9]+", args.verify_message):
            raise RuntimeError("Invalid message ID")
        message = read_message(url, args.verify_message)
        if message.get("id") != args.verify_message or not has_image(message):
            raise RuntimeError("Discord readback did not contain the expected message and image")
        print(json.dumps({"message_id": message["id"], "url": message_url(message), "verified": True}))
        return
    if RECEIPT.exists():
        raise RuntimeError("A Discord receipt already exists; verify it rather than posting again")
    boundary = "BearCave" + uuid.uuid4().hex
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"payload_json\"\r\nContent-Type: application/json\r\n\r\n".encode()
        + json.dumps(data).encode()
        + f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"files[0]\"; filename=\"{IMAGE.name}\"\r\nContent-Type: image/png\r\n\r\n".encode()
        + IMAGE.read_bytes()
        + f"\r\n--{boundary}--\r\n".encode()
    )
    request = Request(
        url + "?wait=true",
        data=body,
        headers={"Content-Type": "multipart/form-data; boundary=" + boundary, "User-Agent": "BearCavePublisher/1.0"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            message = json.loads(response.read())
    except Exception as exc:
        raise RuntimeError("Discord delivery unconfirmed; inspect the channel before retrying") from exc
    if not message.get("id") or not has_image(message):
        raise RuntimeError("Discord response did not confirm the expected message and image")
    confirmed = read_message(url, message["id"])
    if confirmed.get("id") != message["id"] or not has_image(confirmed):
        raise RuntimeError("Discord readback failed after delivery")
    receipt = {
        "message_id": message["id"],
        "channel_id": message.get("channel_id"),
        "guild_id": message.get("guild_id"),
        "url": message_url(message),
        "notes_sha256": sha(NOTES),
        "image_sha256": sha(IMAGE),
        "package_id": "white-walker-tooltip-correction-20261015",
        "readback_verified": True,
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
