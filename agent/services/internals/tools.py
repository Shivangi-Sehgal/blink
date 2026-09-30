from agent.services.thread import Thread
from langchain_core.tools import tool



class InternalTools:
    @classmethod
    def tool(cls):
        @tool("collapsed_tool_results", description="Fetch the old collapsed tool result using the tool call id")
        async def collapsed_tool_result(tool_call_id: str) -> str:
            file_path = Thread.get_tool_result_path() / tool_call_id

            try:
                return file_path.read_text(encoding="utf-8")
            except Exception as e:
                raise str(e)