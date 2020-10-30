import random
import uuid
import os

from fastapi.responses import JSONResponse
from fastapi import Request, APIRouter

from backend.common.mongodb import mongodb
from backend.common.mail import send_mail_code, send_mail_reset
from backend.common.jwt_tools import gen_mail_token, gen_token, check_token
from backend.common.password import gen_password
from backend.common.qiniu_storage import generate_upload_token
from backend.common.response import success_response, error_response
from backend.config import BASE_DIR

from backend.apps.users.form import (Login, UpdatePassword, UserRegistForm)
from backend.common.redis import redis

app = APIRouter()


@app.get('/groups')
async def get_user_groups():
    cursor = mongodb.groups.find()
    datas = []
    async for item in cursor:
        datas.append(item['name'])
    return datas


@app.get('/upload/token')
async def upload_token():
    return success_response({"token": generate_upload_token()})


@app.get('/get_mail_code')
async def send_email(email: str):
    code = f'{random.randint(100000,999999):06}'
    redis.set(f'{email}_code', code, ex=300)
    # send_mail_code(email, code)
    return success_response({'email_code': code})


@app.post('/login')
async def login(data: Login):
    print(data)
    user = await mongodb.users.find_one(
        {
            'email': data.email,
            'password': gen_password(data.password)
        }, {'password': 0})
    if not user:
        return {
            'code': 400,
            'message': '用户名或密码错误',
        }
    token = gen_token(user)
    content = success_response({'token': token})
    response = JSONResponse(content=content)
    response.set_cookie('token', token, max_age=7200)
    return response


@app.post('/regist')
async def regist(data: Request):
    form = UserRegistForm(data=await data.json())
    if await form.is_valid():
        user = await form.create(form.validated_data)
        del user['password']
        token = gen_token(user)
        content = success_response({'token': token})
        response = JSONResponse(content=content)
        response.set_cookie('token', token, max_age=7200)
        return response

    return {
        'code': 400,
        'message': form.errors
    }


@app.post('/update_info')
async def update_info(data: Request):
    json_data = await data.json()
    name = json_data.get('name', None)
    if not name:
        return error_response(message='参数不合法')
    token = data.cookies.get('token')
    is_valid, userinfo = check_token(token)
    if not is_valid:
        return error_response(message="未登录")
    await mongodb.users.update_one({'_id': userinfo['_id']}, {'$set': {'name': name}})
    response = JSONResponse({'code': 0})
    userinfo['name'] = name
    token = gen_token(userinfo)
    response.set_cookie('token', token, max_age=7200)
    return response


@app.get('/reset_password')
async def reset_password(email: str):
    token = gen_mail_token({'email': email})
    send_mail_reset(email, token)
    return success_response({'token': token})


@app.post('/update_password')
async def update_password(data: UpdatePassword):
    is_valid, userinfo = check_token(data.token)
    if not is_valid:
        return {
            'code': 400,
            'message': "链接已失效"
        }
    if data.password != data.password_ensure:
        return {
            'code': 400,
            'message': "密码不匹配"
        }
    await mongodb.users.update_one({'email': userinfo['email']},
                                   {'$set': {'password':
                                             gen_password(data.password)}})
    userinfo = await mongodb.users.find_one({'email': userinfo['email']},
                                            {'password': 0})

    token = gen_token(userinfo)
    content = success_response({'token': token})
    response = JSONResponse(content=content)
    response.set_cookie('token', token, max_age=7200)
    return response


@app.post("/files")
async def create_upload_file(request: Request):
    form = await request.form()
    file = form.get('file')
    key = str(uuid.uuid4())
    data = await file.read()
    path = os.path.join(BASE_DIR, f'static/images/{key}')
    with open(path, 'wb') as f:
        f.write(data)
    return success_response({'key': key})
