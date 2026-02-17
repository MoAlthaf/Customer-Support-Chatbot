import streamlit as st
import requests

st.set_page_config(page_title="Customer Support Chatbot", page_icon="💬")

st.title("💬 Customer Support Chatbot")

API_URL = "http://127.0.0.1:5000/chat"
RESET_URL = "http://127.0.0.1:5000/reset"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Reset Button
if st.button("🔄 Reset Conversation"):
    st.session_state.messages = []
    requests.post(RESET_URL)
    st.success("Conversation reset.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Send to backend
    response = requests.post(API_URL, json={"message": user_input})

    if response.status_code == 200:
        data = response.json()

        bot_reply = data["response"]

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        with st.chat_message("assistant"):
            st.markdown(bot_reply)

        # Show details
        with st.expander("Conversation Details"):
            st.write("**Intent:**", data["intent"])
            st.write("**Summary:**", data["summary"])

    else:
        st.error("Error communicating with backend API.")