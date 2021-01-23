from enum import IntEnum, IntFlag, unique

class DICT_TO_CLASS:
    def __init__(self, **entries):
        self.__dict__.update(entries)

class MsgStatus(IntFlag):
    Public = 0
    Private = 1
    Both = 2

@unique
class ScoreStatus(IntEnum):
	FAILED = 0
	SUBMITTED = 1
	BEST = 2

@unique
class PresenceFilter(IntEnum):
    # this filter allows you to
    # see only your friends for chat ingame
    # or everyone online
    Nil     = 0
    All     = 1
    Friends = 2

members = PresenceFilter.__members__.values()

@unique
class RankingType(IntEnum):
    Local   = 0
    Top     = 1
    Mods    = 2
    Friends = 3
    Country = 4

@unique
class Privileges(IntFlag):
    """Server side user privileges."""

    Normal      = 1 << 0
    Verified    = 1 << 1

    Whitelisted = 1 << 2

    Supporter   = 1 << 4
    Premium     = 1 << 5

    Alumni      = 1 << 7

    Tournament  = 1 << 10
    Nominator   = 1 << 11
    Mod         = 1 << 12
    Admin       = 1 << 13
    Dangerous   = 1 << 14

    Donator = Supporter | Premium
    Staff = Mod | Admin | Dangerous

@unique
class ClientPrivileges(IntFlag):
    """Client side user privileges."""

    Player     = 1 << 0
    Moderator  = 1 << 1
    Supporter  = 1 << 2
    Owner      = 1 << 3
    Developer  = 1 << 4
    Tournament = 1 << 5


@unique
class UserIDS(IntEnum): # unused for right now?
    BANCHO_AUTH_FAILED = -1
    OLD_CLIENT = -2
    BANNED = -3
    BANNED2 = -4
    ERROR_OCCURED = -5
    NEEDS_SUPPORTER = -6
    PASSWORD_RESET = -7
    REQUIRES_VERIFICATION = -8

@unique
class Mods(IntFlag):
    NOMOD = 0
    NOFAIL = 1 << 0
    EASY = 1 << 1
    TOUCHSCREEN = 1 << 2 # old: 'NOVIDEO'
    HIDDEN = 1 << 3
    HARDROCK = 1 << 4
    SUDDENDEATH = 1 << 5
    DOUBLETIME = 1 << 6
    RELAX = 1 << 7
    HALFTIME = 1 << 8
    NIGHTCORE = 1 << 9
    FLASHLIGHT = 1 << 10
    AUTOPLAY = 1 << 11
    SPUNOUT = 1 << 12
    AUTOPILOT = 1 << 13
    PERFECT = 1 << 14
    KEY4 = 1 << 15
    KEY5 = 1 << 16
    KEY6 = 1 << 17
    KEY7 = 1 << 18
    KEY8 = 1 << 19
    FADEIN = 1 << 20
    RANDOM = 1 << 21
    CINEMA = 1 << 22
    TARGET = 1 << 23
    KEY9 = 1 << 24
    KEYCOOP = 1 << 25
    KEY1 = 1 << 26
    KEY3 = 1 << 27
    KEY2 = 1 << 28
    SCOREV2 = 1 << 29
    MIRROR = 1 << 30
    
    def __repr__(self) -> str:
        _mod_dict = {
           Mods.NOFAIL: 'NF',
           Mods.EASY: 'EZ',
           Mods.TOUCHSCREEN: 'TD',
           Mods.HIDDEN: 'HD',
           Mods.HARDROCK: 'HR',
           Mods.SUDDENDEATH: 'SD',
           Mods.DOUBLETIME: 'DT',
           Mods.RELAX: 'RX',
           Mods.HALFTIME: 'HT',
           Mods.NIGHTCORE: 'NC',
           Mods.FLASHLIGHT: 'FL',
           Mods.AUTOPLAY: 'AU',
           Mods.SPUNOUT: 'SO',
           Mods.AUTOPILOT: 'AP',
           Mods.PERFECT: 'PF',
           Mods.KEY4: 'K4',
           Mods.KEY5: 'K5',
           Mods.KEY6: 'K6',
           Mods.KEY7: 'K7',
           Mods.KEY8: 'K8',
           Mods.FADEIN: 'FI',
           Mods.RANDOM: 'RN',
           Mods.CINEMA: 'CN',
           Mods.TARGET: 'TP',
           Mods.KEY9: 'K9',
           Mods.KEYCOOP: 'CO',
           Mods.KEY1: 'K1',
           Mods.KEY3: 'K3',
           Mods.KEY2: 'K2',
           Mods.SCOREV2: 'V2',
           Mods.MIRROR: 'MI'
       }
        if not self:
           return 'NM'
            # dt/nc is a special case, as osu! will send
            # the mods as 'DTNC' while only NC is applied.
        if self & Mods.NIGHTCORE:
            self &= ~Mods.DOUBLETIME
        
        return ''.join(v for k, v in _mod_dict.items() if self & k)

@unique
class ServerRankedStatus(IntEnum):
    NotSubmitted = -1
    Pending = 0
    UpdateAvailable = 1
    Ranked = 2
    Approved = 3
    Qualified = 4
    Loved = 5

    @staticmethod
    def from_command(s: str):
        return {
            'rank': ServerRankedStatus.Ranked,
            'love': ServerRankedStatus.Loved,
            'unrank': ServerRankedStatus.Pending,
            'approve': ServerRankedStatus.Approved
        }[s]
    
    @staticmethod
    def to_command(s):
        return {
            ServerRankedStatus.Ranked: 'ranked',
            ServerRankedStatus.Loved: 'loved',
            ServerRankedStatus.Pending: 'unranked',
            ServerRankedStatus.Approved: 'approved'
        }[s]
    
    @staticmethod
    def from_beatconnect(s: str):
        return {
            'ranked': ServerRankedStatus.Ranked
        }[s]

    @staticmethod
    def from_api(status: int):
        return {
            -2: ServerRankedStatus.Pending,
            -1: ServerRankedStatus.NotSubmitted,
            0: ServerRankedStatus.Ranked,
            1: ServerRankedStatus.Ranked,
            2: ServerRankedStatus.Approved,
            3: ServerRankedStatus.Qualified,
            4: ServerRankedStatus.Loved,
        }[status]

@unique
class RankedStatus(IntEnum):
    Ranked = 0
    Pending = 2
    Qualified = 3
    Graveyard = 5
    Ranked2 = 7
    Loved = 8

    @staticmethod
    def to_api(status: int):
        return {
            0: 'ranked',
            2: 'unranked',
            3: 'qualified',
            4: 'all',
            5: 'unranked',
            7: 'ranked',
            8: 'loved',
        }[status]


@unique
class GameMode(IntEnum):
    vn_std   = 0
    vn_taiko = 1
    vn_catch = 2
    vn_mania = 3

    rx_std   = 4
    rx_taiko = 5
    rx_catch = 6

    ap_std   = 7

    @staticmethod
    def from_params(mode: int, mods: int):
        if mods & Mods.RELAX:
            return GameMode(mode + 4)
        elif mods & Mods.AUTOPILOT:
            return GameMode(7)
        else:
            return GameMode(mode)

    @staticmethod
    def to_api(mode: int):
        return ('std', 'taiko', 'ctb', 'mania')[mode]

    @staticmethod
    def to_db(mode):
        return {
            0: ('std', 'reg'),
            1: ('taiko', 'reg'),
            2: ('ctb', 'reg'),
            3: 'mania',
            4: ('std', 'rx'),
            5: ('taiko', 'rx'),
            6: ('ctb', 'rx'),
            7: ('std', 'ap'),
        }[mode]

@unique
class Action(IntEnum):
    """The client's current state."""
    Idle         = 0
    Afk          = 1
    Playing      = 2
    Editing      = 3
    Modding      = 4
    Multiplayer  = 5
    Watching     = 6
    Unknown      = 7
    Testing      = 8
    Submitting   = 9
    Paused       = 10
    Lobby        = 11
    Multiplaying = 12
    OsuDirect    = 13