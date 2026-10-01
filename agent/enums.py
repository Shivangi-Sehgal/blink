from db.models import models

class LLMProvider(models.TextChoices):
    OPENAI = "openai", "OpenAI"
    OPENAI_COMPATIBLE = "openai-compatible", "OpenAI Compatible"
    OPEN_ROUTER = "open-router", "OpenRouter"

class ServerTransport(models.TextChoices):
    STDIO = "stdio"
    HTTP = "http"