from datetime import datetime

from google.auth.exceptions import RefreshError

from app.config import config
from app.email_service.gmail.token_manager import GmailTokenManager
from app.email_service.gmail.types.calendar_event import CalendarEvent
from app.email_service.gmail.types.calendar_event import CalendarEventList
from app.email_service.gmail.types.error import GmailServiceError

BASE_URL = "https://www.googleapis.com/calendar/v3"


class GoogleCalendarService:

    def __init__(self, token_manager: GmailTokenManager) -> None:
        self.timeout = config.GMAIL_TIMEOUT_SECONDS
        self._session = token_manager.get_session()

    def list_events(self, time_min: datetime, time_max: datetime) -> list[CalendarEvent]:
        params = {
            "timeMin": time_min.isoformat(),
            "timeMax": time_max.isoformat(),
            "singleEvents": "true",
            "orderBy": "startTime",
            "maxResults": 250,
        }
        events: list[CalendarEvent] = []

        while True:
            try:
                response = self._session.get(f"{BASE_URL}/calendars/primary/events", params=params, timeout=self.timeout)
            except RefreshError as error:
                raise GmailServiceError("Google access expired. Please reconnect.", status_code=401) from error

            if response.status_code == 403:
                raise GmailServiceError("Calendar access not granted. Please reconnect.", status_code=403)
            if not response.ok:
                raise GmailServiceError("Calendar request failed.", status_code=response.status_code)

            page = CalendarEventList.model_validate(response.json())
            events.extend(page.items)

            if page.next_page_token is None:
                return events
            params["pageToken"] = page.next_page_token
