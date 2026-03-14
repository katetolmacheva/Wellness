import argparse
import traceback

from .feeds import FEEDS
from .parser import fetch_feed, parse_generic_article
from .db import (
    get_connection,
    acquire_lock,
    release_lock,
    should_run,
    create_import_run,
    finish_import_run,
    upsert_article,
)
from .config import DEFAULT_LIMIT_PER_FEED


def import_all(conn, limit: int) -> tuple[int, int]:
    ok_count = 0
    fail_count = 0

    enabled_feeds = [f for f in FEEDS if f.get("enabled", True)]

    for feed in enabled_feeds:
        print(f"\n=== importing: {feed['title']} ===")
        parsed = fetch_feed(feed["rss_url"])
        entries = parsed.entries[:limit]

        for entry in entries:
            try:
                article = parse_generic_article(entry, feed)
                if not article:
                    continue

                upsert_article(conn, article)
                ok_count += 1
                print("✔", article["title"])
            except Exception as e:
                fail_count += 1
                print("✖", getattr(entry, "title", getattr(entry, "link", "unknown")), "-", str(e))

    return ok_count, fail_count


def run(conn, force: bool, trigger: str, limit: int):
    if not acquire_lock(conn):
        print("RSS import skipped: another import is already running")
        return

    run_id = None
    try:
        if not force:
            allowed, reason = should_run(conn)
            if not allowed:
                print(f"RSS import skipped: {reason}")
                return
            print(f"RSS import allowed: {reason}")
        else:
            print("RSS import forced")

        run_id = create_import_run(conn, trigger)

        ok_count, fail_count = import_all(conn, limit)
        message = f"success={ok_count}, failed={fail_count}"
        finish_import_run(conn, run_id, "success", message)
        print(message)

    except Exception as e:
        if run_id:
            finish_import_run(conn, run_id, "failed", str(e))
        traceback.print_exc()
        raise
    finally:
        release_lock(conn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--trigger", default="manual")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT_PER_FEED)
    args = parser.parse_args()

    conn = get_connection()
    try:
        run(conn, force=args.force, trigger=args.trigger, limit=args.limit)
    finally:
        conn.close()