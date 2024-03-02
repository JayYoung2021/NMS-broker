from fastapi import FastAPI

from routers import nodes, node_groups, commands

app = FastAPI()
app.include_router(nodes.router)
app.include_router(node_groups.router)
app.include_router(commands.router)
