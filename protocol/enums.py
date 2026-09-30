from django.db import models
from a2a.utils import TransportProtocol

class TransportProtocolChoices(models.TextChoices):
    HTTP_JSON = TransportProtocol.HTTP_JSON.value
    JSONRPC = TransportProtocol.JSONRPC.value
    GRPC = TransportProtocol.GRPC.value
