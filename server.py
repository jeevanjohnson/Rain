from WebLamp import Connection
from serverwrapper import OsuServer
from packets import PacketIDS
from typing import Union
from objects.player import Player
import packets
import config
import os
import cache
import aiofiles
import aiotinydb
import time

s = OsuServer()
bancho = ("c.ppy.sh", "c4.ppy.sh", "c5.ppy.sh", "c6.ppy.sh")
web = ["osu.ppy.sh"]
avatar = ["a.ppy.sh"]

loginMsg = '\n'.join([
    " Welcome to Rain!", # cursed
    "This was made for the sole purpose of learning how to make a server.",
    "if your here welcome and enjoy your time.",
    "There are currently {} online users"
])

@s.handler(target = r'^/(?P<userid>[0-9]*)$', domains = avatar)
async def ava(conn: Connection) -> bytes:
    conn.set_status(200)
    userid = int(conn.args['userid'])

    if os.path.exists(f'./data/avatars/{userid}.png'):
        async with aiofiles.open(f'./data/avatars/{userid}.png', 'rb') as f:
            pfp = f.read()
    else:
        async with aiofiles.open(f'./data/avatars/-1.png', 'rb') as f:
            pfp = f.read()
    
    conn.set_body(pfp)
    return conn.response

@s.handler(target = PacketIDS.OSU_LOGOUT, domains = bancho)
async def logout(conn: Connection, p: Union[Player, bool]) -> bytes:
    conn.set_status(200)
    if p:
        del cache.online[p.userid]
        conn.set_body(packets.logout(p.userid))
    return conn.response

@s.handler(target = 'banchologin', domains = bancho)
async def login(conn: Connection) -> bytes:
    body = b''
    userid = -1
    # Getting all password details
    credentials = conn.request['body'].decode().replace('\n', '|').split('|', 5)
    credentials[2] = float(credentials[2][1:])
    credentials[5] = credentials[5].replace('|', ':').split(':')

    # 0 username
    # 1 password (hashed in md5)
    # 2 game version
    # 3 ?
    # 4 ?
    # 5 hardware data

    userid = 3

    # Check credentials to see if anything is wrong
    if not credentials[0]: # this would check db but we are not at this part yet
        ... # will do eventually
    else:
        body += packets.userID(userid) # give correct userid
    
    cache.online[userid] = Player(
        userid, credentials[2], credentials[5], time.time()
    ) 
    
    body += packets.menuIcon('|'.join(config.menuicon))
    body += packets.notification(loginMsg.format(len(cache.online)))
    body += packets.protocolVersion()

    #TODO: channels, privs
    
    conn.set_status(200)
    conn.add_header('cho-token', userid)
    conn.set_body(body)
    
    return conn.response

def run(socket_type: Union[str, tuple] = ("127.0.0.1", 5000)):
    s.run(socket_type)