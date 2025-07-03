"""
This module is the main entry point for the application.
It contains the FastAPI application and the chat endpoint.
"""

# 3rd party imports
from fastapi import FastAPI

# local imports
from .agent import BookingAgent
from .pydantic_models import ChatRequest

# create a fastapi instance
app = FastAPI(title="Calendar Chatbot API")

# Create a agent
booking_agent = BookingAgent()

@app.post("/chat")
async def chat(req: ChatRequest):
    """
    This endpoint handles chat requests.
    It takes a chat request and returns a chat response.
    """

    resp = booking_agent.agent.run(req.message)
    return {"response": resp}
