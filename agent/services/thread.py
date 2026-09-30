from typing import List, Dict, Optional, Union
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage

class Thread:
    def __init__(
        self,
        system_prompt: Union[str, SystemMessage],
        messages: List[Union[ToolMessage, AIMessage, HumanMessage]] = None,
    ):
        self.messages = messages or []
        self.system_prompt = system_prompt

        if self.system_prompt is not None:
            if isinstance(self.system_prompt, str):
                self.system_prompt = SystemMessage(self.system_prompt)
            
            self.messages = [self.system_prompt] + self.messages


    def append(self, message: Union[ToolMessage, AIMessage, HumanMessage]):
        self.messages.append(message)
