from typing import Union
from objects.const import Privileges

online = {}
beatmap = {}
direct = {}
channels = [  
    # '#name', 'description', 1 player count, what prives you need to see and write | privs
    ('#osu', 'general osu!chat', 0, Privileges.Normal), 
    ('#dev', 'Development Chat!', 0, Privileges.Admin), 
    ('#lobby', 'Find a multi!', 0, Privileges.Normal)
]

async def get_channel_from_name(name: str):
    """channels"""
    for channel in channels:
        if channel[0] == name:
            return channel
    return None

async def from_name(username: str):
    """users"""
    for key in online:
        if (p := online[key]).username == username:
            return p
    
    return None

async def from_userids(ids: Union[list, tuple]) -> dict:
    """users"""
    x = {}
    for key in online:
        if key in ids:
            x[key] = online[key]
        
    return x