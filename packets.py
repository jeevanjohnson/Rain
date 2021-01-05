"""
This section needs SO MUCH rewriting due
to it being old and i can improve it now
+ its unfinished lmao
"""

from enum import IntEnum
import struct
from functools import lru_cache
from typing import Union

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

def length_of_bytes(content: bytes) -> bytes:
	length = b''
	while content:
		length += bytes([len(content[:255])])
		content = content[255:]
	return length

def write_string(string: str) -> bytes:
	return b'\x0b' + length_of_bytes(string.encode()) + string.encode()

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
	p[1] = length_of_bytes(p[2]) + b'\x00\x00\x00'

	return b''.join(p)

def read_packet(data: bytes):
	"""soon"""
	...

def channelStart():
	return write(PacketIDS.CHO_CHANNEL_INFO_END)

def channelInfo(name: str, topic: str, Pcount: int):
	return write(
		PacketIDS.CHO_CHANNEL_INFO, 
		(name, 'string'), (topic, 'string'), (Pcount, 'unB')
	)

def channelJoin(name: str) -> bytes:
	return write(
		PacketIDS.CHO_CHANNEL_JOIN_SUCCESS, (name, 'string')
	)

def userID(i: int) -> bytes:
	return write(
		PacketIDS.CHO_USER_ID, (i, f"{'unI' if i > 0 else 'int'}")
	)

# def userStats(p: 'Player') -> bytes:
# 	return write(
# 		PacketIDS.CHO_USER_STATS, 
# 		(p.userid, 'int'), (p.action, 'b'),
# 		(p.info_text, 'string'), (p.map_md5, 'string'),
# 		(p.mods, 'int'), (p.mode, 'unB'),
# 		(p.map_id, 'int'), (p.stats.ranked_score, 'long_long'),
# 		(p.stats.acc / 100.0, 'float'), (p.stats.playcount, 'int'),
# 		(p.stats.total_score, 'long_long'), (p.stats.rank, 'int'),
# 		(p.stats.pp, 'short')
# 	)
# 
# def userPresence(p: 'Player') -> bytes:
# 	return write(
# 		PacketIDS.CHO_USER_PRESENCE,
# 		(p.userid, 'int'), (p.username, 'string'),
# 		(p.utc_offset + 24, 'unB'), (p.country[0], 'unB'),
# 		(p.priv | p.mode << 5, 'unB'), (p.location[0], 'float'),
# 		(p.location[1], 'float'), (p.stats.rank, 'int')
# 	)
# 
# def banchoPrivs(p: 'Player') -> bytes:
# 	return write(
# 		PacketIDS.CHO_PRIVILEGES, (p.priv, 'unB')
# 	)

def notification(msg: str) -> bytes:
	return write(
		PacketIDS.CHO_NOTIFICATION, (msg, 'string')
	)

@lru_cache(maxsize=1)
def menuIcon(icon: str) -> bytes:
	return write(
		PacketIDS.CHO_MAIN_MENU_ICON, (icon, 'string')
	)
