import json
from typing import List
from collections import defaultdict

from fastapi import WebSocket

from backend.common.jwt_tools import check_token


class ConnectionManager:
    def __init__(self):
        self.groups = defaultdict(list)
        self.active_connections: List[WebSocket] = []

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
            group_name = userinfo['group']
            self.groups[group_name].append(websocket)
            setattr(websocket, 'group', group_name)
            return userinfo

    def disconnect(self, websocket: WebSocket):
        self.groups[websocket.group].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, group, message: str):
        for connection in self.groups[group]:
            await connection.send_text(message)


manager = ConnectionManager()
