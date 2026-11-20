from datetime import date as Date
from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class EventTime(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    date_time: datetime | None = Field(default=None, alias="dateTime")  # timed event
    date: Date | None = None  # all-day event


class CalendarEvent(BaseModel):
    id: str
    summary: str | None = None
    start: EventTime
    end: EventTime


class CalendarEventList(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[CalendarEvent] = []
    next_page_token: str | None = Field(default=None, alias="nextPageToken")
