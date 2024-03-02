import requests

from schemas import NodeGroup
from .nodes import _get_node_id_by_name
from .utils import find


def _get_group_id_by_name(name: str) -> int | None:
    url: str = f'http://localhost:1337/api/node-groups?filters[name][$eq]={name}'
    if len(find(url)) == 0:
        return None
    return find(url)[0]['id']


def _group_exits(name: str) -> bool:
    return _get_group_id_by_name(name) is not None


def create_group(name: str) -> None:
    if _group_exits(name):
        raise Exception(f"Node group with name {name} already exists")

    url: str = f'http://localhost:1337/api/node-groups'
    requests.post(url, json={
        'data': {'name': name}
    })


def read_groups() -> list[NodeGroup]:
    url: str = f'http://localhost:1337/api/node-groups?populate[0]=nodes'
    data: list[dict] = find(url)
    return [
        NodeGroup(
            name=x['attributes']['name'],
            node_names=[
                y['attributes']['name']
                for y in x['attributes']['nodes']['data']
            ]
        ) for x in data
    ]


def delete_group_by_name(name: str) -> None:
    id_: int | None = _get_group_id_by_name(name)
    if id_ is None:
        return None

    url: str = f'http://localhost:1337/api/node-groups/{id_}'
    requests.delete(url)


def add_node(group_name: str, node_name: str) -> None:
    group_id: int | None = _get_group_id_by_name(group_name)
    if group_id is None:
        raise Exception(f"No node group with name {group_name}")

    node_id: int | None = _get_node_id_by_name(node_name)
    if node_id is None:
        raise Exception(f"No node with name {node_name}")

    node_ids: list[int] = [
        y['id']
        for y in find(
            f'http://localhost:1337/api/node-groups?filters[name][$eq]={group_name}&populate[0]=nodes'
        )[0]['attributes']['nodes']['data']
    ]
    if node_id in node_ids:
        return

    node_ids.append(node_id)
    url: str = f'http://localhost:1337/api/node-groups/{group_id}'
    requests.put(url, json={
        'data': {'nodes': node_ids}
    })


def remove_node(group_name: str, node_name: str) -> None:
    group_id: int | None = _get_group_id_by_name(group_name)
    if group_id is None:
        raise Exception(f"No node group with name {group_name}")

    node_id: int | None = _get_node_id_by_name(node_name)
    if node_id is None:
        raise Exception(f"No node with name {node_name}")

    node_ids: list[int] = [
        y['id']
        for y in find(
            f'http://localhost:1337/api/node-groups?filters[name][$eq]={group_name}&populate[0]=nodes'
        )[0]['attributes']['nodes']['data']
    ]
    if node_id not in node_ids:
        return

    node_ids.remove(node_id)
    url: str = f'http://localhost:1337/api/node-groups/{group_id}'
    requests.put(url, json={
        'data': {'nodes': node_ids}
    })


def read_group_by_name(name: str) -> NodeGroup | None:
    if not _group_exits(name):
        return None

    url: str = f'http://localhost:1337/api/node-groups?filters[name][$eq]={name}&populate[0]=nodes'
    data: dict = find(url)[0]
    attributes: dict = data['attributes']
    return NodeGroup(
        name=attributes['name'],
        node_names=[
            x['attributes']['name']
            for x in attributes['nodes']['data']
        ]
    )
