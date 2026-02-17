from flask import Flask,request,jsonify
from chatbot import get_response

app=Flask(__name__)

#Storing COnversation History
chat_history=[]

@app.route("/")
def home():
    return "Customer Support Chatbot is running!"

@app.route("/chat",methods=["POST"])
def chat():
    global chat_history

    data=request.get_json()
    user_input=data.get("message","")

    if not user_input:
        return jsonify({"error":"No message provided"}),400
    
    response,chat_history=get_response(user_input,chat_history)

    if response is None:
        return jsonify({"error":"Failed to get response from chatbot"}),500
    
    return jsonify({
        "intent":response.intent,
        "response":response.response,
        "summary":response.summary
    })

if __name__ == "__main__":
    app.run(debug=True)