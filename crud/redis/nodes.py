import json

import redis

from schemas import Node
from .relational_db import nodes as relational_db

EXPIRE_TIME_IN_SECONDS: int = 1800


def create_node(node: Node, r: redis.Redis) -> None:
    relational_db.create_node(node)
    r.set(f'node:{node.name}', node.json(), EXPIRE_TIME_IN_SECONDS)


def read_nodes( r: redis.Redis) -> list[Node]:
    nodes: list[Node] = relational_db.read_nodes()
    for node in nodes:
        r.set(f'node:{node.name}', node.json(), EXPIRE_TIME_IN_SECONDS)
    return nodes


def delete_node_by_name(name: str, r: redis.Redis) -> None:
    relational_db.delete_node_by_name(name)
    r.delete(f'node:{name}')


def read_node_by_name(name: str, r: redis.Redis) -> Node | None:
    if r.exists(f'node:{name}'):
        x: str = r.get(f'node:{name}')
        y: dict = json.loads(x)
        return Node(**y)
    node: Node | None = relational_db.read_node_by_name(name)
    if node is None:
        return None
    r.set(f'node:{node.name}', node.json(), EXPIRE_TIME_IN_SECONDS)
    return node
