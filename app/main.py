from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates

# locate templates
templates = Jinja2Templates(directory="templates")

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data):
        for connection in self.active_connections:
            await connection.send_json(data)


manager = ConnectionManager()


@app.get("/")
def get_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@app.websocket("/api/chat/{client_id}")
async def chat(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    response = {
        "sender": client_id,
        "message": "got connected"
    }
    await manager.broadcast(response)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        response['message'] = "left"
        await manager.broadcast(response)
