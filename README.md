# Customer Support Chatbot

An intelligent customer support chatbot powered by the Mistral AI API, built with Flask backend and Streamlit frontend.

## Overview

This project implements an AI-driven customer support assistant that:
- **Classifies user queries** into intents: Billing, Refund, Technical, or General
- **Provides personalized responses** based on conversation context
- **Maintains conversation summaries** for continuity across exchanges

## Architecture

### Backend (`app.py`)
- Flask REST API with two main endpoints:
  - `POST /chat` - Processes user messages and returns intent, response, and summary
  - `POST /reset` - Clears conversation history

### Chatbot Core (`chatbot.py`)
- Uses **LangChain** with **Mistral AI** (`mistral-small` model)
- Structured output using Pydantic with JSON formatting
- Maintains chat history and running conversation summary
- Temperature set to 0.2 for consistent, focused responses

### Frontend (`streamlit_app.py`)
- Interactive web UI for conversation
- Real-time chat display with message history
- One-click conversation reset
- Communicates with Flask backend via HTTP requests

## Setup & Running

### Prerequisites
- Python 3.8+
- Mistral API key (set `MISTRAL_API_KEY` in `.env`)

### Installation
```bash
pip install -r requirements.txt
```

### Run the Application
1. **Terminal 1 - Start Backend:**
   ```bash
   python app.py
   ```

2. **Terminal 2 - Start Frontend:**
   ```bash
   streamlit run streamlit_app.py
   ```

The Streamlit app will be available at `http://localhost:8501`

## Key Features
- ✅ Real-time intent classification
- ✅ Context-aware responses with conversation memory
- ✅ Clean separation of backend API and frontend UI
- ✅ Structured JSON outputs for easy integration
