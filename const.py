from objects.const import Privileges, RankedStatus, ServerRankedStatus
from objects.beatmap import Beatmap
from objects.player import Player
from aiotinydb import AIOTinyDB
from config import prefix
import packets
import json
import re

commands = {}

def command(rgx: str, perms: int):
    def inner(func):
        commands[json.dumps({'rgx': rgx, 'perms': perms})] = func
        return func
    return inner

@command(f'^\{prefix}alert\ (?P<msg>.*)$', Privileges.Normal)
async def alert(msg: dict, p: Player) -> str:
    from cache import online
    msg = msg['msg']
    for key in online:
        x = online[key]
        x.enqueue.append(packets.notification(msg.replace(r'\n', '\n')))
    
    return 'Alert Sent!'

@command(f'^\{prefix}map\ (?P<rankstatus>.*) (?P<map_or_set>.*)$', Privileges.Normal)
async def mapedit(msg: dict, p: Player) -> str:
    if msg['rankstatus'] not in ('rank', 'love', 'unrank') or msg['map_or_set'] not in ('map', 'set'):
        return f'Invalid Syntax!\n{prefix}map [rank, love, unrank] [map, set]'
    
    if msg['map_or_set'] == 'map':
        async with AIOTinyDB(config.beatamp_path) as DB:
            x = DB.search(lambda z: True if z['mapid'] == p.last_np else False)
            if not x:
                return "Map couldn't be found!" # should never happen
            for doc in (docs := x):
                md5 = doc['md5']
                r = ServerRankedStatus.from_command(msg['rankstatus'])
                doc['rankedstatus'] = r

                from cache import beatmap
                if md5 in beatmap:
                    beatmap[md5]['rankedstatus'] = r
                else:
                    beatmap[md5] = doc
                    beatmap[md5]['rankedstatus'] = r
            
            DB.write_back(docs)
    else:
        async with AIOTinyDB(config.beatamp_path) as DB:
            x = DB.search(lambda z: True if z['mapid'] == p.last_np else False)
            await Beatmap.download_from_setid(x[0]['setid'])
            if not x:
                return "Map couldn't be found!" # should never happen
            x = DB.search(lambda z: True if z['setid'] == x[0]['setid'] else False)
            for doc in (docs := x):
                md5 = doc['md5']
                r = ServerRankedStatus.from_command(msg['rankstatus'])
                doc['rankedstatus'] = r

                from cache import beatmap
                if md5 in beatmap:
                    beatmap[md5]['rankedstatus'] = r
                else:
                    beatmap[md5] = doc
                    beatmap[md5]['rankedstatus'] = r
            
            DB.write_back(docs)

    
    return f'Ranked status was updated for https://osu.ppy.sh/b/{p.last_np}'

@command(f'^\{prefix}py\ (?P<args>.*)', Privileges.Normal)
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

async def process_cmd(msg: str, p: Player) -> str:
    for x in commands:
        xx = json.loads(x)
        rgx = xx['rgx']
        perms = Privileges(xx['perms'])
        rgx = re.compile(rgx)
        if not (m := rgx.match(msg)):
            continue
        if not p.privileges & perms:
            continue
    
        return await commands[x](m.groupdict(), p)


    return 'Command not found.'