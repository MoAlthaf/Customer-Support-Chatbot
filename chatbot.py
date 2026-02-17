from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import PydanticOutputParser

from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

if "MISTRAL_API_KEY" not in os.environ:
    raise ValueError("MISTRAL_API_KEY not found in environment variables. Please set it in the .env file.")

# -----------------------------
# Structured Output Schema
# -----------------------------

class SupportResponse(BaseModel):
    intent: str = Field(
        ...,
        description="The intent of the user's query (Billing, Refund, Technical, General)."
    )
    response: str = Field(
        ...,
        description="Personalized response to the user's query."
    )
    summary: str = Field(
        ...,
        description="Updated concise summary of the entire conversation so far."
    )

parser = PydanticOutputParser(pydantic_object=SupportResponse)
format_instructions = parser.get_format_instructions()

# -----------------------------
# LLM Setup
# -----------------------------

llm = ChatMistralAI(
    model="mistral-small",
    temperature=0.2,
    api_key=os.getenv("MISTRAL_API_KEY")
)

# -----------------------------
# Core Chat Function
# -----------------------------

def get_response(user_input, chat_history, running_summary):
    """
    user_input: str
    chat_history: list of LangChain messages (HumanMessage, AIMessage)
    running_summary: str (summary of conversation so far)
    """

    # System prompt with injected running summary
    system_message = SystemMessage(
        content=f"""
You are a professional Customer Support Assistant.

Current conversation summary:
{running_summary}

Tasks:
1. Classify intent (Billing, Refund, Technical, General).
2. Provide a helpful and personalized response.
3. Update the conversation summary concisely to reflect the entire conversation so far.

Return your answer strictly in the following JSON format:
{format_instructions}
"""
    )

    # Build clean message list (NO JSON in history)
    messages = [system_message]
    messages.extend(chat_history)
    messages.append(HumanMessage(content=user_input))

    try:
        response = llm.invoke(messages)

        structured_response = parser.parse(response.content)

        # Update running summary from model output
        updated_summary = structured_response.summary

        # Store only natural conversation messages
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=structured_response.response))

        return structured_response, chat_history, updated_summary

    except Exception:
        return None, chat_history, running_summary


# -----------------------------
# Local Testing (CLI Mode)
# -----------------------------

if __name__ == "__main__":
    chat_history = []
    running_summary = ""

    while True:
        user_input = input("User: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chatbot. Goodbye!")
            break

        result, chat_history, running_summary = get_response(
            user_input,
            chat_history,
            running_summary
        )

        if result:
            print("Intent:", result.intent)
            print("Response:", result.response)
            print("Updated Summary:", result.summary)
        else:
            print("Error processing request.")