import datetime
import os
import random
import subprocess

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
README = "README.MD"
ITEMS_PER_TYPE = 3


def fetch_random_items(media_type, count=ITEMS_PER_TYPE):
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


def append_under_heading(date_heading, sub_heading, line):
    with open(README, "r") as f:
        lines = f.read().splitlines()

    date_idx = lines.index(date_heading)
    sub_idx = lines.index(sub_heading, date_idx + 1)
    insert_idx = sub_idx + 1
    while insert_idx < len(lines) and not lines[insert_idx].startswith("#"):
        insert_idx += 1

    lines.insert(insert_idx, line)

    with open(README, "w") as f:
        f.write("\n".join(lines) + "\n")


def ensure_date_section(date_heading):
    with open(README, "r") as f:
        content = f.read()

    if date_heading in content:
        return False

    content = content.rstrip() + f"\n\n{date_heading}\n\n### Movies\n\n### TV Shows\n"

    with open(README, "w") as f:
        f.write(content)
    return True


def commit(message):
    subprocess.run(["git", "add", README], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)


def add_and_commit_item(item, media_type, date_heading, sub_heading):
    label = "movie" if media_type == "movie" else "TV show"
    line = format_entry(item, media_type)

    append_under_heading(date_heading, sub_heading, line)
    commit(f"Add {label}: {line[2:]}")
    print(f"Committed: {line}")


def main():
    today = datetime.date.today().isoformat()
    date_heading = f"## {today}"

    if ensure_date_section(date_heading):
        commit(f"Add {today} section to README")

    for item in fetch_random_items("movie"):
        add_and_commit_item(item, "movie", date_heading, "### Movies")

    for item in fetch_random_items("tv"):
        add_and_commit_item(item, "tv", date_heading, "### TV Shows")


if __name__ == "__main__":
    main()
