from typing import Union
from objects.const import Privileges

online = {}
beatmap = {}
direct = {}
channels = [
    ('#how', 'how', 0, Privileges.Normal), 
    # '#name', 'description', 1 player count, what prives you need to see | privs
]

async def get_channel_from_name(name: str):
    for channel in channels:
        if channel[0] == name:
            return channel
    return None

async def from_name(username: str):
    for key in online:
        if (p := online[key]).username == username:
            return p
    
    return None

async def from_userids(ids: Union[list, tuple]) -> dict:
    x = {}
    for key in online:
        if key in ids:
            x[key] = online[key]
        
    return x