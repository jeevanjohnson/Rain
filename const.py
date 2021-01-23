from objects.const import MsgStatus, Privileges, ServerRankedStatus
from cache import beatmap, leaderboards
from objects.beatmap import Beatmap
from objects.player import Player
from aiotinydb import AIOTinyDB
from config import prefix
from typing import Union
import packets
import config
import json
import re

commands = {}
comrgx = re.compile(f'^\{prefix}' + r'(?P<cmd>[a-zA-Z]*) (?P<args>.*)')

def command(triggers: list, perms: Privileges, public: MsgStatus):
    def inner(func):
        commands[json.dumps({'triggers': triggers, 'perms': perms.value, 'public': public.value})] = func
        return func
    return inner

@command(triggers = ['alert'], perms = Privileges.Normal, public = MsgStatus.Private)
async def alert(msg: dict, p: Player) -> str:
    from cache import online
    msg = msg['msg']
    for key in online:
        x = online[key]
        x.enqueue.append(packets.notification(msg.replace(r'\n', '\n')))
    
    return 'Alert Sent!'

@command(triggers = ['map'], perms = Privileges.Normal, public = MsgStatus.Both)
async def mapedit(msg: dict, p: Player) -> str:
    args = msg['args']

    if args[0] not in ('rank', 'love', 'unrank', 'approve') \
    or args[1] not in ('map', 'set'):
        return f'Invalid Syntax!\n{prefix}map [rank, love, unrank] [map, set]'
    
    if args[1] == 'map':
        async with AIOTinyDB(config.beatamp_path) as DB:
            x = DB.search(lambda z: True if z['mapid'] == p.last_np else False)
            if not x:
                return "Map couldn't be found!" # should never happen
            for doc in (docs := x):
                bmap = doc
                md5 = doc['md5']
                r = ServerRankedStatus.from_command(args[0])
                doc['rankedstatus'] = r

                if md5 in leaderboards:
                    leaderboards[md5][0] = str(r.value) + leaderboards[md5][0][1:]

                if md5 in beatmap:
                    beatmap[md5]['rankedstatus'] = r
                else:
                    beatmap[md5] = doc
                    beatmap[md5]['rankedstatus'] = r
            
            DB.write_back(docs)
    else:
        async with AIOTinyDB(config.beatamp_path) as DB:
            x = DB.search(lambda z: True if z['mapid'] == p.last_np else False)
            if not x:
                return "Map couldn't be found!" # should never happen
            await Beatmap.download_from_setid(x[0]['setid'])
            x = DB.search(lambda z: True if z['setid'] == x[0]['setid'] else False)
            for doc in (docs := x):
                bmap = doc
                md5 = doc['md5']
                r = ServerRankedStatus.from_command(args[0])
                doc['rankedstatus'] = r

                if md5 in leaderboards:
                    leaderboards[md5][0] = str(r.value) + leaderboards[md5][0][1:]

                if md5 in beatmap:
                    beatmap[md5]['rankedstatus'] = r
                else:
                    beatmap[md5] = doc
                    beatmap[md5]['rankedstatus'] = r
            
            DB.write_back(docs)

    if args[1] == 'map':
        return '{title} [{diff_name}] was {status}!'.format(**bmap, status = ServerRankedStatus.to_command(r))
    else:
        return "{title}'s set was {status}!".format(**bmap, status = ServerRankedStatus.to_command(r))

@command(triggers = ['py'], perms = Privileges.Normal, public = MsgStatus.Public)
async def py(msg: dict, p: Player) -> str:
    #TODO: change from normal user to admin
    import cache
    try:
        f = {}
        exec(f'async def _py(p, msg, cache):\n    {msg["args"]}', f)
        output = await f['_py'](p, msg, cache)
        if output:
            return str(output)
        else:
            return 'Success'
    except Exception as e:
        return str(e).replace(r'\n', '\n')

async def process_cmd(msg: str, p: Player, msgstatus: MsgStatus) -> Union[str, bool]:
    msg = comrgx.search(msg)
    if not msg:
        return None
    
    msg = msg.groupdict()
    msg['args'] = msg['args'].split()

    for x in commands:
        triggers, perms, public = json.loads(x).values()
        perms = Privileges(perms)
        public = MsgStatus(public)
        
        if msg['cmd'] not in triggers:
            continue
        if not p.privileges & perms:
            continue
        if not public & MsgStatus.Both:
            if not msgstatus & public:
                continue
    
        return await commands[x](msg, p)

    return None