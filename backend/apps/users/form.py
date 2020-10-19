import uuid
from typing import Optional

from pydantic import BaseModel

from backend.lib.form import fields, form
from backend.common.password import gen_password
from backend.common.redis import redis
from backend.common.mongodb import mongodb


class Login(BaseModel):
    email: str
    password: Optional[str] = None


class Regist(BaseModel):
    name: str
    email: str
    password: str
    password_ensure: str
    email_code: str
    group: str


class ResetPassword(BaseModel):
    email: str


class UpdatePassword(BaseModel):
    password: str
    password_ensure: str
    token: str


class UserRegistForm(form.BaseForm):
    name = fields.CharField(min_length=2, max_length=16)
    email = fields.RegexField(regex=r'[^@]+@[^@]+')
    password = fields.CharField(min_length=8, max_length=16)
    password_ensure = fields.CharField(min_length=8, max_length=16)
    email_code = fields.CharField(max_length=6, min_length=6)
    group = fields.CharField()

    async def validate(self, validated_data):
        password = validated_data['password']
        password_ensure = validated_data['password_ensure']
        if password != password_ensure:
            raise form.ValidationError('密码不匹配')
        key = f'{validated_data["email"]}_code'
        email_code = redis.get(key)
        request_email_code = validated_data['email_code']
        if not email_code or email_code != request_email_code:
            raise form.ValidationError('验证码不争取')
        user_exits = await mongodb.users.find_one(
            {'email': validated_data['email']},
            {'_id': 1})
        if user_exits:
            raise form.ValidationError('用户已经存在')
        return validated_data

    async def create(self, validated_data):
        userinfo = {
            '_id': str(uuid.uuid4()),
            'email': validated_data['email'],
            'name': validated_data['name'],
            'password': gen_password(validated_data['password']),
            'group': validated_data['group']
        }
        await mongodb.users.insert_one(userinfo)
        return userinfo
