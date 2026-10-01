import uuid
from django.db import models
from agent.enums import LLMProvider, ServerTransport
from encrypted_model_fields.fields import EncryptedCharField

# Create your models here.
class LLMConfig(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=100, choices = LLMProvider.choices, default=LLMProvider.OPENAI_COMPATIBLE)
    model = models.CharField(max_length=100)
    base_url = models.URLField(blank=True, null=True)
    api_key = EncryptedCharField(max_limit=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.dateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.provider} - {self.model}"

class InternalTools(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class MCPServerConfig(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    transport = models.CharField(max_length=10, choices=ServerTransport.choices, default=ServerTransport.HTTP)
    url = models.URLField(blank=True, null=True)
    command = models.CharField(max_length=200, blank=True, null=True)
    args = models.JSONField(blank=True, null=True)
    env = JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ToolHideRuleModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    message = models.TextField(max_length=500)
    server = models.ForeignKey(MCPServerConfig, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.server.name} - {self.name}"

class CompressionPrompt(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    prompt = models.TextField(max_length=3_000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Prompt(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    content = models.TextField(max_length=3_000)
    server = models.ForeignKey(
        MCPServerConfig, 
        on_delete=models.CASCADE, 
        null=True, blank=True, 
        related_name="prompts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class SystemPrompt(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    name = models.CharField(max_length=100, unique=True)
    content = models.TextField(max_length=3_000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    content = models.TextField(max_length=4_000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ThreadConfig(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max-length=100, unique=True)
    system_prompt = models.ForeignKey(SystemPrompt, on_delete=models.DO_NOTHING, blank=True, null=True)
    compression_prompt = models.ForeignKey(CompressionPrompt, on_delete=models.DO_NOTHING, blank=True, null=True)
    compression_token_limit = models.IntegerField(blank=True, null=True)
    tool_hide_rules = models.ManyToManyField(ToolHideRuleModel, blank=True, related_name="thread_configs")
    auto_hide_rule = models.BooleanField(default=False)
    token_limit = models.IntegerField(blank=True, null=True)
    per_tool_token_limit = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name




