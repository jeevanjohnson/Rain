from enum import IntEnum, IntFlag, unique

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
class UserIDS(IntEnum):
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
class RankedStatus(IntEnum):
    Ranked = 0
    Ranked2 = 7
    Loved = 8
    Qualified = 3
    Pending = 2
    Graveyard = 5

    @staticmethod
    def to_api(status):
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
    def to_api(mode: int):
        return ('std', 'taiko', 'ctb', 'mania')[mode]

    @staticmethod
    def to_db(mode):
        return {
            0: 'std',
            1: 'taiko',
            2: 'ctb',
            3: 'mania',
            4: ('std', 'rx'),
            5: ('taiko', 'rx'),
            6: ('catch', 'rx'),
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