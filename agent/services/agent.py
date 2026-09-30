from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage
from typing import List, Dict, Any, Optional, Union


class Agent:
    def __init__(self, model: ChatOpenAI, tools: List):
        self.model = model
        self.tools = tools

        if self.tools:
            self.model = self.model.bind_tools(self.tools)

        self.tool_map = {tool.name: tool for tool in self.tools}

    def invoke(self, messages):
        while True:
            response = self.model.invoke(messages)
            messages.append(response)

            if response.tool_calls:
                for tool in response.tool_calls:
                    tool_name = tool['name']
                    tool_args = tool['args']
                    tool_call_id = tool['id']
                    result = self.tool_map[tool_name].invoke(tool_args)

                    messages.append(ToolMessage(content=result, tool_call_id=tool_call_id, name=tool_name))

            else:
                return response
