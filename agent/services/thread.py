import json
import tiktoken
from pathlib import Path
from typing import List, Dict, Optional, Union
from agent.services.rules import ToolHideRule, AutoToolHideRule
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

        # If the messages are provided then we will find out the system message index and if it is not at the starting position then we will raise an error.
        if messages is not None:
            index = self._find_system_message(messages)
            if index == -1 or index == 0:
                self.messages = messages
            else:
                raise ValueError(
                    f"System prompt is not at the starting position, it was found at {index} index."
                )

        # If system prompt is provided then we will find out the system message index and make the changes accordingly.
        if self.system_prompt is not None:
            index = self._find_system_message(self.messages)
            if isinstance(self.system_prompt, str):
                self.system_prompt = SystemMessage(self.system_prompt)

            if index == 0:
                if len(messages) == 0:
                    self.append(self.system_prompt)
                else:
                    self.messages[0] = self.system_prompt
            elif index == -1:
                self.messages = [self.system_prompt] + self.messages
            else:
                pass


    # To find the system message index.
    def _find_system_message(self, messages: List[Union[SystemMessage, HumanMessage, AIMessage, ToolMessage]]):
        for i in range(len(messages)):
            if isinstance(messages[i], SystemMessage):
                return i

        return -1

    # To get the path where the tool result has been saved after the ToolHideRules has been applied.
    @classmethod
    def get_tool_result_path(cls):
        path = Path.cwd() / "tool_results"
        path.mkdir(parents=True, exist_ok=True)
        return path


    # To save the tool result on that particular path after applying the ToolHideRules.
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


    # To append the message to the Thread.
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



        # This code block is for the compression of the messages and making the new thread with the compression report.
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
                new_thread.append(root.messages[0])    # Here we have used __getitem__ magic function to get the message at that particular index.
            
            new_thread.append(HumanMessage(compression_report))

        else:
            self.messages.append(message)


    # To count the number of SystemMessage, AIMessage, ToolMessage, HumanMessage in the Thread.
    def count(self):
        counts = {
            "Depth": 0,
            "System": 0,
            "AI": 0,
            "Tool": 0,
            "Human":0,
        }

        thread = self
        depth = 0

        if isinstance(thread.messages[0], SystemMessage):
            counts["System"] = 1

        while True:
            for msg in thread:
                if isinstance(msg, AIMessage):
                    counts["AI"] += 1

                elif isinstance(msg, ToolMessage):
                    counts["Tool"] += 1

                elif isinstance(msg, HumanMessage):
                    counts["Human"] += 1

                else:
                    pass
            
            if thread.child is None:
                break

            else:
                thread = thread.child
                depth += 1

        counts["Depth"] = depth
        return counts


    # To make the new thread instance.
    def __copy__(self):
        new_instance = Thread()
        return new_instance


    # To append the message to the thread using the pipe operator.
    def __ror__(self, other: Union[SystemMessage, AIMessage, ToolMessage, HumanMessage]):
        if self.tail is not None:
            self.tail.append(other)
        else:
            self.append(other)

    # To get the message at the particular index.
    def __getitem__(self, index):
        if self.tail is not None:
            return self.tail.messages[index]

        else:
            return self.messages[index]


    # To set the message at the particular index.
    def __setitem__(self, index, value):
        if self.tail is not None:
            self.tail.messages[index] = value

        else:
            self.messages[index] = value


    # To get the length of the thread messages.
    def __len__(self):
        if self.tail is not None:
            return len(self.tail.messages)

        else:
            return len(self.messages)

    # To iterate over the messages in the Thread.
    def __iter__(self):
        if self.tail is not None:
            for msg in self.tail.messages:
                yield msg
        else:
            for msg in self.messages:
                yield msg

    # To return the count of SystemMessage, AIMessage, Toolmessage, HumanMessage in the Thread.
    def __str__(self):
        counts = self.count()
        return json.dumps(counts, indent=4)

    # To return the count of SystemMessage, AIMessage, ToolMessage, HumanMessage in the Thread.
    def __repr__(self):
        counts = self.count()
        return json.dumps(counts, indent=4)