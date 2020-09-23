from hashlib import md5

from config import JWT_SECRET


def gen_password(white):
    gener = md5()
    gener.update(f'{white}{JWT_SECRET}'.encode())

    black = gener.hexdigest()

    return black
