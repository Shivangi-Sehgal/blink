from protocol.models import AgentInterfaceModel
from protocol.errors import GetAgentInterfaceError
from a2a.types import AgentInterface
from a2a.utils import TransportProtocol

async def get_agent_interface(agent_interface: AgentInterfaceModel):
    try:
        return AgentInterface(
            url = f"http://{agent_interface.url}:{agent_interface.port}",
            protocol_bindings = TransportProtocol(agent_interface.protocol_binding)
        )
    except Exception as e:
        raise GetAgentInterfaceError(str(e))