import redis
from fastapi import APIRouter, Depends

import crud.nodes
from dependencies import get_redis
from schemas import Node

router = APIRouter(
    prefix='/nodes',
    tags=["nodes"],
)


@router.post('/')
async def create_node(node: Node, r: redis.Redis = Depends(get_redis)):
    crud.nodes.create_node(node, r)


@router.get('/', response_model=list[Node])
async def read_nodes(r: redis.Redis = Depends(get_redis)):
    return crud.nodes.read_nodes(r)


@router.delete('/{name}')
async def delete_node(name: str, r: redis.Redis = Depends(get_redis)):
    crud.nodes.delete_node_by_name(name, r)
