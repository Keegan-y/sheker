import json
from datetime import datetime

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import Response


app = FastAPI()


@app.api_route('/', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD'])
async def index(request: Request):

    data = {
        'method': request.method,
        'url': request.url._url,
        'query_params': {key: value for key, value in request.query_params.items()},
        'headers': {key: value for key, value in request.headers.items()},
        'body': (await request.body()).decode(),
        'cookies': {key: value for key, value in request.cookies.items()}
    }

    response = Response(json.dumps(data),
                        200,
                        {'Content-Type': 'application/json'})

    response.set_cookie('datetime-now',
                        datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'),
                        expires=60*60*48)
    return response


@app.get('/html')
async def html():
    html_str = """

    <html>
    <head>
    </head>
    <body>
你好，我是中文
    </body>
    </html>
    """
    resp = Response(html_str, headers={
                    'Content-Type': 'text/html;charset=gbk'})
    return resp
