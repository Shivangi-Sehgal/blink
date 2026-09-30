import tiktoken



from typing import List, Dict, Optional, Union
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage

# class Thread:
#     def __init__(
#         self,
#         system_prompt: Union[str, SystemMessage],
#         messages: List[Union[ToolMessage, AIMessage, HumanMessage]] = None,
#     ):
#         self.messages = messages or []
#         self.system_prompt = system_prompt

#         if self.system_prompt is not None:
#             if isinstance(self.system_prompt, str):
#                 self.system_prompt = SystemMessage(self.system_prompt)
            
#             self.messages = [self.system_prompt] + self.messages


#     def append(self, message: Union[ToolMessage, AIMessage, HumanMessage]):
#         self.messages.append(message)


class Thread:
    messages: List[Union[SystemMessage, AIMessage, ToolMessage, HumanMessage]]
    root: Optional[Thread] = None
    parent: Optional[Thread] = None
    child: Optional[Thread] = None
    tail: Optional[Thread] = None

    def __init__(
        self,
        messages: Optional[List[Union[SystemMessage, HumanMessage, AIMessage, ToolMessage]]] = None,
        system_prompt: Optional[Union[str, SystemMessage]] = None,
        compression_prompt: Optional[str] = None,
        compression_token_limit: Optional[int] = None,
        tool_hide_rules: Optional[List[Union[ToolHideRule, AutoToolHideRule]]] = None
    ):
        self.messages = []
        self.system_prompt = system_prompt
        self.compression_prompt = compression_prompt
        self.compression_token_limit = compression_token_limit
        self.tool_hide_rules = tool_hide_rules
        self.encoder = tiktoken.encoding_for_model("gpt-4o-mini")   # To convert the tool message into tokens
        self.agent = None
        self.root = None
        self.parent = None
        self.child = None
        self.tail = None
        self.path = Path.cwd() / "tool_results"
        self.path.mkdir(parents=True, exist_ok=True)


        def save_tool_result(self, message: ToolMessage) -> bool:
            try:
                content = message.content

                if isinstance(content, dict):
                    content = json.dumps(content)

                else:
                    content = str(content)
                
                with open(self.path / str(message.tool_call_id), "w", encoding="utf-8") as f:
                    f.write(content)
                
                return True

            except:
                return False

        @classmethod
        def get_tool_result_path(cls):
            path = Path.cwd() / "tool_results"
            path.mkdir(parents=True, exist_ok=True)
            return path


        def append(self, message: Union[SystemMessage, HumanMessage, AIMessage, ToolMessage]):
            if self.root is not None:      # If we are on the main root thread
                tool_hide_rules = self.tool_hide_rules
            else:
                tool_hide_rules = self.tool_hide_rules
            
            thread_hide_rules = []
            auto_tool_hide_rules = None

            if tool_hide_rules is not None:
                thread_hide_rules = [rule for rule in tool_hide_rules if isinstance(rule, ToolHideRule)]

                auto_tool_hide_rule = [rule for rule in tool_hide_rules if isinstance(rule, AutoToolHideRule)]
            

            # This code block - saves the last tool content and then replaces its tool content with the provided toolhiderule message.
            if isinstance(message, ToolMessage) and tool_hide_rules is not None:
                name = message.name  # Get the actual tool name
                match = False
                tool_hide_rule = None
                for rule in thread_hide_rules:    # Fetching the details of thread hide rules
                    if rule.name == name:
                        match = True
                        tool_hide_rule = rule     # Stores the replacement message for that tool name

                if match:
                    assert tool_hide_rule is not None  # another check to make sure that the tool hide rule is not none
                    for msg in reversed(self.messages):
                        if isinstance(msg, ToolMessage) and msg.name == name:
                            self.messages.save_tool_result(msg)
                            msg.content = tool_hide_rule.message + f"\n Tool Call ID : {msg.tool_call_id}. Use this ID to retrieve the tool result using collapsed_tool_result" 
                            break

