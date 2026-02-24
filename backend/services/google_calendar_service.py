"""
Google Calendar integration for fetching available call slots.

Reads free/busy from callassistant@getniro.ai via the Calendar API.
Requires a service account with 'See only free/busy (hide details)' access
to the calendar (share from Google Calendar settings).

Env vars:
  GOOGLE_CALENDAR_ID          defaults to callassistant@getniro.ai
  GOOGLE_SERVICE_ACCOUNT_JSON full JSON string of the service account key file
  BUSINESS_START_HOUR         default 9  (IST)
  BUSINESS_END_HOUR           default 18 (IST)
  BUSINESS_DAYS               not configurable via env; Mon–Fri hardcoded

Dev mode: when GOOGLE_SERVICE_ACCOUNT_JSON is not set, all business-hours
slots are returned as available so the UI works without credentials.
"""

import asyncio
import json
import logging
import os
from datetime import date as date_type
from datetime import datetime, timedelta

import pytz

logger = logging.getLogger(__name__)

CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID", "callassistant@getniro.ai")
SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
BUSINESS_START_HOUR = int(os.environ.get("BUSINESS_START_HOUR", "9"))
BUSINESS_END_HOUR = int(os.environ.get("BUSINESS_END_HOUR", "18"))
SLOT_DURATION = 10  # minutes
BUSINESS_DAYS = {0, 1, 2, 3, 4}  # Mon–Fri
IST = pytz.timezone("Asia/Kolkata")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def get_available_slots(requested_date: date_type) -> tuple:
    """
    Returns (slots: list[dict], timezone: str) for the requested date.

    Each slot dict: { "time": "HH:MM", "displayTime": "H:MM AM/PM", "available": bool }
    """
    if requested_date.weekday() not in BUSINESS_DAYS:
        return [], "Asia/Kolkata"

    all_slots = _generate_slots(requested_date)
    if not all_slots:
        return [], "Asia/Kolkata"

    if not SERVICE_ACCOUNT_JSON:
        logger.info(
            "[DEV] GOOGLE_SERVICE_ACCOUNT_JSON not set — "
            "returning all business-hours slots as available"
        )
        return [{**s, "available": True} for s in all_slots], "Asia/Kolkata"

    busy = await _fetch_busy_times(requested_date)
    slots = [{**s, "available": s["time"] not in busy} for s in all_slots]
    return slots, "Asia/Kolkata"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _generate_slots(requested_date: date_type) -> list:
    """Return all 10-min slot dicts for business hours, filtering past slots."""
    slots = []
    cur = BUSINESS_START_HOUR * 60
    end = BUSINESS_END_HOUR * 60
    while cur + SLOT_DURATION <= end:
        h, m = divmod(cur, 60)
        slots.append(
            {
                "time": f"{h:02d}:{m:02d}",
                "displayTime": f"{h % 12 or 12}:{m:02d} {'AM' if h < 12 else 'PM'}",
            }
        )
        cur += SLOT_DURATION

    # Remove past slots when requested_date is today (IST)
    now_local = datetime.now(IST)
    if requested_date == now_local.date():
        now_mins = now_local.hour * 60 + now_local.minute
        slots = [
            s
            for s in slots
            if (int(s["time"][:2]) * 60 + int(s["time"][3:])) > now_mins
        ]

    return slots


async def _fetch_busy_times(requested_date: date_type) -> set:
    """Query Google Calendar freebusy API and return a set of busy 'HH:MM' strings."""
    try:
        sa_info = json.loads(SERVICE_ACCOUNT_JSON)
    except Exception as exc:
        logger.error(f"[Calendar] Failed to parse GOOGLE_SERVICE_ACCOUNT_JSON: {exc}")
        return set()

    day_start = IST.localize(
        datetime(requested_date.year, requested_date.month, requested_date.day, 0, 0, 0)
    )
    day_end = day_start + timedelta(days=1)

    def _query_sync():
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        creds = service_account.Credentials.from_service_account_info(
            sa_info,
            scopes=["https://www.googleapis.com/auth/calendar.readonly"],
        )
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        body = {
            "timeMin": day_start.isoformat(),
            "timeMax": day_end.isoformat(),
            "items": [{"id": CALENDAR_ID}],
        }
        return service.freebusy().query(body=body).execute()

    try:
        data = await asyncio.to_thread(_query_sync)
    except Exception as exc:
        logger.error(f"[Calendar] freebusy query failed: {exc}")
        return set()

    busy_periods = data.get("calendars", {}).get(CALENDAR_ID, {}).get("busy", [])
    busy_times: set = set()

    for period in busy_periods:
        start_dt = datetime.fromisoformat(period["start"].replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(period["end"].replace("Z", "+00:00"))
        start_local = start_dt.astimezone(IST)
        end_local = end_dt.astimezone(IST)

        cur = start_local.hour * 60 + start_local.minute
        end_min = end_local.hour * 60 + end_local.minute
        while cur < end_min:
            h, m = divmod(cur, 60)
            busy_times.add(f"{h:02d}:{m:02d}")
            cur += SLOT_DURATION

    logger.info(
        f"[Calendar] {requested_date}: {len(busy_periods)} busy periods → "
        f"{len(busy_times)} blocked slots"
    )
    return busy_times
