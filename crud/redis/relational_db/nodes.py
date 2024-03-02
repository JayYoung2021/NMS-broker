import requests

from schemas import Node
from .utils import find


def _get_node_id_by_name(name: str) -> int | None:
    url: str = f'http://localhost:1337/api/nodes?filters[name][$eq]={name}'
    data: list[dict] = find(url)
    if len(data) == 0:
        return None
    return data[0]['id']


def _node_exists(name: str) -> bool:
    return _get_node_id_by_name(name) is not None


def create_node(node: Node) -> None:
    if _node_exists(node.name):
        raise Exception(f"Node with name {node.name} already exists")

    url: str = f'http://localhost:1337/api/nodes'
    requests.post(url, json={'data': node.dict()})


def read_nodes() -> list[Node]:
    url: str = f'http://localhost:1337/api/nodes'
    data: list[dict] = find(url)
    return [
        Node(
            name=x['attributes']['name'],
            server=x['attributes']['server'],
            port=x['attributes']['port'],
        ) for x in data
    ]


def delete_node_by_name(name: str) -> None:
    id_: int | None = _get_node_id_by_name(name)
    if id_ is None:
        return

    url: str = f'http://localhost:1337/api/nodes/{id_}'
    requests.delete(url)


def read_node_by_name(name: str) -> Node | None:
    if not _node_exists(name):
        return None

    url: str = f'http://localhost:1337/api/nodes?filters[name][$eq]={name}'
    data: list[dict] = find(url)
    attributes: dict = data[0]['attributes']
    return Node(
        name=attributes['name'],
        server=attributes['server'],
        port=attributes['port'],
    )
