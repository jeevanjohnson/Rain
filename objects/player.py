from objects.const import *
from aiotinydb import AIOTinyDB

class Stats:
    def __init__(self) -> None:
        self.ranked_score = 0
        self.acc = 0
        self.playcount = 0
        self.total_score = 0
        self.rank = 0
        self.pp = 0

class Player:
    def __init__(self, userID: int, version: float, hardwareData: list, loginTime: float) -> None:
        self.username = ''
        self.userid = userID
        self.version = version
        self.hardwareData = [x for x in hardwareData if x]
        self.loginTime = loginTime

        self._privileges = 1
        self.privileges = Privileges(self._privileges)
        self.utc_offset: int = 0
        self.country = (0, 'XX')
        self.location = (0.0, 0.0)
        self.stats = Stats()
        self.pres_filter = PresenceFilter.All

        self.action = Action.Idle
        self.info_text = ''
        self.map_md5 = ''
        self.mods = Mods.NOMOD
        self.mode = GameMode.vn_std
        self.map_id = 0

        self.last_np = 0
        self.max_combo = 0

        self.enqueue = [] # this is when the client wants to get other player's info or whatever

    @property
    def banco_privs(self):
        p = ClientPrivileges(0) # gets a normal player privs
        if self.privileges & Privileges.Normal: # check if they have normal perms
            # we check if its a normal player because we want
            # too give the user free supporter features
            # like direct
            p |= (ClientPrivileges.Player | ClientPrivileges.Supporter)
        return p

    async def update(self):
        async with AIOTinyDB('./data/users.json') as DB:
            x = DB.get(lambda user: True if user['userid'] == self.userid else False)
            self.username = x['username']
            self._privileges = x['privs'] # if self.userid not in (3, 4) else x['privs'] + Privileges.Admin
            self.privileges = Privileges(self._privileges)

            d = GameMode.to_db(self.mode)
            if isinstance(d, tuple):
                s = x[d[0]][d[1]]
            else:
                s = x[d]
            
            self.stats.acc = s['acc']
            self.stats.playcount = s['playcount']
            self.stats.ranked_score = s['ranked_score']
            self.stats.total_score = s['total_score']
            self.stats.rank = s['rank']
            self.stats.pp = s['pp']
            self.max_combo = s['max_combo']

            DB.update(
                {'hwidMd5': self.hardwareData, 'version': self.version},
                lambda user: True if user['username'] == self.username else False
            )