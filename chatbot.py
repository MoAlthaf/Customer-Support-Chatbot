from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv
import os

load_dotenv()

from pydantic import BaseModel,Field

class SupportResponse(BaseModel):
    intent: str = Field(..., description="The intent of the user's query, e.g., 'billing_issue', 'technical_support', 'general_inquiry'.")
    response: str = Field(description="The response to the user's query.")
    summary: str = Field(description="A brief summary of the conversation so far.")

from langchain_core.output_parsers import PydanticOutputParser

parser = PydanticOutputParser(pydantic_object=SupportResponse)

if "MISTRAL_API_KEY" not in os.environ:
    raise ValueError("MISTRAL_API_KEY not found in environment variables. Please set it in the .env file.")



llm=ChatMistralAI(
    model="mistral-small",
    temperature=0.2,
    api_key=os.getenv("MISTRAL_API_KEY")
    )


format_instructions=parser.get_format_instructions()

system_message = SystemMessage(
    content=f"""
You are a professional Customer Support Assistant.

Tasks:
1. Classify intent (Billing, Refund, Technical, General)
2. Provide a personalized response
3. Provide a short conversation summary

Return your answer in the following JSON format:
{format_instructions}
"""
)



def get_response(user_input,chat_history):
    if len(chat_history) == 0:
        chat_history.append(system_message)

    chat_history.append(HumanMessage(content=user_input))
    try:
        response = llm.invoke(chat_history)
    
        structured_response=parser.parse(response.content)

        chat_history.append(AIMessage(content=response.content))

        return structured_response,chat_history
    except Exception as e:
        return "Sorry, there was an error processing your request. Please try again later.", chat_history
    
    

if __name__ == "__main__":
    chat_history = []

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chatbot. Goodbye!")
            break
        response, chat_history = get_response(user_input, chat_history)
        print(f"Chatbot: {response}")