from qiniu import Auth
from qiniu import put_data
import requests

from config import QINIU_ACCESS_KEY, QINIU_SECRET_KEY, QINIU_BUCKET_NAME, QINIU_TOKEN_EXPIRE


def generate_upload_token():
    """
    七牛云上传文件
    :param data: 上传的二进制数据
    :return: 七牛云上的文件名
    """

    # 需要填写你的 Access Key 和 Secret Key
    access_key = QINIU_ACCESS_KEY
    secret_key = QINIU_SECRET_KEY
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = QINIU_BUCKET_NAME

    # 上传后保存的文件名
    key = None  # 如果设置为None, 七牛云会自动给文件起名(hash值)

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, QINIU_TOKEN_EXPIRE)
    return token


def upload_file(stream):
    token = generate_upload_token()
    # resp = requests.post('http://up-z2.qiniup.com/', data={
    #     'token': token,
    #     'file': stream
    # })
    # import ipdb
    # ipdb.set_trace()
    ret, info = put_data(token, key=None, data=stream)
    return ret['key']
