from protocol.models import AgentCardModel
from protocol.errors import GetAgentCardError
from protocol.backend.skill import get_agent_skill
from protocol.backend.interface import get_agent_interface
from a2a.types import AgentCard, AgentSkill, AgentInterface, AgentCapabilities

async def get_agent_card(agent_card: AgentCardModel):
    try:
        
        supported_interfaces = []
        skills = []

        for interface in agent_card.supported_interfaces.all():
            agent_interface = get_agent_interface(interface)
            if isinstance(agent_interface, AgentInterface):
                supported_interfaces.append(agent_interface)

        if len(supported_interfaces) <= 0:
            raise GetAgentCardError("No Supported Interfaces Found For Agent Card.")

        for skill in agent_card.skills.all():
            agent_skill = get_agent_skill(skill)
            if isinstance(agent_skill, AgentSkill):
                skills.append(agent_skill)

        return AgentCard(
            name = agent_card.name,
            description = agent_card.description,
            version = agent_card.version,
            supported_interfaces = supported_interfaces,
            capabilities = AgentCapabilities(
                streaming = agent_card.streaming,
                push_notifications = agent_card.push_notifications,
            ),
            default_input_modes = ["text/plain"],
            default_output_modes = ["text/plain"],
            skills = skills,
        )
    except Exception as e:
        raise GetAgentCardError(str(e))