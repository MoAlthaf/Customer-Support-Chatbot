from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import PydanticOutputParser

from dotenv import load_dotenv
import os
import json
import re
from pydantic import BaseModel, Field
from typing import Literal
# Load environment variables
#load_dotenv() #Only for local testing

if "MISTRAL_API_KEY" not in os.environ:
    raise ValueError("MISTRAL_API_KEY not found in environment variables. Please set it in the .env file.")

# -----------------------------
# Structured Output Schema
# -----------------------------

class SupportResponse(BaseModel):
    intent: Literal["Billing", "Refund", "Technical", "General"] = Field(
        ...,
        description="Must be one of: Billing, Refund, Technical, General."
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
    content=f"""You are a professional Customer Support Assistant.

Current conversation summary:
{running_summary}

CRITICAL: You MUST respond with ONLY valid JSON, nothing else. No text before or after.

Required JSON structure EXACTLY like this:
{{
  "intent": "Billing",
  "response": "Your response text here",
  "summary": "Updated summary of conversation"
}}

Rules:
1. The "intent" field MUST be exactly one of: Billing, Refund, Technical, or General
2. If unclear, set intent to "General"
3. Always include all three fields
4. Return ONLY JSON - no markdown, no explanations, no extra text
5. Valid JSON only

{format_instructions}"""
                 )
    
    # Build clean message list (NO JSON in history)
    messages = [system_message]
    messages.extend(chat_history)
    messages.append(HumanMessage(content=user_input))

    try:
        response = llm.invoke(messages)
        raw_content = response.content.strip()
        structured_response = None
        
        try:
            # Try to parse as JSON first
            structured_response = parser.parse(raw_content)
        except Exception as parse_error:
            # If parsing fails, try to extract JSON from the response
            print(f"Initial parse failed: {parse_error}")
            print(f"Raw output: {raw_content}")
            
            # Try to find JSON object in the response
            json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(0)
                    parsed_json = json.loads(json_str)
                    
                    # Create response with extracted JSON
                    structured_response = SupportResponse(
                        intent=parsed_json.get("intent", "General"),
                        response=parsed_json.get("response", raw_content),
                        summary=parsed_json.get("summary", running_summary)
                    )
                except Exception as json_error:
                    print(f"JSON extraction failed: {json_error}")
            
            # If JSON extraction also failed, use safe fallback
            if structured_response is None:
                print("Using safe fallback response")
                structured_response = SupportResponse(
                    intent="General",
                    response=raw_content,
                    summary=running_summary
                )

        # Update running summary from model output
        updated_summary = structured_response.summary

        # Store only natural conversation messages
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=structured_response.response))

        return structured_response, chat_history, updated_summary

    except Exception as e:
        print(f"Error in get_response: {e}")
        
        # Final fallback: return a safe response with General intent
        fallback_response = SupportResponse(
            intent="General",
            response="I encountered a processing issue. Could you please rephrase your question?",
            summary=running_summary
        )
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=fallback_response.response))
        return fallback_response, chat_history, running_summary


# -----------------------------
# Local Testing 
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