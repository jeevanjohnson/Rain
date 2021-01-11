"""
This section needs SO MUCH rewriting due
to it being old and i can improve it now
+ its unfinished lmao
"""

from enum import IntEnum
from objects.const import Action, GameMode, Mods
import struct
from functools import lru_cache
from typing import Union
from objects.player import Player

"""
Packets from the client and the server sending them are
formated by this:

\x05 \x00
^ 
packetid

\x00 <- compressed byte

\x04 \x00 \x00 \x00
^ 
length of packet data

\xff\xff\xff\xff <- packet data

"""

class PacketIDS(IntEnum):
    OSU_CHANGE_ACTION = 0
    OSU_SEND_PUBLIC_MESSAGE = 1
    OSU_LOGOUT = 2
    OSU_REQUEST_STATUS_UPDATE = 3
    OSU_PING = 4
    CHO_USER_ID = 5
    CHO_SEND_MESSAGE = 7
    CHO_PONG = 8
    CHO_HANDLE_IRC_CHANGE_USERNAME = 9
    CHO_HANDLE_IRC_QUIT = 10
    CHO_USER_STATS = 11
    CHO_USER_LOGOUT = 12
    CHO_SPECTATOR_JOINED = 13
    CHO_SPECTATOR_LEFT = 14
    CHO_SPECTATE_FRAMES = 15
    OSU_START_SPECTATING = 16
    OSU_STOP_SPECTATING = 17
    OSU_SPECTATE_FRAMES = 18
    CHO_VERSION_UPDATE = 19
    OSU_ERROR_REPORT = 20
    OSU_CANT_SPECTATE = 21
    CHO_SPECTATOR_CANT_SPECTATE = 22
    CHO_GET_ATTENTION = 23
    CHO_NOTIFICATION = 24
    OSU_SEND_PRIVATE_MESSAGE = 25
    CHO_UPDATE_MATCH = 26
    CHO_NEW_MATCH = 27
    CHO_DISPOSE_MATCH = 28
    OSU_PART_LOBBY = 29
    OSU_JOIN_LOBBY = 30
    OSU_CREATE_MATCH = 31
    OSU_JOIN_MATCH = 32
    OSU_PART_MATCH = 33
    CHO_TOGGLE_BLOCK_NON_FRIEND_DMS = 34
    CHO_MATCH_JOIN_SUCCESS = 36
    CHO_MATCH_JOIN_FAIL = 37
    OSU_MATCH_CHANGE_SLOT = 38
    OSU_MATCH_READY = 39
    OSU_MATCH_LOCK = 40
    OSU_MATCH_CHANGE_SETTINGS = 41
    CHO_FELLOW_SPECTATOR_JOINED = 42
    CHO_FELLOW_SPECTATOR_LEFT = 43
    OSU_MATCH_START = 44
    CHO_ALL_PLAYERS_LOADED = 45
    CHO_MATCH_START = 46
    OSU_MATCH_SCORE_UPDATE = 47
    CHO_MATCH_SCORE_UPDATE = 48
    OSU_MATCH_COMPLETE = 49
    CHO_MATCH_TRANSFER_HOST = 50
    OSU_MATCH_CHANGE_MODS = 51
    OSU_MATCH_LOAD_COMPLETE = 52
    CHO_MATCH_ALL_PLAYERS_LOADED = 53
    OSU_MATCH_NO_BEATMAP = 54
    OSU_MATCH_NOT_READY = 55
    OSU_MATCH_FAILED = 56
    CHO_MATCH_PLAYER_FAILED = 57
    CHO_MATCH_COMPLETE = 58
    OSU_MATCH_HAS_BEATMAP = 59
    OSU_MATCH_SKIP_REQUEST = 60
    CHO_MATCH_SKIP = 61
    CHO_UNAUTHORIZED = 62 # unused
    OSU_CHANNEL_JOIN = 63
    CHO_CHANNEL_JOIN_SUCCESS = 64
    CHO_CHANNEL_INFO = 65
    CHO_CHANNEL_KICK = 66
    CHO_CHANNEL_AUTO_JOIN = 67
    OSU_BEATMAP_INFO_REQUEST = 68
    CHO_BEATMAP_INFO_REPLY = 69
    OSU_MATCH_TRANSFER_HOST = 70
    CHO_PRIVILEGES = 71
    CHO_FRIENDS_LIST = 72
    OSU_FRIEND_ADD = 73
    OSU_FRIEND_REMOVE = 74
    CHO_PROTOCOL_VERSION = 75
    CHO_MAIN_MENU_ICON = 76
    OSU_MATCH_CHANGE_TEAM = 77
    OSU_CHANNEL_PART = 78
    OSU_RECEIVE_UPDATES = 79
    CHO_MONITOR = 80 # unused
    CHO_MATCH_PLAYER_SKIPPED = 81
    OSU_SET_AWAY_MESSAGE = 82
    CHO_USER_PRESENCE = 83
    OSU_IRC_ONLY = 84
    OSU_USER_STATS_REQUEST = 85
    CHO_RESTART = 86
    OSU_MATCH_INVITE = 87
    CHO_MATCH_INVITE = 88
    CHO_CHANNEL_INFO_END = 89
    OSU_MATCH_CHANGE_PASSWORD = 90
    CHO_MATCH_CHANGE_PASSWORD = 91
    CHO_SILENCE_END = 92
    OSU_TOURNAMENT_MATCH_INFO_REQUEST = 93
    CHO_USER_SILENCED = 94
    CHO_USER_PRESENCE_SINGLE = 95
    CHO_USER_PRESENCE_BUNDLE = 96
    OSU_USER_PRESENCE_REQUEST = 97
    OSU_USER_PRESENCE_REQUEST_ALL = 98
    OSU_TOGGLE_BLOCK_NON_FRIEND_DMS = 99
    CHO_USER_DM_BLOCKED = 100
    CHO_TARGET_IS_SILENCED = 101
    CHO_VERSION_UPDATE_FORCED = 102
    CHO_SWITCH_SERVER = 103
    CHO_ACCOUNT_RESTRICTED = 104
    CHO_RTX = 105 # unused
    CHO_MATCH_ABORT = 106
    CHO_SWITCH_TOURNAMENT_SERVER = 107
    OSU_TOURNAMENT_JOIN_MATCH_CHANNEL = 108
    OSU_TOURNAMENT_LEAVE_MATCH_CHANNEL = 109

def write_uleb128(num: int) -> bytes:
    if num == 0:
        return bytearray(b'\x00')

    ret = bytearray()
    length = 0

    while num > 0:
        ret.append(num & 0b01111111)
        num >>= 7
        if num != 0:
            ret[length] |= 0b10000000
        length += 1

    return bytes(ret)

def write_string(string: str) -> bytes:
    return b'\x0b' + write_uleb128(len(string.encode())) + string.encode()

def write_int(i: int) -> bytes:
    return struct.pack('<i', i)

def write_unsigned_int(i: int) -> bytes:
    return struct.pack('<I', i)

def write_float(f: float) -> bytes:
    return struct.pack('<f', f)

def write_byte(b: int) -> bytes:
    return struct.pack('<b', b)

def write_unsigned_byte(b: int) -> bytes:
    return struct.pack('<B', b)

def write_short(s: int) -> bytes:
    return struct.pack('<h', s)

def write_long_long(l: int) -> bytes:
    return struct.pack('<q', l)

def write(packetid: int, *args) -> bytes:
    """Putting together the base of the packet"""
    p = [struct.pack('<Hx', packetid), b'', b'']

    """Adding the body of the packet"""
    for ctx, _type in args:
        if _type == 'string':
            p[2] += write_string(ctx)
        elif _type == 'int':
            p[2] += write_int(ctx)
        elif _type == 'unsigned int' or _type == 'unI':
            p[2] += write_unsigned_int(ctx)
        elif _type == 'short':
            p[2] += write_short(ctx)
        elif _type == 'float':
            p[2] += write_float(ctx)
        elif _type == 'long_long':
            p[2] += write_long_long(ctx)
        elif _type == 'b' or _type == 'byte':
            p[2] += write_byte(ctx)
        elif _type == 'unsigned_byte' or _type == 'unB':
            p[2] += write_unsigned_byte(ctx)
        else:
            """Custom type O_O"""
            p[2] += struct.pack(f'<{_type}', ctx)
    
    """Adding size"""
    p[1] = struct.pack('<I', len(p[2]))	
    
    return b''.join(p)

def read_packet(data: bytes, type: str):
    x = PacketReader(data)
    decoded_data: Union[str, list, dict, int]
    if type == 'action':
        decoded_data = x.readAction()
    elif type == 'list_i32':
        decoded_data = x.read_i32_list(len_size = 2)
    elif type == 'message':
        decoded_data = x.read_msg()
    elif type == 'updates':
        decoded_data = x.read_updates()  
    elif type == 'channelJoin':
        decoded_data = x.read_string()  
    else:
        Exception("Can't read data")
    
    return decoded_data

class PacketReader:
    def __init__(self, data: bytes) -> None:
        # reference from coover import Replay
        self._data = data
        self.offset = 0
        self.packetID = self.read_packetID()
        self.length = self.read_length()
    
    @property
    def data(self):
        return self._data[self.offset:]
    
    def read_updates(self) -> int:
        return self.read_int()

    def read_msg(self) -> list:
        # 0: client
        # 1: msg
        # 2: target
        # 3: client_id
        return [
            self.read_string(),
            self.read_string(),
            self.read_string(),
            self.read_int()
        ]

    def read_i32_list(self, len_size: int) -> list:
        # MISS READ
        length, = struct.unpack(f'<{"h" if len_size == 2 else "i"}', self.data[:len_size])
        self.offset += len_size

        val = struct.unpack(f'<{"I" * length}', self.data[:length * 4])
        self.offset += length * 4
        return val
    
    def readAction(self) -> dict:
        a = {
            'action': Action(self.read_unsigned_byte()), # 'unB',
            'info_text': self.read_string(), # 'string',
            'map_md5': self.read_string(), # 'string',
            'mods': self.read_unsigned_int(), # 'unI',
            'mode': self.read_unsigned_byte(), # 'unB',
            'map_id': self.read_int() # 'int',
        }
        a['mods'] = m = Mods(a['mods'])
        if not (readableMods := m.__repr__()):
            a['mods'] = 0
        elif 'RX' in readableMods:
            a['mode'] += 4
        elif 'AP' in readableMods:
           a['mode'] = 7
        
        a['mode'] = GameMode(a['mode'])
        a['mods'] = Mods(a['mods'])

        return a

    def read_packetID(self) -> PacketIDS:
        format_specifier = '<Hx'
        val, = struct.unpack(format_specifier, self.data[:3])
        self.offset += 3
        return val
    
    def read_length(self) -> int:
        format_specifier = '<I'
        val, = struct.unpack(format_specifier, self.data[:4])
        self.offset += 4
        return val

    def read_unsigned_int(self) -> int:
        format_specifier = '<I'
        val, = struct.unpack(format_specifier, self.data[:4])
        self.offset += 4
        return val
    
    def read_unsigned_byte(self) -> int:
        format_specifier = '<B'
        val, = struct.unpack(format_specifier, self.data[:1])
        self.offset += 1
        return val

    def read_byte(self) -> int:
        format_specifer = '<b'
        val, = struct.unpack(format_specifer, self.data[:1])
        self.offset += 1
        return val

    def read_short(self) -> int:
        format_specifer = '<h'
        val, = struct.unpack(format_specifer, self.data[:2])
        self.offset += 2
        return val

    def read_int(self) -> int:
        format_specifer = '<i'
        val, = struct.unpack(format_specifer, self.data[:4])
        self.offset += 4
        return val

    def read_long_long(self) -> int:
        format_specifer = '<q'
        val, = struct.unpack(format_specifer, self.data[:8])
        self.offset += 8
        return val

    def read_double(self) -> int:
        format_specifer = '<d'
        val, = struct.unpack(format_specifer, self.data[:8])
        self.offset += 8
        return val

    def read_uleb128(self) -> int:
        val = shift = 0

        while True:
            b = self.data[0]
            self.offset += 1

            val |= ((b & 0b01111111) << shift)
            if (b & 0b10000000) == 0:
                break


            shift += 7

        return val

    def read_string(self) -> str:
        if self.read_byte() == 0x0b:
            return self.read_raw(self.read_uleb128()).decode()

        return ''

    def read_raw(self, length: int) -> bytes:
        val = self.data[:length]
        self.offset += length
        return val
    

def channelStart():
    return write(PacketIDS.CHO_CHANNEL_INFO_END)

def channelInfo(name: str, topic: str, Pcount: int):
    return write(
        PacketIDS.CHO_CHANNEL_INFO, 
        (name, 'string'), (topic, 'string'), (Pcount, 'short')
    )

def channelJoin(name: str) -> bytes:
    return write(
        PacketIDS.CHO_CHANNEL_JOIN_SUCCESS, (name, 'string')
    )

def userID(i: int) -> bytes:
    return write(
        PacketIDS.CHO_USER_ID, (i, f"{'unI' if i > 0 else 'int'}")
    )

def logout(userID: int) -> bytes:
    return write(
        PacketIDS.CHO_USER_LOGOUT, (userID, 'int'), (0, 'unB')
    )

def userStats(p: 'Player') -> bytes:
    return write(
        PacketIDS.CHO_USER_STATS, 
        (p.userid, 'int'), (p.action, 'b'),
        (p.info_text, 'string'), (p.map_md5, 'string'),
        (p.mods, 'int'), (p.mode, 'unB'),
        (p.map_id, 'int'), (p.stats.ranked_score, 'long_long'),
        (p.stats.acc / 100.0, 'float'), (p.stats.playcount, 'int'),
        (p.stats.total_score, 'long_long'), (p.stats.rank, 'int'),
        (p.stats.pp, 'short')
    )

def userPresence(p: 'Player') -> bytes:
    return write(
        PacketIDS.CHO_USER_PRESENCE,
        (p.userid, 'int'), (p.username, 'string'),
        (p.utc_offset + 24, 'unB'), (p.country[0], 'unB'),
        (p.banco_privs | p.mode << 5, 'unB'), (p.location[0], 'float'),
        (p.location[1], 'float'), (1, 'int') # p.stats.rank
    )

def banchoPrivs(p: 'Player') -> bytes:
    return write(
        PacketIDS.CHO_PRIVILEGES, (p.banco_privs, 'int')
    )

def notification(msg: str) -> bytes:
    return write(
        PacketIDS.CHO_NOTIFICATION, (msg, 'string')
    )

@lru_cache(maxsize=1)
def menuIcon(icon: str) -> bytes:
    return write(
        PacketIDS.CHO_MAIN_MENU_ICON, (icon, 'string')
    )

@lru_cache(maxsize=1)
def protocolVersion(i: int = 19):
    return write(
        PacketIDS.CHO_PROTOCOL_VERSION, (i, 'int')
    )

def systemRestart(ms: int = 1) -> bytes:
    return write(
        PacketIDS.CHO_RESTART, (ms, 'int')
    )

def pong() -> bytes:
    return write(
        PacketIDS.CHO_PONG
    )

def sendMessage(client: str, msg: str, target: str, userid: int):
    # client is most likely username
    # id is most likely userid
    # target is our channel
    # msg is our msg man
    return write(
        PacketIDS.CHO_SEND_MESSAGE, 
        (client, 'string'), (msg, 'string'),
        (target, 'string'), (userid, 'int') 
    )

def write_channel(name: str, topic: str, count: int) -> bytes:
    body = write_string(name)
    body += write_string(topic)
    body += write_int(count)
    return body