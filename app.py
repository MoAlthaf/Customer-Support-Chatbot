from flask import Flask, request, jsonify
from chatbot import get_response
import os

app = Flask(__name__)

# In-memory storage (simple for lab assignment)
chat_history = []
running_summary = ""

@app.route("/")
def home():
    return "Customer Support Chatbot API is running!"

@app.route("/chat", methods=["POST"])
def chat():
    global chat_history, running_summary

    data = request.get_json()
    user_input = data.get("message")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    result, chat_history, running_summary = get_response(
        user_input,
        chat_history,
        running_summary
    )

    if result is None:
        return jsonify({"error": "LLM processing failed"}), 500

    return jsonify({
        "intent": result.intent,
        "response": result.response,
        "summary": result.summary
    })


@app.route("/reset", methods=["POST"])
def reset():
    global chat_history, running_summary
    chat_history = []
    running_summary = ""
    return jsonify({"message": "Conversation reset successful"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)