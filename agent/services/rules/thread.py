from pydantic import BaseModel
from typing import Optional

class ToolHideRule(BaseModel):
    name: str
    message: str
class AutoToolhideRule(BaseModel):
    token_limit: int
    per_tool_token_limit: Optional[int] = None