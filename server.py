from objects.beatmap import Beatmap
from WebLamp import Connection, printc
from WebLamp.utlies import Colors
from serverwrapper import OsuServer
from packets import PacketIDS
from typing import Union
from objects.player import Player
from objects.const import GameMode, Mods, RankedStatus, RankingType, ServerRankedStatus, UserIDS
from helpers import USERS, SCORES, BEATMAPS
from functools import lru_cache
import aiohttp
import packets
import config
import os
import cache
import time
import hashlib 
import re
import json

regex = {
    'email': re.compile(r'^\w+@\w+.\w+$')
}

s = OsuServer()
bancho = ("c.ppy.sh", "c4.ppy.sh", "c5.ppy.sh", "c6.ppy.sh")
web = ["osu.ppy.sh"]
avatar = ["a.ppy.sh"]

DIRECT_API = "https://beatconnect.io/api"

loginMsg = '\n'.join([
    "Welcome to Rain!",
    "",
    "This was made for the sole purpose of learning how to make a server.",
    "if your here welcome and enjoy your time.",
    "There are currently {} online users"
])

@s.handler(target = '/users', domains = web, method = ['POST'])
async def accountCreation(conn: Connection) -> bytes:
    body = b''
    errors = {
        'username': [],
        'user_email': [],
        'password': [],
    }

    credentials = conn.request['multipart']
    username = credentials[1][1][:-2]
    email = credentials[2][1][:-2]
    password = credentials[3][1][:-2]
    check = credentials[4][1][:-2] # idk what this does for now

    # you would have to do more checks but im not gonna do that lol
    if not regex['email'].match((email := email.decode())):
        errors['user_email'].append('Please enter a valid email.')
    
    if len((username := username.decode())) < 4:
        errors['username'].append(
            'Username is too short. Please make a username of at least 4 character'
        )
    
    async with USERS as DB:
        if DB.get(lambda x: True if x['username'] == username else False):
            errors['username'].append(
            'Username already exists!'
        )
        if DB.get(lambda x: True if x['email'] == email else False):
            errors['username'].append(
            'email already exists! Are you sure your making your first account ever? :D'
        )
    
    if len(password.decode()) < 2:
        errors['password'].append(
            'Password is too short. Please make a password of at least 2 character'
        )
    
    if True in [bool(errors[x]) for x in errors]:
        conn.set_status(400)
        body += json.dumps(
            {'form_error': {'user': errors}}
        ).encode()
        conn.set_body(body)
        return conn.response
    
    if check == b'0':
        password = hashlib.md5(password).hexdigest()
        async with USERS as db:
            users = db.search(lambda x: True if True else True)
            i = {
                'userid': len(users) + 3,
                'username': username,
                'passwordmd5': password,
                'email': email,
                'version': 0,
                'hwidMd5': [],
                'privs': 1,
                'std': {
                    'reg': {
                        'ranked_score': 0, 'acc': 0, 
                        'playcount': 0, 'total_score': 0, 
                        'rank': len(users) + 1, 'pp': 0 
                        },
                    'rx': {
                        'ranked_score': 0, 'acc': 0, 
                        'playcount': 0, 'total_score': 0, 
                        'rank': len(users) + 1, 'pp': 0 
                    },
                    'ap': {
                        'ranked_score': 0, 'acc': 0, 
                        'playcount': 0, 'total_score': 0, 
                        'rank': len(users) + 1, 'pp': 0 
                    }
                },
                'taiko': {
                    'reg': {
                        'ranked_score': 0, 'acc': 0, 
                        'playcount': 0, 'total_score': 0, 
                        'rank': len(users) + 1, 'pp': 0 
                    },
                    'rx': {
                        'ranked_score': 0, 'acc': 0, 
                        'playcount': 0, 'total_score': 0, 
                        'rank': len(users) + 1, 'pp': 0 
                    }
                },
                'ctb': {
                    'reg': {
                        'ranked_score': 0, 'acc': 0, 
                        'playcount': 0, 'total_score': 0, 
                        'rank': len(users) + 1, 'pp': 0 
                    },
                    'rx': {
                        'ranked_score': 0, 'acc': 0, 
                        'playcount': 0, 'total_score': 0, 
                        'rank': len(users) + 1, 'pp': 0 
                    }
                },
                'mania': {
                    'reg': {
                        'ranked_score': 0, 'acc': 0, 
                        'playcount': 0, 'total_score': 0, 
                        'rank': len(users) + 1, 'pp': 0 
                    }
                }
            }
            db.insert(i)
        printc(f'{username} has registered an account!', Colors.Blue)
        body += b'ok'
    else:
        body += b'ok'
    
    conn.set_status(200)
    conn.set_body(body)
    return conn.response

@s.handler(target = '/web/osu-submit-modular-selector.php', domains = web)
async def scoreSub(conn: Connection) -> bytes:
    # When osu sends 'replay bytes'
    # it doesn't actually send replay bytes
    # it sends cursor movements or frames as a proper word
    print()
    
    return b''

@s.handler(target = '/web/osu-osz2-getscores.php', domains = web)
async def leaderboard(conn: Connection) -> bytes:
    conn.set_status(200)
    body = b''
    params = conn.request['params']
    p: Player = await cache.from_name(params['us'])
    if not p:
        return b''
    map_md5 = params['c']
    mods = Mods(int(params['mods']))
    mode = GameMode.from_params(int(params['m']), mods)
    map_set_id = int(params['i'])
    rank_type = RankingType(int(params['v']))
    filename = params['f'].replace('+', ' ').replace('%5b', '').replace('%5d', '')

    if p.mode != mode:
        p.mode = mode
        await p.update()
        p.enqueue.append(packets.userStats(p))
        p.enqueue.append(packets.userPresence(p))
    
    lb = []
    if filename in cache.beatmap:
        m = cache.beatmap[map_md5]
        lb.append(f'{m.rankedstatus}|false')
    elif (m := await Beatmap.from_md5_to_api(map_md5)):
        lb.append(f'{m.rankedstatus}|false')
        cache.beatmap[map_md5] = m
    else:
        lb.append(f'{ServerRankedStatus.Pending}|false')
    
    conn.set_body('\n'.join(lb).encode())
    return conn.response

@s.handler(target = '/web/osu-search.php', domains = web)
async def direct(conn: Connection) -> bytes:
    args = conn.request['params']
    url = f'{config.mirror}/api/search/'
    params = {
        'token': config.api_keys['beatconnect']
    }

    if args['q'] and args['q'] != 'Newest':
        params['q'] = args['q'].replace('+', ' ')

    if args['m'] != '-1':
        params['m'] = GameMode.to_api(int(args['m']))

    params['s'] = RankedStatus.to_api(int(args['r']))

    async with aiohttp.request('GET', url, params = params) as req:
        if not req or req.status != 200 or not (r := await req.json()):
            return b"Failed to find maps!"

    beatmaps = r['beatmaps']
    lbeatmaps = len(beatmaps)
    maps = [f"{'101' if lbeatmaps == 100 else lbeatmaps}"]
    
    for bmap in beatmaps:
        diffs = []
        for row in sorted(bmap['beatmaps'], key = lambda x: x['difficulty']):
            diffs.append(
                '[{difficulty:.2f}⭐] {version} {{CS{cs} OD{accuracy} AR{ar} HP{drain}}}@{mode_int}'.format(
                **row)
            )

        diffs = ','.join(diffs)
        maps.append(
            '{id}.osz|{artist}|{title}|{creator}|'
            '{ranked}|10.0|{last_updated}|{id}|'
            '0|0|0|0|0|{diffs}'.format(**bmap, diffs=diffs)
        ) # 0s are threadid, has_vid, has_story, filesize, filesize_novid

    conn.set_status(200)
    conn.set_body('\n'.join(maps).encode())
    return conn.response

@s.handler(target = PacketIDS.OSU_RECEIVE_UPDATES, domains = bancho)
async def action(conn: Connection, p: Union[Player, bool]) -> bytes:
    conn.set_status(200)
    if not p:
        body = b''
        body += packets.notification('Server restarting!') 
        body += packets.systemRestart()
        conn.set_body(body)
        return conn.response
    if p.enqueue:
        body = b''
        for x in p.enqueue:
            body += x
        conn.set_body(body)
        return conn.response #TODO don't return
    
    printc(PacketIDS.OSU_RECEIVE_UPDATES.name, Colors.Red)
    return b''

@s.handler(target = PacketIDS.OSU_REQUEST_STATUS_UPDATE, domains = bancho)
async def action(conn: Connection, p: Union[Player, bool]) -> bytes:
    conn.set_status(200)
    if not p:
        body = b''
        body += packets.notification('Server restarting!') 
        body += packets.systemRestart()
        conn.set_body(body)
        return conn.response
    if p.enqueue:
        body = b''
        for x in p.enqueue:
            body += x
        conn.set_body(body)
        return conn.response #TODO don't return
    
    printc(PacketIDS.OSU_REQUEST_STATUS_UPDATE.name, Colors.Red)
    return b''

@s.handler(target = PacketIDS.OSU_USER_STATS_REQUEST, domains = bancho)
async def action(conn: Connection, p: Union[Player, bool]) -> bytes:
    conn.set_status(200)
    if not p:
        body = b''
        body += packets.notification('Server restarting!') 
        body += packets.systemRestart()
        conn.set_body(body)
        return conn.response
    if p.enqueue:
        body = b''
        for x in p.enqueue:
            body += x
        conn.set_body(body)
        return conn.response #TODO don't return
    
    printc(PacketIDS.OSU_USER_STATS_REQUEST.name, Colors.Red)
    return b''

@s.handler(target = PacketIDS.OSU_CHANGE_ACTION, domains = bancho)
async def action(conn: Connection, p: Union[Player, bool]) -> bytes:
    conn.set_status(200)
    if not p:
        body = b''
        body += packets.notification('Server restarting!') 
        body += packets.systemRestart()
        conn.set_body(body)
        return conn.response
    if p.enqueue:
        body = b''
        for x in p.enqueue:
            body += x
        conn.set_body(body)
        return conn.response #TODO don't return
    
    printc(PacketIDS.OSU_CHANGE_ACTION.name, Colors.Red)
    return b''

@s.handler(target = r'^/d/(?P<setid>[0-9]*)$', domains = web)
@lru_cache(maxsize=None)
async def download(conn: Connection) -> bytes:
    conn.set_status(200)
    setid = int(conn.args['setid'])
    async with aiohttp.request('GET', f'{config.mirror}/b/{setid}') as req:
        if not req or req.status != 200:
            conn.set_body(b"can't retrive map")
            return conn.response
        
        conn.set_body(await req.content.read())
    return conn.response

@s.handler(target = r'^/(?P<userid>[0-9]*)$', domains = avatar)
@lru_cache(maxsize=None)
async def ava(conn: Connection) -> bytes:
    conn.set_status(200)
    userid = int(conn.args['userid'])

    if os.path.exists(f'./data/avatars/{userid}.png'):
        with open(f'./data/avatars/{userid}.png', 'rb') as f:
            pfp = f.read()
    else:
        with open(f'./data/avatars/-1.png', 'rb') as f:
            pfp = f.read()
    
    conn.set_body(pfp)
    return conn.response

@s.handler(target = PacketIDS.OSU_PING, domains = bancho)
async def pong(conn: Connection, p: Union[Player, bool]) -> bytes:
    conn.set_status(200)
    conn.set_body(b'')
    return conn.response

@s.handler(target = PacketIDS.OSU_LOGOUT, domains = bancho)
async def logout(conn: Connection, p: Union[Player, bool]) -> bytes:
    conn.set_status(200)
    if p:
        if (time.time() - p.loginTime) < 2:
            return b''
        del cache.online[p.userid]
        conn.set_body(packets.logout(p.userid))
        printc(f'{p.username} has logged out!', Colors.Blue)
    return conn.response

@s.handler(target = 'banchologin', domains = bancho)
async def login(conn: Connection) -> bytes:
    body = b''
    userid = -1
    # Getting all credentials details
    credentials = conn.request['body'].decode().replace('\n', '|').split('|', 5)
    credentials[2] = float(credentials[2][1:])
    credentials[5] = credentials[5].replace('|', ':').split(':')

    # 0 username
    # 1 password (hashed in md5)
    # 2 game version
    # 3 ?
    # 4 ?
    # 5 hardware data

    async with USERS as DB:
        x = DB.get(lambda x: True if x['username'] == credentials[0] else False)
        if not x:
            pass
        elif x and (x['username'], x['passwordmd5']) == (credentials[0], credentials[1]):
            userid = x['userid']
        
    if userid < 0:
        conn.set_status(200)
        conn.add_header('cho-token', userid)
        body += packets.userID(userid)
        conn.set_body(body)   
        return conn.response
        
    body += packets.userID(userid)
    
    p = Player(
        userid, credentials[2], credentials[5], time.time()
    )
    await p.update()
    
    body += packets.menuIcon('|'.join(config.menuicon))
    body += packets.notification(loginMsg.format(len(cache.online) + 1))
    body += packets.protocolVersion()
    body += packets.banchoPrivs(p)
    body += packets.userStats(p)
    body += packets.userPresence(p)
    body += packets.channelStart()
    
    for c in cache.channels:
        if not p.privileges & c[3]: # check if player is allowed to see channels privs 
            continue
            
        body += packets.channelJoin(c[0])
        body += packets.channelInfo(c[0], c[1], c[2])
    
    #TODO: channels
    
    body += packets.userStats(p)
    for x in cache.online: 
        body += packets.userPresence(cache.online[x]) + packets.userStats(cache.online[x])
    cache.online[userid] = p

    conn.set_status(200)
    conn.add_header('cho-token', userid)
    conn.set_body(body)
    printc(f'{p.username} has logged in!', Colors.Blue)
    return conn.response

def run(socket_type: Union[str, tuple] = ("127.0.0.1", 5000)):
    s.run(socket_type)