from objects.const import Privileges, ClientPrivileges

online = {}
beatmap = {}
direct = {}
channels = [
    ('#how', 'how', 0, Privileges.Normal), 
    # '#name', 'description', 1 player count, what prives you need to see | privs
]

def from_name(username: str):
    for key in online:
        if (p := online[key]).username == username:
            return p
    
    return None