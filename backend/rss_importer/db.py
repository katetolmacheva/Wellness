import json
from datetime import datetime, timezone
from typing import Optional

import psycopg2
from psycopg2.extras import Json, RealDictCursor

from .config import DATABASE_URL, IMPORT_JOB_NAME, IMPORT_MIN_HOURS, PG_ADVISORY_LOCK_KEY


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def utc_now():
    return datetime.now(timezone.utc)


def acquire_lock(conn) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT pg_try_advisory_lock(%s);", (PG_ADVISORY_LOCK_KEY,))
        row = cur.fetchone()
        return bool(row[0])


def release_lock(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_unlock(%s);", (PG_ADVISORY_LOCK_KEY,))
    conn.commit()


def get_last_success(conn) -> Optional[dict]:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT *
            FROM "ImportRun"
            WHERE "jobName" = %s AND "status" = 'success'
            ORDER BY "startedAt" DESC
            LIMIT 1
            """,
            (IMPORT_JOB_NAME,),
        )
        return cur.fetchone()


def should_run(conn) -> tuple[bool, str]:
    last = get_last_success(conn)
    if not last:
        return True, "never-ran"

    started_at = last["startedAt"]
    now = utc_now()
    diff_hours = (now - started_at).total_seconds() / 3600

    if diff_hours >= IMPORT_MIN_HOURS:
        return True, "interval-expired"

    return False, f"too-early-last-success={started_at.isoformat()}"


def create_import_run(conn, trigger: str) -> str:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO "ImportRun" ("id", "jobName", "status", "trigger")
            VALUES (gen_random_uuid()::text, %s, 'running', %s)
            RETURNING "id";
            """,
            (IMPORT_JOB_NAME, trigger),
        )
        run_id = cur.fetchone()[0]
    conn.commit()
    return run_id


def finish_import_run(conn, run_id: str, status: str, message: str):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE "ImportRun"
            SET "status" = %s,
                "message" = %s,
                "finishedAt" = NOW()
            WHERE "id" = %s
            """,
            (status, message, run_id),
        )
    conn.commit()


def slug_exists_for_other(conn, slug: str, external_url: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 1
            FROM "Article"
            WHERE "slug" = %s
              AND COALESCE("externalUrl", '') <> COALESCE(%s, '')
            LIMIT 1
            """,
            (slug, external_url),
        )
        return cur.fetchone() is not None


def ensure_unique_slug(conn, base_slug: str, external_url: str) -> str:
    candidate = base_slug
    counter = 2

    while slug_exists_for_other(conn, candidate, external_url):
        candidate = f"{base_slug}-{counter}"
        counter += 1

    return candidate


def upsert_article(conn, article: dict):
    article["slug"] = ensure_unique_slug(conn, article["slug"], article.get("externalUrl"))

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO "Article" (
                "id",
                "title",
                "slug",
                "authorName",
                "authorBio",
                "category",
                "annotation",
                "imageUrl",
                "imageAlt",
                "content",
                "sources",
                "published",
                "externalUrl",
                "sourceSite",
                "sourceRssUrl",
                "guid",
                "rawHtml",
                "importedAt",
                "createdAt",
                "updatedAt"
            )
            VALUES (
                gen_random_uuid()::text,
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s,
                NOW(),
                COALESCE(%s::timestamptz, NOW()),
                NOW()
            )
            ON CONFLICT ("externalUrl")
            DO UPDATE SET
                "title" = EXCLUDED."title",
                "slug" = EXCLUDED."slug",
                "authorName" = EXCLUDED."authorName",
                "authorBio" = EXCLUDED."authorBio",
                "category" = EXCLUDED."category",
                "annotation" = EXCLUDED."annotation",
                "imageUrl" = EXCLUDED."imageUrl",
                "imageAlt" = EXCLUDED."imageAlt",
                "content" = EXCLUDED."content",
                "sources" = EXCLUDED."sources",
                "published" = EXCLUDED."published",
                "sourceSite" = EXCLUDED."sourceSite",
                "sourceRssUrl" = EXCLUDED."sourceRssUrl",
                "guid" = EXCLUDED."guid",
                "rawHtml" = EXCLUDED."rawHtml",
                "updatedAt" = NOW()
            """,
            (
                article["title"],
                article["slug"],
                article["authorName"],
                article.get("authorBio"),
                article["category"],
                article["annotation"],
                article["imageUrl"],
                article["imageAlt"],
                Json(article["content"]),
                Json(article["sources"]),
                article.get("published", True),
                article.get("externalUrl"),
                article.get("sourceSite"),
                article.get("sourceRssUrl"),
                article.get("guid"),
                article.get("rawHtml"),
                article.get("createdAt"),
            ),
        )
    conn.commit()