import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.tools import tool

from agent.agent_logic import Agent, Thread

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("LLM"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
    timeout=30,
)

@tool("calculator", description="Performs arithmetic calculations. Use this for any math problems.")
def calculator(expression: str) -> str:
    """Evaluate mathematical expressions."""
    return str(eval(expression))

agent = Agent(
    model=llm,
    tools=[calculator],
)

thread = Thread("You are a helpful arithmetic calculator. Help the user with their math problems. Strictly Use tool call.")

thread.append(HumanMessage("solve : 10-2*21"))

response = agent.invoke(thread.messages)

for m in thread.messages:
    print(m)
    print("-"*100)