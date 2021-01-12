from aiotinydb import AIOTinyDB
USERS = AIOTinyDB('./data/users.json')
SCORES = AIOTinyDB('./data/scores.json')
BEATMAPS = AIOTinyDB('./data/beatmaps.json')

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from objects.score import Score

def is_best_score(score: 'Score'):
    ...

def remove_duplicates(s: list) -> list:
    temp = []
    ss = []
    for x in s:
        if x['userid'] not in temp:
            temp.append(x['userid'])
            ss.append(x)
    
    return ss

def addRanks(l: list) -> list:
    cop = l.copy()
    rank = 0
    for x in l:
        rank += 1
        i = l.index(x)
        x['rank'] = rank
        cop[i] = x
    
    return cop

def get_scores(userid: int, l: list) -> dict:
    for x in l:
        if x['userid'] == userid:
            return x

async def get_rank_for_pp(pp: float, key: Union[tuple, str]) -> int:
    if isinstance(key, tuple):
        fake_player = {
            key[0]: {key[1]: {'pp': pp}},
            'userid': 'yes'
        }
    else:
        fake_player = {
            key[0]: {'pp': pp},
            'userid': 'yes'
        }
    
    def s(sc):
        if isinstance(key, tuple):
            return sc[key[0]][key[1]]['pp']
        else:
            return sc[key[0]]['pp']

    async with USERS as DB:
        x = DB.all()
        x.append(fake_player)
        r = addRanks(sorted(x, key = s, reverse = True))
        for z in r:
            if 'userid' in z:
                if z['userid'] == 'yes':
                    return z['rank']

def get_rank_for_score(score: 'Score', scores: list) -> int:
    rank = 0
    if not scores:
        return rank + 1
    for s in scores:
        rank += 1
        if s['pp'] < score.pp:
            rank -= 1
            if rank < 1:
                rank = 1
            return rank 
