import asyncio
import httpx
from a2a.utils import TransportProtocol
from pydantic import Basemodel, Field, ConfigDict
from agent.services.thread import Thread
from langchain_core.tools import tool

class A2ARequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    url: str = Field(..., description="Request URL")
    protocol: TransportProtocol = Field(default=Transportprotocol.JSONRPC, description="Transport protocol")
    text: str = Field(..., description="Query/Message/Text to send to the agent")
    boolean : bool = False

class InternalTools:
    @classmethod
    def tool(cls):      # One place which returns "all the internal tools"
        @tool("collapsed_tool_results", description="Fetch the old collapsed tool result using the tool call id")
        async def collapsed_tool_result(tool_call_id: str) -> str:
            file_path = Thread.get_tool_result_path() / tool_call_id

            try:
                return file_path.read_text(encoding="utf-8")
            except Exception as e:
                raise str(e)

        @tool("a2a_invoke")
        async def a2a_invoke(
            request: A2ARequest
        ):