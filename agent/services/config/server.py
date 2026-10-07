from typing import Dict, Any, Optional, Union
from agent.enums import ServerTransport
from agent.models import MCPServerConfig

class Server:

    def __init__(
        self,
        name: str,
        transport: ServerTransport,
        url: Optional[str] = None,
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.transport = transport
        self.url = url
        self.command = command
        self.args = args
        self.env = env

    @classmethod
    def from_config(cls, config: MCPServerConfig):
        return cls(
            name = config.name,
            transport = ServerTransport(config.transport),
            url = config.url,
            command = config.command,
            args = config.args,
            env = config.env,
        )

    def dump_json(self):
        config = {}
        config["transport"] = self.transport
        if self.env is not None:
            config['env'] = self.env

        match self.transport:
            case ServerTransport.HTTP:
                config["url"] = self.url
            case ServerTransport.STDIO:
                config["command"] = self.command
                config["args"] = self.args

        return config
        
             

