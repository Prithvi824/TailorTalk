"""
This module contains the configuration for the application.
"""

# 1st party imports
import os
from typing import List

# 3rd party imports
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API key
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

# Path to your Google service-account credentials JSON file
GOOGLE_CREDS_JSON: str = os.getenv("GOOGLE_CREDS_JSON")

# Google Calendar ID where events will be booked
CALENDAR_ID: str = os.getenv("CALENDAR_ID")

# Default timezone for all operations
TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Kolkata")

# OpenAI model and organization (optional)
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Define scopes for the google calender
SCOPES: List[str] = ["https://www.googleapis.com/auth/calendar"]

# Asserts
assert OPENAI_API_KEY, "OPENAI_API_KEY must be set in .env"
assert GOOGLE_CREDS_JSON, "GOOGLE_CREDS_JSON must be set in .env"
assert CALENDAR_ID, "CALENDAR_ID must be set in .env"
