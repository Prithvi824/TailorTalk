"""
This module contains the LangChain agent that can
book, reschedule, or cancel Google Calendar events.
"""

# 1st party imports
from typing import List

# 3rd party imports
from langchain_openai import ChatOpenAI
from langchain.tools import StructuredTool
from langchain.agents import initialize_agent, AgentType

# local imports
from .google_calendar import GoogleCalendar
from .config import OPENAI_API_KEY, OPENAI_MODEL, SCOPES, GOOGLE_CREDS_JSON
from .pydantic_models import (
    CheckAvailability,
    CreateEvent,
    UpdateEventTime,
    CancelEvent,
    GetEventIdByStartTime,
)


class BookingAgent:
    """
    A class to represent the booking agent.

    Attributes:
        google_calender: The Google Calendar service object.
        llm: The ChatOpenAI object.
        tools: The list of tools that the agent will use.
        agent: The initialized agent.
    """

    def __init__(self):
        """
        Initialize the agent with the necessary tools.
        """

        # initialize the google calender
        self.google_calender = GoogleCalendar(SCOPES, GOOGLE_CREDS_JSON)

        # initialize the llm
        self.llm = ChatOpenAI(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
        self.tools = self._load_tools()
        self.agent = initialize_agent(
            self.tools, self.llm, agent=AgentType.OPENAI_FUNCTIONS
        )

    def _load_tools(self) -> List[StructuredTool]:
        """
        Load the tools that the agent will use.

        Returns:
            List[Tool]: A list of tools that the agent will use.
        """

        return [
            StructuredTool.from_function(
                func=self.google_calender.is_free_on_date,
                name="check_availability",
                description="Check user's calendar for busy time slots on a specific day. if the year is not specified take the current year (2025). If the month is not specified take the current month (7). Returns True if the user is free on the date, False otherwise.",
                args_schema=CheckAvailability,
                handle_tool_error=True,
            ),
            StructuredTool.from_function(
                func=self.google_calender.create_event,
                name="create_event",
                description="Create a calendar event.  if the year is not specified take the current year (2025). If the month is not specified take the current month (7). Returns the event id of the newly created event.",
                args_schema=CreateEvent,
                handle_tool_error=True,
            ),
            StructuredTool.from_function(
                func=self.google_calender.update_event_time,
                name="update_event_time",
                description="Update the start/end time of an existing event. Returns true if the update succeeded.",
                args_schema=UpdateEventTime,
                handle_tool_error=True,
            ),
            StructuredTool.from_function(
                func=self.google_calender.cancel_event,
                name="cancel_event",
                description="Cancel (delete) an event from the calendar. Returns the event id of the deleted event.",
                args_schema=CancelEvent,
                handle_tool_error=True,
            ),
            StructuredTool.from_function(
                func=self.google_calender.get_event_id_by_start_time,
                name="get_event_id_by_start_time",
                description="Get the event id of an event by its start time. Returns the event id of the event.",
                args_schema=GetEventIdByStartTime,
                handle_tool_error=True,
            ),
        ]
