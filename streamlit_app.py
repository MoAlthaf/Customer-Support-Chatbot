import streamlit as st
import requests
from dotenv import load_dotenv
import os


st.set_page_config(page_title="Customer Support Chatbot", page_icon=":speech_balloon:")

st.title("Customer Support Chatbot")

load_dotenv()
API_URL = os.getenv("API_URL")
CHAT_URL = f"{API_URL}/chat"
#Storing Chat

if "messages" not in st.session_state:
    st.session_state.messages = []

#Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Send to Flask API
    response = requests.post(CHAT_URL, json={"message": user_input})

    if response.status_code == 200:
        data = response.json()
        bot_reply = data["response"]

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        with st.chat_message("assistant"):
            st.markdown(bot_reply)

        # Optional: show intent + summary
        with st.expander("Conversation Details"):
            st.write("**Intent:**", data["intent"])
            st.write("**Summary:**", data["summary"])

    else:
        st.error("Error communicating with backend API.")