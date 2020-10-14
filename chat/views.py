from typing import List, Optional
import json
import uuid
import time
import os
from html import escape

from fastapi import Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.websockets import WebSocketDisconnect, WebSocket

from common.mongodb import mongodb
from common.jwt_tools import check_token
from config import BASE_DIR

from manage import app


@app.get("/")
async def get(token: Optional[str] = Cookie(None)):
    if token:
        is_valid, user = check_token(token)
        if not is_valid:
            return RedirectResponse('/login_page')
        f = open(os.path.join(BASE_DIR, 'html/index.html'))
        html = f.read()
        f.close()
        return HTMLResponse(html)

    return RedirectResponse('/login_page')


@app.get('/login_page')
async def login_page():
    f = open(os.path.join(BASE_DIR, 'html/login.html'))
    html = f.read()
    f.close()
    return HTMLResponse(html)


@app.get('/users/reset_password_page')
async def reset_password_page():
    f = open(os.path.join(BASE_DIR, 'html/reset_password.html'))
    html = f.read()
    f.close()
    return HTMLResponse(html)


@app.get('/regist_page')
async def regist_page():
    f = open(os.path.join(BASE_DIR, 'html/regist.html'))
    html = f.read()
    f.close()
    return HTMLResponse(html)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.websocket_info = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        cookies = websocket.cookies
        token = cookies.get('token', '')
        is_valid, userinfo = check_token(token)
        if not is_valid:
            data = {'message': {'type': "sys", 'code': 401, 'content': '未登录'}}
            await websocket.send_text(json.dumps(data, ensure_ascii=True))
            return False
        else:
            self.active_connections.append(websocket)
            self.websocket_info[id(websocket)] = userinfo
            return True

    def get_userinfo(self, websocket: WebSocket):
        return self.websocket_info.get(id(websocket), {})

    def disconnect(self, websocket: WebSocket):
        if id(websocket) in self.websocket_info:
            del self.websocket_info[id(websocket)]
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    ok = await manager.connect(websocket)
    if not ok:
        await websocket.close()
        return ''
    userinfo = manager.get_userinfo(websocket)
    try:
        count = mongodb.messages.count()-20
        last_10_msgs = mongodb.messages.find({}).offset(
            count).sort([('time', -1)]).limit(30)
        async for msg in last_10_msgs:
            await websocket.send_text(json.dumps(msg))
        while True:
            data = await websocket.receive_text()
            json_data = json.loads(data)
            json_data['content'] = escape(json_data['content'])

            message = {'_id': str(uuid.uuid4()),
                       'time': time.time()*1000,
                       'message': json_data,
                       'userinfo': userinfo}
            await mongodb.messages.insert_one(message)
            await manager.broadcast(json.dumps(message))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # await manager.broadcast(f"Client left the chat")
