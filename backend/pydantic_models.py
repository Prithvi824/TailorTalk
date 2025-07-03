"""This module contains Pydantic models for the Agent."""

# 1st party imports
from typing import Optional
from datetime import date, datetime

# 3rd party imports
from pydantic import BaseModel, Field


class CheckAvailability(BaseModel):
    """
    A model for representing the function signature for checking user's availability.
    """

    date_to_be_checked: date


class ChatRequest(BaseModel):
    """
    A model for representing the chat request.
    """

    message: str


class CreateEvent(BaseModel):
    """
    A model for representing the function signature for creating a new event.
    """

    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None


class UpdateEventTime(BaseModel):
    """
    A model for representing the function signature for updating an event's time.
    """

    event_id: str
    new_start_time: datetime
    new_end_time: datetime


class CancelEvent(BaseModel):
    """
    A model for representing the function signature for canceling an event.
    """

    event_id: str


class GetEventIdByStartTime(BaseModel):
    """
    A model for representing the function signature for getting an event's id by its start time.
    """

    start_time: datetime
    window_minutes: int = Field(60, description="±60 minutes around start_time by default.")
