from typing import Union
from objects.player import Player
from objects.const import Privileges
import json
import re

commands = {}

def command(rgx: str, perms: int):
    def inner(func):
        commands[json.dumps({'rgx': rgx, 'perms': perms})] = func
        return func
    return inner

@command(r'^\!(?P<type>[a-z]*)\ (?P<args>.*)', Privileges.Admin)
async def py(msg: dict, p: Player) -> str:
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


    return None