from typing import Optional, List, Union, Any
from langchain_openai import ChatOpenAI
from langchain_openrouter import ChatOpenRouter
from pydantic import SecretStr
from agent.enums import LLMProvider
from agent.models import LLMConfig


class LLM:
    def __init__(
        self,
        provider: LLMProvider,
        model: str,
        base_url: Optional[str] = None,
        api_key = Optional[str] = None,
    ):
        self.provider = provider
        self.model = model
        self.base_url = base_url
        self.api_key = api_key


    @classmethod
    def from_config(clas, config: LLMConfig):
        return cls(
            provider = LLMProvider(config.provider),
            model = config.model,
            base_url = config.base_url,
            api_key = config.api_key,
       )

    def connect(self):
        api_key = SecretStr(self.api_key) if self.api_key is not None else None

        if self.provider == LLMProvider.OPENAI:
            return ChatOpenAI(
                model=self.model,
                api_key=api_key,
            )

        elif self.provider == LLMProvider.OPENAI_COMPATIBLE:
            return ChatOpenRouter(
                model=self.model,
                base_url=self.base_url,
                api_key=self.api_key,
            )
        
        elif self.provider == LLMProvider.OPEN_ROUTER:
            return ChatOpenRouter(
                model=self.model,
                api_key=self.api_key,
            )

        else:
            raise ValueError(f"Unsupported Provider: {self.provider}")