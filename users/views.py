import random
import uuid
import os

from fastapi.responses import JSONResponse, FileResponse
from fastapi import Request

from manage import app
from users.form import Login, Regist, UpdatePassword
from common.mail import send_mail_code, send_mail_reset
from common.redis import redis_client
from common.jwt_tools import gen_mail_token, gen_token, check_token

from common.mongodb import mongodb, get_groups
from common.password import gen_password
from common.qiniu_storage import generate_upload_token
from common.response import success_response
from config import BASE_DIR


@app.get('/users/groups')
async def get_user_groups():
    groups = await get_groups()
    return success_response(groups)


@app.get('/users/upload/token')
async def upload_token():
    return success_response({"token": generate_upload_token()})


@app.get('/users/get_mail_code')
async def send_email(email: str):
    code = f'{random.randint(100000,999999):06}'
    redis_client.set(f'{email}_code', code, ex=300)
    send_mail_code(email, code)
    return success_response({'email_code': code})


@app.post('/users/login')
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
    response = JSONResponse(content=success_response({'token': token}))
    response.set_cookie('token', token, max_age=7200)
    return response


@app.post('/users/regist')
async def regist(data: Regist):
    if data.password != data.password_ensure:

        return {
            'code': 400,
            'message': "密码不匹配"
        }
    email_code = redis_client.get(f'{data.email}_code')
    if not email_code or email_code != data.email_code:
        return {
            'code': 400,
            'message': "验证码不正确"
        }
    if data.group not in await get_groups():
        return {
            'code': 400,
            'message': "分组不存在"
        }
    user_exits = await mongodb.users.find_one({'email': data.email})
    if user_exits:
        return {
            'code': 400,
            'message': "用户已存在"
        }
    userinfo = {
        '_id': str(uuid.uuid4()),
        'email': data.email,
        'name': data.name,
        'password': gen_password(data.password),
        'group': data.group
    }
    await mongodb.users.insert_one(userinfo)
    del userinfo['password']
    token = gen_token(userinfo)
    response = JSONResponse(content=success_response({'token': token}))
    response.set_cookie('token', token, max_age=7200)
    return response


@app.get('/users/reset_password')
async def reset_password(email: str):
    token = gen_mail_token({'email': email})
    send_mail_reset(email, token)
    return success_response({'token': token})


@app.post('/users/update_password')
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
                                   {'$set': {'password': gen_password(data.password)}})
    userinfo = await mongodb.users.find_one({'email': userinfo['email']}, {'password': 0})

    token = gen_token(userinfo)
    response = JSONResponse(content=success_response({'token': token}))
    response.set_cookie('token', token, max_age=7200)
    return response


@app.post("/users/files")
async def create_upload_file(request: Request):
    form = await request.form()
    file = form.get('file')
    key = str(uuid.uuid4())
    data = await file.read()
    with open(os.path.join(BASE_DIR, f'static/images/{key}'), 'wb') as f:
        f.write(data)
    return success_response({'key': key})


@app.get('/static/{filepath:path}')
async def get_file(filepath: str):
    response = FileResponse(os.path.join(BASE_DIR, 'static', filepath),
                            headers={'content-type': 'image/png'})
    return response
