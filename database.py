import asyncio
import uuid
from typing import MutableMapping

import orjson
from aio_pika import Message, connect
from aio_pika.abc import AbstractChannel
from aio_pika.abc import AbstractConnection
from aio_pika.abc import AbstractIncomingMessage
from aio_pika.abc import AbstractQueue


class RpcClient:
    connection: AbstractConnection
    channel: AbstractChannel
    callback_queue: AbstractQueue
    loop: asyncio.AbstractEventLoop

    def __init__(
            self,
            host: str,
            port: int
    ) -> None:
        self._host: str = host
        self._port: int = port

        self.futures: MutableMapping[str, asyncio.Future] = {}
        self.loop = asyncio.get_running_loop()

    async def connect(self) -> "RpcClient":
        self.connection = await connect(
            host=self._host,
            port=self._port,
            loop=self.loop
        )
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_response, no_ack=True)

        return self

    def on_response(self, message: AbstractIncomingMessage) -> None:
        if message.correlation_id is None:
            print(f"Bad message {message!r}")
            return

        future: asyncio.Future = self.futures.pop(message.correlation_id)
        future.set_result(message.body)

    async def call(self, request: dict) -> dict:
        correlation_id = str(uuid.uuid4())
        future = self.loop.create_future()

        self.futures[correlation_id] = future

        # message: any -> body: bytes
        body: bytes = orjson.dumps(request)

        await self.channel.default_exchange.publish(
            Message(
                body,
                content_type='application/octet-stream',
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key="rpc_queue",
        )

        x: bytes = await future  # TODO
        return orjson.loads(x)

    async def __aenter__(self) -> "RpcClient":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is not None:
            print(f"Exception caught: {exc_type!r}, {exc_value!r}")

        await self.connection.close()
