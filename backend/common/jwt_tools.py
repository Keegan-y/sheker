from datetime import datetime, timedelta

import jwt

from backend.config import JWT_AL, JWT_SECRET, JWT_EX, MAIL_EX


def gen_token(data, expire=JWT_EX):
    payload = {
        'exp': datetime.utcnow()+timedelta(seconds=expire)
    }
    payload.update(data)
    data = jwt.encode(payload, key=JWT_SECRET, algorithm=JWT_AL)
    return data.decode()


def check_token(token):
    try:
        data = jwt.decode(token, key=JWT_SECRET, algorithms=JWT_AL)  # 取出的是数据内容
        return True, data
    except jwt.PyJWTError:
        return False, ""


def gen_mail_token(data):
    return gen_token(data, expire=MAIL_EX)
