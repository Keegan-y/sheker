import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WEB_SERVER_DOMAIN = "https://www.mering.live"
WEB_SERVER_DOMAIN = "http://localhost:8000"
RESET_PASSOWD_PAGE_URL = "/users/reset_password_page"

MAIL_HOST = 'smtp.qq.com'
MAIL_PORT = 587
MAIL_SENDER = '772775481@qq.com'
MAIL_CODE = 'hqexhbhjqylebfaa'

MAIL_EX = 300


REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
MONGO_DBNAME = 'chat'


JWT_SECRET = 'd0823190bd8601f0b693c6c644b31c3bc46ca722eabd755a115a643e0ec46e78'
JWT_AL = 'HS256'
JWT_EX = 60*60*24*7


QINIU_ACCESS_KEY = 'vtT_LwBjGgt5JGL-bP6im1tldGcZwOGHRNdyWUFp'
QINIU_SECRET_KEY = 'b5DQrYLidafU-u0oI_NygoTunyZgDHuD7ptFKimf'
QINIU_BUCKET_NAME = 'hmnew'
QINIU_TOKEN_EXPIRE = 3600
