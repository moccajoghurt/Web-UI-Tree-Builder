from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from tree_host.actions import tree


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ActionItem(BaseModel):
    id: str
    parent: str | None
    path: list[str]
    title: str
    route: str
    type: str


class DeleteItem(BaseModel):
    id: str


class ConnectionManager:
    """Manage active WebSocket connections and broadcast events."""

    def __init__(self) -> None:
        self.active: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active.discard(websocket)

    async def broadcast(self, message: str) -> None:
        if not self.active:
            return
        to_remove: list[WebSocket] = []
        for ws in list(self.active):
            try:
                if (
                    getattr(ws, "application_state", None) is not None
                    and ws.application_state != WebSocketState.CONNECTED
                ):
                    to_remove.append(ws)
                    continue
                await ws.send_text(message)
            except (RuntimeError, ConnectionError):
                to_remove.append(ws)
        for ws in to_remove:
            self.disconnect(ws)


manager = ConnectionManager()


@app.get("/")
async def index():
    html_content = await tree.load_index()
    return HTMLResponse(content=html_content, media_type="text/html")


@app.post("/update-tree")
async def update(data: ActionItem):
    await tree.update_tree(data.model_dump())
    await manager.broadcast("tree_updated")


@app.post("/delete")
async def delete_node(data: DeleteItem):
    await tree.delete_node({"id": data.id})
    await manager.broadcast("tree_updated")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)
