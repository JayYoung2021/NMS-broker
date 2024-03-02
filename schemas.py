from pydantic import BaseModel, conint


class NodeBase(BaseModel):
    name: str


class Node(NodeBase):
    server: str
    port: conint(ge=1, le=65535)


class NodeGroup(BaseModel):
    name: str
    node_names: list[str] = list()


class CommandBody(BaseModel):
    name: str


class CurlBody(CommandBody):
    url: str


class DrillBody(CommandBody):
    host: str


class MtrBody(CommandBody):
    host: str


class NcBody(CommandBody):
    host: str
    port: conint(ge=1, le=65535)


class PingBody(CommandBody):
    host: str
    count: conint(ge=1) = 10
