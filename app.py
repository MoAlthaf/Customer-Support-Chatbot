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

    try:
        data = request.get_json()
        user_input = data.get("message")

        if not user_input:
            return jsonify({"error": "No message provided"}), 400

        result, chat_history, running_summary = get_response(
            user_input,
            chat_history,
            running_summary
        )

        if not result:
            return jsonify({"error": "Empty result from LLM"}), 500
        
        return jsonify({
        "intent": result.intent,
        "response": result.response,
        "summary": result.summary}), 200
    
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({
            "intent": "unknown",
            "response": "Internal formatting error. Please try again.",
            "summary": ""
        }), 200





@app.route("/reset", methods=["POST"])
def reset():
    global chat_history, running_summary
    chat_history = []
    running_summary = ""
    return jsonify({"message": "Conversation reset successful"})


if __name__ == "__main__":
    #debug mode to test locally
    #app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)