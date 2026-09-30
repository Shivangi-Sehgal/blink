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

    @classmethod
    def get_tool_result_path(cls):
        path = Path.cwd() / "tool_results"
        path.mkdir(parents=True, exist_ok=True)
        return path


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

    # Calculate the tokens for the whole thread messages.
    def count_tokens(self):
        if self.tail is not None:
            content = [msg.content for msg in self.tail.messages]

        else:
            content = [msg.content for msg in self.messages]

        merged = "\n".join(str(m) for m in content)
        return len(self.encoder.encode(merged))

    # Calculate the tokens for the particular given tool content.
    def calculate_tokens(self, content):
        return len(self.encoder.encode(str(content)))


    def append(self, message: Union[SystemMessage, HumanMessage, AIMessage, ToolMessage]):
        if self.root is not None:      # If we are on the main root thread
            tool_hide_rules = self.tool_hide_rules
        else:
            tool_hide_rules = self.tool_hide_rules
        
        thread_hide_rules = []
        auto_tool_hide_rules = None

        if tool_hide_rules is not None:
            thread_hide_rules = [rule for rule in tool_hide_rules if isinstance(rule, ToolHideRule)]

            for rule in tool_hide_rules:
                if isinstance(rule, AutoToolHideRule):
                    auto_tool_hide_rules = rule
                    break
        

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
                        self.save_tool_result(msg)
                        msg.content = tool_hide_rule.message + f"\n Tool Call ID : {msg.tool_call_id}. Use this ID to retrieve the tool result using collapsed_tool_result" 
                        break


        # This code block - collapses the tool call result if the total tokens are greater than the token limit or if the per_tool_token_limit is greater than the provided toool token limit.
        if auto_tool_hide_rules is not None:
            total_tokens = self.count_tokens()
            if total_tokens >= auto_tool_hide_rules.token_limit:
                if auto_tool_hide_rules.per_tool_token_limit is not None:
                    per_tool_token_limit = auto_tool_hide_rules.per_tool_token_limit
                    for msg in reversed(self.messages):
                        if isinstance(msg, ToolMessage) and self.calculate_tokens(msg.content) > per_tool_token_limit:
                            self.save_tool_result(msg)
                            msg.content = f"This tool call result has been collapsed due to token size constraints. \n Tool Call ID : {msg.tool_call_id} : use this Tool Call ID to retrieve the tool call result using collapsed_tool_result."

                
                # If the per_tool_token_limit is not given then we will use the default value of 8000 tokens.
                else:
                    per_tool_token_limit = 8_0000
                    for msg in reversed(self.messages):
                        if instance(msg, ToolMessage) and self.calculate_tokens(msg.content) > per_tool_token_limit:
                            self.save_tool_result(msg)
                            msg.content = f"This tool call result has been collapsed due to token size constraints. \n Tool Call ID : {msg.tool_call_id} : use this Tool Call ID to retrieve the tool call result using collapsed_tool_results."



        token_usuage = self.count_tokens()
        if self.compression_token_limit is not None and token_usuage > self.compression_token_limit and self.agent is not None and self.compression_prompt is not None:
            self.messages.append(HumanMessage(self.compression_prompt))
            compression_report = self.agent.invoke(self, self_append=False).content     # It takes the Thread and self append false which means that the agent will not append this response into the thread and the new thread will start now because the token limit of the messages is more than the compression token limit.
            self.messages.pop()  # Remove the last human message which takes the compression prompt.


            # From here we will build a new thread with the compression-report and the system prompt.
            new_thread = self.__copy__()
            self.child = new_thread
            new_thread.parent = self
            root = self.root if self.root is not None else self
            new_thread.root = root
            root.tail = new_thread

            new_thread.messages = []
            # Now add the messages to the new thread which is system prompt and the compression report as the HumanMessage.
            if len(root.messages) > 0 and isinstance(root.messages[0], SystemMessage):
                new_thread.append(root[0])    # Here we have used __getitem__ magic function to get the message at that particular index.
            
            new_thread.append(HumanMessage(compression_report))


    # To make the new thread instance.
    def __copy__(self):
        new_instance = Thread()
        return new_instance


    # To get the message at the particular index.
    def __getitem__(self, index):
        if self.tail is not None:
            return self.tail.messages[index]

        else:
            self.messages[index]


