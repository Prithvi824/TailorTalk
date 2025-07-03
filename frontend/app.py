"""
This module contains the Streamlit app for the agent.
"""

# 1st party imports
import os
import httpx

# 3rd party imports
import streamlit as st

# fetch the api url
try:
    API_URL = st.secrets["API_URL"]
except Exception:
    API_URL = os.getenv("API_URL", "http://localhost:8000/chat")

# create a title and chat container
st.title("📅 Calendar Booking Assistant")
chat_container = st.container()

# create a session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# display the chat
for m in st.session_state["messages"]:
    chat_container.chat_message(m["role"]).write(m["content"])

# handle user input
prompt = st.chat_input("Ask me to book, reschedule, or cancel a meeting…")
if prompt:

    # add user message to session state
    st.session_state["messages"].append({"role": "user", "content": prompt})
    chat_container.chat_message("user").write(prompt)

    # send the prompt to the backend
    with st.spinner("Thinking…"):
        try:
            resp = httpx.post(API_URL, json={"message": prompt}, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            ans = data.get("response", str(data))
        except Exception as e:
            ans = f"Backend error: {e}\n\nRaw response: {getattr(resp, 'text', '')}"
        except Exception as e:
            ans = f"Backend error: {e}\n\nRaw response: {getattr(resp, 'text', '')}"
    st.session_state["messages"].append({"role": "assistant", "content": ans})
    chat_container.chat_message("assistant").write(ans)
