import uuid
import importlib

from fastapi import FastAPI


from backend.common.mongodb import mongodb
redis_client = None


async def init_groups():
    await mongodb.groups.delete_many({})
    await mongodb.groups.insert_many([
        {
            '_id': str(uuid.uuid4()),
            'name': 'py37',
            'label': '上海 python37 期'
        },
        {
            '_id': str(uuid.uuid4()),
            'name': 'py38',
            'label': '上海 python38 期'
        },
        {
            '_id': str(uuid.uuid4()),
            'name': 'py39',
            'label': '上海 python39 期'
        }
    ])


def init_apps(app: FastAPI):
    users = importlib.import_module('backend.apps.users.views')
    chat = importlib.import_module('backend.apps.chat.views')
    app.include_router(users.app, prefix='/users')
    app.include_router(chat.app)
    for route in app.routes:
        print(route.path)


async def startup():
    await init_groups()


async def get_groups():
    cursor = mongodb.groups.find()
    datas = []
    async for item in cursor:
        datas.append(item['name'])
    return datas


def init_events(app: FastAPI):
    app.on_event('startup')(startup)
    # app.on_event('shutdown')(shutdown)


def create_app():
    app = FastAPI()
    init_events(app)
    init_apps(app)
    return app
