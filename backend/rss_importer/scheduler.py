from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from .config import TIMEZONE, DEFAULT_LIMIT_PER_FEED
from .main import run
from .db import get_connection


def scheduled_job():
    conn = get_connection()
    try:
        run(conn, force=False, trigger="schedule", limit=DEFAULT_LIMIT_PER_FEED)
    finally:
        conn.close()


if __name__ == "__main__":
    tz = pytz.timezone(TIMEZONE)
    scheduler = BlockingScheduler(timezone=tz)

    scheduler.add_job(
        scheduled_job,
        CronTrigger(day_of_week="mon,thu", hour=3, minute=0, timezone=tz),
        id="rss-import-twice-weekly",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    print(f"RSS scheduler started, timezone={TIMEZONE}, schedule=Mon/Thu 03:00")
    scheduler.start()