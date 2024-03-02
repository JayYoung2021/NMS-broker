import asyncio

import redis
from fastapi import APIRouter, Depends

import schemas
from crud.node_groups import read_node_group_by_name
from crud.nodes import read_node_by_name
from database import RpcClient
from dependencies import get_redis

router = APIRouter(
    prefix='/commands',
    tags=['commands'],
)


async def make_rpc_call(
        node: schemas.Node,
        method: str,
        params: dict
) -> dict:
    async with RpcClient(host=node.server, port=node.port) as rpc:
        return await rpc.call({
            'method': method,
            'params': params
        })


async def make_rpc_calls_to_nodes_in_group(
        name: str,
        method: str,
        params: dict,
        r: redis.Redis
) -> list:
    group: schemas.NodeGroup = read_node_group_by_name(name, r)
    tasks: list = []
    for node_name in group.node_names:
        node: schemas.Node = read_node_by_name(node_name, r)
        tasks.append(make_rpc_call(node, method, params))
    return await asyncio.gather(*tasks)


@router.post('/curl')
async def curl(body: schemas.CurlBody, r: redis.Redis = Depends(get_redis)):
    return await make_rpc_calls_to_nodes_in_group(
        body.name,
        'curl',
        {'url': body.url},
        r
    )


@router.post('/drill')
async def drill(body: schemas.DrillBody, r: redis.Redis = Depends(get_redis)):
    return await make_rpc_calls_to_nodes_in_group(
        body.name,
        'drill',
        {'host': body.host},
        r
    )


@router.post('/mtr')
async def mtr(body: schemas.MtrBody, r: redis.Redis = Depends(get_redis)):
    return await make_rpc_calls_to_nodes_in_group(
        body.name,
        'mtr',
        {'host': body.host},
        r
    )


@router.post('/nc')
async def nc(body: schemas.NcBody, r: redis.Redis = Depends(get_redis)):
    return await make_rpc_calls_to_nodes_in_group(
        body.name,
        'nc',
        {'host': body.host, 'port': body.port},
        r
    )


@router.post('/ping')
async def ping(body: schemas.PingBody, r: redis.Redis = Depends(get_redis)):
    return await make_rpc_calls_to_nodes_in_group(
        body.name,
        'ping',
        {'host': body.host, 'count': body.count},
        r
    )
