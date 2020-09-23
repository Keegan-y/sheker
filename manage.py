
import importlib
from fastapi import FastAPI


app = FastAPI()

importlib.import_module('chat.views')
importlib.import_module('users.views')
# from chat import views
# from users import views