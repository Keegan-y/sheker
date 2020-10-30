import os

import aiofiles

from backend.config import TEMPLATE_DIR


async def get_template(file_path):
    path = os.path.join(TEMPLATE_DIR, file_path)
    if os.path.isfile(path):
        async with aiofiles.open(path) as f:
            html = await f.read()
            return html
    return None
