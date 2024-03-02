import redis
from fastapi import APIRouter, Depends

import crud.node_groups
from dependencies import get_redis
from schemas import NodeBase
from schemas import NodeGroup

router = APIRouter(
    prefix='/node-groups',
    tags=["node-groups"],
)


@router.post('/')
async def create_group(group: NodeGroup, r: redis.Redis = Depends(get_redis)):
    crud.node_groups.create_group(group.name, r)


@router.get('/', response_model=list[NodeGroup])
async def read_node_groups(r: redis.Redis = Depends(get_redis)):
    return crud.node_groups.read_groups(r)


@router.delete('/{name}')
async def delete_node_group(name: str, r: redis.Redis = Depends(get_redis)):
    crud.node_groups.delete_group_by_name(name, r)


@router.post('/{group_name}/nodes')
async def add_node(group_name: str, node: NodeBase, r: redis.Redis = Depends(get_redis)):
    crud.node_groups.add_node(group_name, node.name, r)


@router.delete('/{group_name}/nodes')
async def remove_node(group_name: str, node: NodeBase, r: redis.Redis = Depends(get_redis)):
    crud.node_groups.remove_node(group_name, node.name, r)
