from a2a.types import AgentSkill
from protocol.models import AgentSkillModel
from protocol.errors import GetAgentSkillError

async def get_agent_skill(agent_skill: AgentSkillModel):
    try:
        return AgentSkill(
            id=str(agent_skill.uuid),
            name=agent_skill.name,
            description=agent_skill.description,
            tags = [tag.name for tag in agent_skill.tags.all()],
            examples = [example.content for example in agent_skill.examples.all()],
            input_modes = ["text/plain"],
            output_modes = ["text/plain"],
        )
    except Exception as e:
        raise GetAgentSkillError(str(e))