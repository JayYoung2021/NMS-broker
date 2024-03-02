import json

import redis

from schemas import NodeGroup
from .relational_db import node_groups as relational_db

EXPIRE_TIME_IN_SECONDS: int = 1800


def create_group(name: str, r: redis.Redis) -> None:
    relational_db.create_group(name)
    r.set(f'group:{name}', NodeGroup(name=name).json(), EXPIRE_TIME_IN_SECONDS)


def read_groups(r: redis.Redis) -> list[NodeGroup]:
    groups: list[NodeGroup] = relational_db.read_groups()
    for group in groups:
        r.set(f'group:{group.name}', group.json(), EXPIRE_TIME_IN_SECONDS)
    return groups


def delete_group_by_name(name: str, r: redis.Redis) -> None:
    relational_db.delete_group_by_name(name)
    r.delete(f'group:{name}')


def add_node(group_name: str, node_name: str, r: redis.Redis) -> None:
    relational_db.add_node(group_name, node_name)
    if r.exists(f'group:{group_name}'):
        x: str = r.get(f'group:{group_name}')
        y: dict = json.loads(x)
        if node_name in y['nodes']:
            return None
        y['nodes'].append(node_name)
        r.set(f'group:{group_name}', json.dumps(y), EXPIRE_TIME_IN_SECONDS)


def remove_node(group_name: str, node_name: str, r: redis.Redis) -> None:
    relational_db.remove_node(group_name, node_name)
    if r.exists(f'group:{group_name}'):
        x: str = r.get(f'group:{group_name}')
        y: dict = json.loads(x)
        if node_name not in y['nodes']:
            return None
        y['nodes'].remove(node_name)
        r.set(f'group:{group_name}', json.dumps(y), EXPIRE_TIME_IN_SECONDS)


def read_node_group_by_name(name: str, r: redis.Redis) -> NodeGroup | None:
    if r.exists(f'group:{name}'):
        x: str = r.get(f'group:{name}')
        y: dict = json.loads(x)
        return NodeGroup(**y)
    group: NodeGroup | None = relational_db.read_group_by_name(name)
    if group is None:
        return None
    with redis.Redis(decode_responses=True) as r:
        r.set(f'group:{name}', group.json(), EXPIRE_TIME_IN_SECONDS)
    return group
