from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage
from typing import List, Dict, Any, Optional, Union
from agent.services.llm import LLM
from agent.services.thread import Thread


# class Agent:
#     def __init__(self, model: ChatOpenAI, tools: List):
#         self.model = model
#         self.tools = tools

#         if self.tools:
#             self.model = self.model.bind_tools(self.tools)

#         self.tool_map = {tool.name: tool for tool in self.tools}

#     def invoke(self, messages):
#         while True:
#             response = self.model.invoke(messages)
#             messages.append(response)

#             if response.tool_calls:
#                 for tool in response.tool_calls:
#                     tool_name = tool['name']
#                     tool_args = tool['args']
#                     tool_call_id = tool['id']
#                     result = self.tool_map[tool_name].invoke(tool_args)

#                     messages.append(ToolMessage(content=result, tool_call_id=tool_call_id, name=tool_name))

#             else:
#                 return response


class Agent:
    def __init__(self, model: LLM, tools: Optional[List] = None):
        self.model = model.connect()