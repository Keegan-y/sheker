import json
import uuid
import time
import os
from html import escape
from typing import Optional

from fastapi import Cookie, APIRouter
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.websockets import WebSocketDisconnect, WebSocket

from backend.common.jwt_tools import check_token
from backend.common.mongodb import mongodb
from backend.common.socket_manager import manager
from backend.common.template import get_template
from backend.config import BASE_DIR

app = APIRouter()


@app.get("/")
async def get(token: Optional[str] = Cookie(None)):
    if token:
        is_valid, user = check_token(token)
        if not is_valid:
            return RedirectResponse('/pages/login')
        html = await get_template('index.html')
        return HTMLResponse(html)

    return RedirectResponse('/pages/login')


@app.get('/pages/{page_name}')
async def get_page(page_name):
    html = await get_template(f'{page_name}.html')
    if html:
        return HTMLResponse(html)
    return HTMLResponse('not found', status_code=404)


@app.get('/update_info_page')
async def update_info():
    html = await get_template('update_info.html')
    return HTMLResponse(html)


@app.get('/login_page')
async def login_page():
    html = await get_template('login.html')
    return HTMLResponse(html)


@app.get('/users/reset_password_page')
async def reset_password_page():
    html = await get_template('reset_password.html')
    return HTMLResponse(html)


@app.get('/regist_page')
async def regist_page():
    html = await get_template('regist.html')
    return HTMLResponse(html)


# @app.post('/upload_file')
# async def upload_file():
#     return success_response()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    userinfo = await manager.connect(websocket)
    if not userinfo:
        await websocket.close()
        return None
    try:
        query = {'userinfo.group': userinfo['group']}
        count = await mongodb.messages.count_documents(query)-30
        if count > 0:
            recent_msgs = mongodb.messages.find(query).skip(count)
        else:
            recent_msgs = mongodb.messages.find(query)
        async for msg in recent_msgs:
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
            await manager.broadcast(userinfo['group'],
                                    json.dumps(message))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # await manager.broadcast(f"Client left the chat")


@app.get('/static/{filepath:path}')
async def get_file(filepath: str):
    path = os.path.join(BASE_DIR, 'static', filepath)
    headers = {'content-type': 'image/png'}
    response = FileResponse(path, headers=headers)
    return response
