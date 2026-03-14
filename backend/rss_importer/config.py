import os
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

raw_database_url = os.getenv("DATABASE_URL", "")


def normalize_database_url_for_psycopg2(url: str) -> str:
    if not url:
        return url

    parsed = urlparse(url)
    query_params = parse_qsl(parsed.query, keep_blank_values=True)

    filtered_query = [(k, v) for k, v in query_params if k.lower() != "schema"]

    normalized = parsed._replace(query=urlencode(filtered_query))
    return urlunparse(normalized)


DATABASE_URL = normalize_database_url_for_psycopg2(raw_database_url)

IMPORT_JOB_NAME = "rss-import"
IMPORT_MIN_HOURS = int(os.getenv("RSS_IMPORT_MIN_HOURS", "84"))
TIMEZONE = os.getenv("RSS_TIMEZONE", "Europe/Amsterdam")
IMAGE_DIR = os.getenv("RSS_IMAGE_DIR", "public/images/articles")
USER_AGENT = os.getenv(
    "RSS_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

PG_ADVISORY_LOCK_KEY = int(os.getenv("RSS_PG_LOCK_KEY", "84512001"))
REQUEST_TIMEOUT = int(os.getenv("RSS_REQUEST_TIMEOUT", "25"))
DEFAULT_LIMIT_PER_FEED = int(os.getenv("RSS_LIMIT_PER_FEED", "10"))