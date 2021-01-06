import time
from objects.const import Privileges, ClientPrivileges
from enum import IntEnum, IntFlag, unique

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
class GameMode(IntEnum):
    vn_std   = 0
    vn_taiko = 1
    vn_catch = 2
    vn_mania = 3

    rx_std   = 4
    rx_taiko = 5
    rx_catch = 6

    ap_std   = 7

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

class Stats:
    def __init__(self, userID: int) -> None:
        ...

class Player:
    def __init__(self, userID: int, version: float, hardwareData: list, loginTime: float) -> None:
        self.username: str = 'owo' # soon
        self.userid = userID
        self.version = version
        self.hardwareData = hardwareData
        loginTime = loginTime

        self._privileges = 1 # raw priv number
        self.privileges = Privileges(self._privileges)
        self.utc_offset: int = 0
        self.country = (0, 'XX')
        self.location = (0.0, 0.0)
        self.stats = Stats(userID)

        self.action = Action.Idle
        self.info_text = ''
        self.map_md5 = ''
        self.mods = Mods.NOMOD
        self.mode = GameMode.rx_std
        self.map_id = 0

        self.queue = [] # this is when the client wants to get other player's info or whatever

    @property
    def banco_privs(self):
        p = ClientPrivileges(0) # gets a normal player privs
        if self.privileges & Privileges.Normal: # check if they have normal perms
            # we check if its a normal player because we want
            # too give the user free supporter features
            # like direct
            p |= (ClientPrivileges.Player | ClientPrivileges.Supporter)

        return p

    def update(self):
        ...
