from base64 import b64decode
from typing import Union
from aiotinydb import AIOTinyDB
from py3rijndael import RijndaelCbc, ZeroPadding
from objects.const import Mods, ScoreStatus, GameMode, DICT_TO_CLASS
from subprocess import run, PIPE
from json import loads
import time
import os

class Score:
    def __init__(self) -> None:
        self.scoreID = int = None
        self.map_md5: str = None
        self.player_name: str = None
        self.userid: int = None
        self.mode: GameMode = None
        self.n300: int = None
        self.n100: int = None
        self.n50: int = None
        self.ngeki: int = None
        self.nkatus: int = None
        self.nmiss: int = None
        self.score: int = None
        self.max_combo: int = None
        self.perfect: bool = None
        self.rank: str = None
        self.mods: Mods = None
        self.passed: bool = None
        self.playtime: float = None
        self.sub_type: ScoreStatus = None
        self.acc: float = None
        self.pp: float = None

    @staticmethod
    async def from_submission(score: dict):
        # i need to learn this at some point
        iv = b64decode(score['iv']).decode('latin_1')
        sscore = b64decode(score['score'])

        key = f'osu!-scoreburgr---------{score["osuver"].decode()}'
        cbc = RijndaelCbc(key, iv, ZeroPadding(32), 32)
        score_details = cbc.decrypt(sscore).decode().split(':')

        s = Score()

        s.map_md5 = score_details[0]
        s.player_name = score_details[1].strip()

        async with AIOTinyDB('./data/users.json') as DB:
            p = DB.get(lambda user: True if user['username'] == s.player_name else False)
            from cache import online
            s.userid = p['userid']
            player = online[p['userid']]
        
        async with AIOTinyDB('./data/scores.json') as DB:
            try:
                alls = DB.all()
                s.scoreID = len(alls)
            except:
                s.scoreID = 1

        s.mode = player.mode
        s.n300 = int(score_details[3])
        s.n100 = int(score_details[4])
        s.n50 = int(score_details[5])
        s.ngeki = int(score_details[6])
        s.nkatus = int(score_details[7])
        s.nmiss = int(score_details[8])
        s.score = int(score_details[9])
        s.max_combo = int(score_details[10])
        s.perfect = score_details[11] != 'False'
        s.rank = score_details[12]
        s.mods = Mods(int(score_details[13]))
        # s.readableMods = Mods.readable(m = int(score_details[13]))
        s.passed = score_details[14] == 'True'
        s.playtime = int(time.time())
        s.sub_type = ScoreStatus.SUBMITTED if s.passed else ScoreStatus.FAILED
        if int(s.mode) > 3:
            s.get_acc(int(s.mode) - 4)
        elif int(s.mode) == 7:
            s.get_acc(0)
        else:
            s.get_acc(s.mode)

        if s.mode in (GameMode.vn_std, GameMode.vn_taiko, GameMode.vn_catch, GameMode.vn_mania) and s.mods & Mods.RELAX:
            s.mode = GameMode(s.mode + 4)
        elif s.mode in (GameMode.vn_std, GameMode.vn_taiko, GameMode.vn_catch, GameMode.vn_mania) and s.mods & Mods.AUTOPILOT:
            s.mode = GameMode(7)
        
        await s.calc_pp()
        
        return s
    
    async def calc_pp(self):
        """
        So for oppai i used, https://github.com/Francesco149/oppai-ng#installing-linux
        from here i made it a default command on linux so probably just use this ^
        """
        if self.mode not in (0, 1, 4, 5, 7): # check if mode not supported man
            self.pp = 0.0
            return # TODO?: add mania and ctb someday

        async with AIOTinyDB('./data/beatmaps.json') as DB:
            beatmap = DB.get(lambda mapp: True if mapp['md5'] == self.map_md5 else False)
            if not beatmap:
                self.pp = 0.0
                return
            beatmap = DICT_TO_CLASS(**beatmap)

        filepath = os.path.abspath(f"./data/beatmaps/{beatmap.filename}") # little weird because we are currently in the data folder lol
        cmd = ['oppai', f'"{filepath}"']

        cmd.append(f'{self.acc:.2f}%')
        cmd.append(f'{self.n100}x100')
        cmd.append(f'{self.n50}x50')
        cmd.append(f'{self.nmiss}xmiss')
        cmd.append(f'{self.max_combo}x')

        mods = self.mods.__repr__()

        if self.mode in (1, 5): # taiko, taikorx
            cmd.append(f'-m1')
            cmd.append(f'-taiko')
        
        if 'TD' in mods: # check if touch screen
            cmd.append(f'-touch')
        
        if self.mods and mods != 'NM':
            cmd.append(f'+{mods.replace("RX", "").replace("AP", "")}')
        
        cmd.append(f'-ojson')

        process = run(
            ' '.join(cmd), shell = True, stdout = PIPE, stderr = PIPE
        )

        output = loads(process.stdout.decode('utf-8', errors='ignore'))
        self.pp = 0.0

        if 'RX' in mods: 
            self.pp = output['aim_pp'] 
        elif 'AP' in mods:
            self.pp = output['acc_pp']
        else:
            self.pp = output['pp']   
    
    def get_acc(self, mode: int):
        if mode == 0: # osu!
            total = sum((self.n300, self.n100, self.n50, self.nmiss))

            if total == 0:
                self.acc = 0.0
                return

            self.acc = 100.0 * sum((
                self.n50 * 50.0,
                self.n100 * 100.0,
                self.n300 * 300.0
            )) / (total * 300.0)

        elif mode == 1: # osu!taiko
            total = sum((self.n300, self.n100, self.nmiss))

            if total == 0:
                self.acc = 0.0
                return

            self.acc = 100.0 * sum((
                self.n100 * 0.5,
                self.n300
            )) / total

        elif mode == 2:
            # osu!catch
            total = sum((self.n300, self.n100, self.n50,
                            self.nkatus, self.nmiss))

            if total == 0:
                self.acc = 0.0
                return

            self.acc = 100.0 * sum((
                self.n300,
                self.n100,
                self.n50
            )) / total

        elif mode == 3:
            # osu!mania
            total = sum((self.n300, self.n100, self.n50,
                            self.ngeki, self.nkatus, self.nmiss))

            if total == 0:
                self.acc = 0.0
                return

            self.acc = 100.0 * sum((
                self.n50 * 50.0,
                self.n100 * 100.0,
                self.nkatus * 200.0,
                (self.n300 + self.ngeki) * 300.0
            )) / (total * 300.0)

# for bot
async def oppai(mapid: int, mods: str, acc: Union[tuple, float] = (100.0, 99.0, 98.0, 97.0, 96.0)):
    msg = []
    async with AIOTinyDB('./data/beatmaps.json') as DB:
        beatmap = DB.get(lambda mapp: True if mapp['mapid'] == mapid else False)
        if not beatmap:
            return ''
    beatmap = DICT_TO_CLASS(**beatmap)
    filepath = os.path.abspath(f"./data/beatmaps/{beatmap.filename}")
    
    if isinstance(acc, tuple):
        for a in acc:
            cmd = ['oppai', f'"{filepath}"', f'{a}%', f'+{mods}', '-ojson']

            process = run(
                ' '.join(cmd), shell = True, stdout = PIPE, stderr = PIPE
            )

            output = loads(process.stdout.decode('utf-8', errors='ignore'))

            if 'pp' not in output:
                msg.append(f'0 PP for {a}%')
            else:
                msg.append(f"{output['pp']:.2f}PP for {a}%")
    else:
        ...
    
    return '\n'.join(msg)