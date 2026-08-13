import os
import random
import subprocess

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
README = "README.MD"


def fetch_random_items(media_type, count=5):
    """Pull `count` unique random items from TMDB's popular list for the given media_type ('movie' or 'tv')."""
    pool = {}
    while len(pool) < count:
        page = random.randint(1, 20)
        resp = requests.get(
            f"{BASE_URL}/{media_type}/popular",
            params={"api_key": API_KEY, "page": page},
        )
        resp.raise_for_status()
        for item in resp.json().get("results", []):
            pool[item["id"]] = item

    return random.sample(list(pool.values()), count)


def format_entry(item, media_type):
    title = item["title"] if media_type == "movie" else item["name"]
    date = item.get("release_date") if media_type == "movie" else item.get("first_air_date")
    year = date[:4] if date else "N/A"
    return f"- {title} ({year})"


def append_under_heading(heading, line):
    with open(README, "r") as f:
        lines = f.read().splitlines()

    heading_idx = lines.index(heading)
    insert_idx = heading_idx + 1
    while insert_idx < len(lines) and not lines[insert_idx].startswith("## "):
        insert_idx += 1

    lines.insert(insert_idx, line)

    with open(README, "w") as f:
        f.write("\n".join(lines) + "\n")


def ensure_headings():
    with open(README, "r") as f:
        content = f.read()

    original = content
    if "## Movies" not in content:
        content = content.rstrip() + "\n\n## Movies\n"
    if "## TV Shows" not in content:
        content = content.rstrip() + "\n\n## TV Shows\n"

    if content == original:
        return False

    with open(README, "w") as f:
        f.write(content)
    return True


def commit(message):
    subprocess.run(["git", "add", README], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)


def add_and_commit_item(item, media_type):
    heading = "## Movies" if media_type == "movie" else "## TV Shows"
    label = "movie" if media_type == "movie" else "TV show"
    line = format_entry(item, media_type)

    append_under_heading(heading, line)
    commit(f"Add {label}: {line[2:]}")
    print(f"Committed: {line}")


def main():
    if ensure_headings():
        commit("Add Movies and TV Shows sections to README")

    for item in fetch_random_items("movie", 5):
        add_and_commit_item(item, "movie")

    for item in fetch_random_items("tv", 5):
        add_and_commit_item(item, "tv")


if __name__ == "__main__":
    main()
