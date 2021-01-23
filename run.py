from WebLamp import printc as log, Colors
from server import run
import asyncio
import shutil
import config
import cache
import time
import os

# if x == f'{p}beatmaps': # or x == f'{p}replays':
#     shutil.rmtree(x)

os.chdir(os.path.dirname(os.path.realpath(__file__))) # sets our director in the console to /rain
p = './data' 

if not os.path.exists(p):
    os.mkdir(p)
p += '/'
for x in (f'{p}replays', f'{p}beatmaps', f'{p}screenshots', f'{p}avatars'):
    if not os.path.exists(x):
        os.mkdir(x)
        if x == f'{p}avatars': print('Get a default profile picture and save it as "-1.png"')

PING_TIMEOUT = 300
async def inactive():
    """
    This will check if our player is pretty
    much off the game, and if are, we will remove
    them from the cache.
    """
    while True:
        await asyncio.sleep(10)
        for p in list(cache.online):
            p = cache.online[p]
            if p.userid == 3:
                continue
            
            if p.pingtime and time.time() - p.pingtime > PING_TIMEOUT:
                log(f'{p.username} has logged off!', Colors.Blue)
                del cache.online[p.userid]

run(
    config.socket_type, uvloop = True, debug = True, dtasks = [inactive]
)