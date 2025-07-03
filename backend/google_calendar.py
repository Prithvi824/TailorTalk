"""
This module contains the Google Calendar integration for the Agent.
"""

# special imports
from __future__ import annotations

# 1st party imports
import pytz
from typing import Dict, Any, List, Optional
from datetime import date, datetime, time, timedelta

# 3rd party imports
from google.oauth2 import service_account
from googleapiclient.discovery import build

# local imports
from .config import CALENDAR_ID, TIMEZONE

# initialize timezone
tz = pytz.timezone(TIMEZONE)


class GoogleCalendar:
    """
    A class to interact with Google Calendar using the provided service account credentials.

    This class provides methods to initialize the Google Calendar API service and to check
    whether the user is free on a specified date.

    Attributes:
        CREDS: The Google service account credentials.
        SERVICE: The Google Calendar API service object.

    Methods:
        __init__(scopes: List[str], credentials: Dict[str, Any]):
            Initializes the Google Calendar API service with the given scopes and credentials.

        is_free_on_date(date_to_be_checked: date) -> bool:
            Checks if the user has any events scheduled (i.e., is busy) on the provided date.
    """

    def __init__(self, scopes: List[str], credentials: Dict[str, Any]):
        """
        This function is used to initialize the Google Calendar service.

        Args:
            scopes (List[str]): The scopes for the calendar.
            credentials (Dict[str, Any]): The credentials for the calendar.
        """

        self.CREDS = service_account.Credentials.from_service_account_file(
            credentials, scopes=scopes
        )
        self.SERVICE = build(
            "calendar", "v3", credentials=self.CREDS, cache_discovery=False
        )

    def is_free_on_date(self, date_to_be_checked: date) -> bool:
        """
        This function is used to check if the user is free on a specific date.

        Args:
            date_to_be_checked (date): The date to check.
        Returns:
            bool: True if the user is free on the date, False otherwise.
        """

        # create a time range from 00:00 hours to midnight
        start = datetime.combine(date_to_be_checked, time(0, 0)).astimezone(
            pytz.timezone(TIMEZONE)
        )
        end = datetime.combine(date_to_be_checked, time(23, 59)).astimezone(
            pytz.timezone(TIMEZONE)
        )

        # create the body
        body = {
            "timeMin": start.isoformat(),
            "timeMax": end.isoformat(),
            "timeZone": TIMEZONE,
            "items": [{"id": CALENDAR_ID}],
        }

        # fetch the response
        response = self.SERVICE.freebusy().query(body=body).execute()
        busy_slots = response["calendars"][CALENDAR_ID]["busy"]

        # check if any busy slots are available
        return len(busy_slots) == 0

    def create_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
    ) -> str:
        """This function creates a calendar event.

        Args:
            title: Title (summary) of the event.
            start_time: Event start as a timezone-aware ``datetime``.
            end_time: Event end as a timezone-aware ``datetime``.
            description: Optional long-form description.

        Returns:
            str: The Google Calendar ``eventId`` of the newly created event.
        """

        # Ensure datetimes are timezone-aware
        if start_time.tzinfo is None:
            start_time = tz.localize(start_time)
        if end_time.tzinfo is None:
            end_time = tz.localize(end_time)

        # create the event body
        event_body: Dict[str, Any] = {
            "summary": title,
            "description": description or "",
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": TIMEZONE,
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": TIMEZONE,
            },
        }

        # create the event
        created_event = (
            self.SERVICE.events()
            .insert(calendarId=CALENDAR_ID, body=event_body, sendUpdates="all")
            .execute()
        )
        return created_event["id"]

    def update_event_time(
        self,
        event_id: str,
        new_start_time: datetime,
        new_end_time: datetime,
    ) -> bool:
        """Update the start/end time of an existing event.

        Args:
            event_id: The event identifier returned from ``create_event``.
            new_start_time: New start time as timezone-aware ``datetime``.
            new_end_time: New end time as timezone-aware ``datetime``.

        Returns:
            bool: ``True`` if the update succeeded.
        """

        # localize the new start and end times if they are not timezone-aware
        if new_start_time.tzinfo is None:
            new_start_time = tz.localize(new_start_time)
        if new_end_time.tzinfo is None:
            new_end_time = tz.localize(new_end_time)

        try:

            # get the event
            event = (
                self.SERVICE.events()
                .get(calendarId=CALENDAR_ID, eventId=event_id)
                .execute()
            )
        except Exception:
            return False

        # update the event start and end times
        event["start"]["dateTime"] = new_start_time.isoformat()
        event["end"]["dateTime"] = new_end_time.isoformat()

        try:

            # update the event
            self.SERVICE.events().update(
                calendarId=CALENDAR_ID,
                eventId=event_id,
                body=event,
                sendUpdates="all",
            ).execute()
            return True
        except Exception:
            return False

    def cancel_event(self, event_id: str) -> bool:
        """Cancel (delete) an event from the calendar.

        Args:
            event_id: The event identifier returned from ``create_event``.

        Returns:
            bool: ``True`` if deletion succeeded.
        """

        try:
            # delete the event
            self.SERVICE.events().delete(
                calendarId=CALENDAR_ID, eventId=event_id, sendUpdates="all"
            ).execute()
            return True
        except Exception:
            return False

    def get_event_id_by_start_time(
        self,
        start_time: datetime,
        window_minutes: int = 60,
    ) -> Optional[str]:
        """Return the Google Calendar event ID whose start time matches *start_time*.

        Args:
            start_time: Target start ``datetime`` (timezone-aware preferred). If
                naïve, we assume the default ``TIMEZONE``.
            window_minutes: How many minutes on either side of *start_time* to
                search. Defaults to ±60 minute.

        Returns:
            The ``eventId`` if exactly one event is found within the window,
            otherwise ``None``.
        """

        # Normalise to timezone-aware  datetime
        if start_time.tzinfo is None:
            start_time = tz.localize(start_time)

        # create the window
        time_min_dt = start_time - timedelta(minutes=window_minutes)
        time_max_dt = start_time + timedelta(minutes=window_minutes)

        # fetch the events
        events_result = (
            self.SERVICE.events()
            .list(
                calendarId=CALENDAR_ID,
                timeMin=time_min_dt.isoformat(),
                timeMax=time_max_dt.isoformat(),
                singleEvents=True,
                timeZone=TIMEZONE,
            )
            .execute()
        )

        # search for the event in the window
        for event in events_result.get("items", []):

            # get the start time of the event
            raw_start = event.get("start", {}).get("dateTime") or event.get(
                "start", {}
            ).get("date")
            if not raw_start:
                continue

            # convert the start time to datetime
            try:
                ev_dt = datetime.fromisoformat(raw_start)
            except ValueError:
                # Google can return Z-suffix; handle via fromisoformat after replace
                ev_dt = datetime.fromisoformat(raw_start.replace("Z", "+00:00"))

            # localize the event start time if it is not timezone-aware
            if ev_dt.tzinfo is None:
                ev_dt = tz.localize(ev_dt)

            # Check if the event start time is within the window
            if abs((ev_dt - start_time).total_seconds()) <= window_minutes * 60:
                return event["id"]

        # No matching event found
        return None
