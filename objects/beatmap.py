from helpers import BEATMAPS
from aiohttp import request
import config

class Beatmap:
    def __init__(self) -> None:
        ...
    
    @staticmethod
    async def from_md5_to_api(md5: str):
        b = Beatmap()
        url = f'{config.mirror}/api/search/'
        params = {
            
        }
        async with request('GET', url, params = params) as req:
            ...
