from django.db import models
from protocol.enums import TransportProtocolChoices

# Create your models here.
class SkillTag(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

class AgentSkillModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    tags = ManyToManyField(SkillTag, related_name='skills')
    examples = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class AgentInterfaceModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.CharField(max_length=20, default="127.0.0.1")
    port = models.IntegerField(default=8000)
    protocol_binding = models.CharField(max_length=100, choices=TransportProtocolChoices, default=TransportprotocolChoices.JSONRPC)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeFiled(auto_now=True)


class AgentCardModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    version = models.CharField(max_length=100, default="0.1.0", blank=True, null=True)
    supported_interfaces = models.ManyToManyField(AgentInterfaceModel, blank=True, related_name="agent_cards")
    streaming = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=False)
    skills = models.manyTomanyField(AgentSkillModel, blank=True, related_name="agent_cards")
    created_at = models.dateTiemField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class AgentExecutorModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_card = models.ForeignKey(AgentCardModel, on_delete=models.DO_NOTHING)