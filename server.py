from objects.leaderboards import Leaderboard
from objects.score import Score
from objects.beatmap import Beatmap
from WebLamp import Connection, printc
from WebLamp.utlies import Colors
from serverwrapper import OsuServer
from packets import PacketIDS
from typing import Union
from objects.player import Player
from objects.const import *
from helpers import *
from functools import lru_cache
from const import process_cmd
from objects.score import oppai
import aiohttp
import packets
import config
import os
import cache
import time
import hashlib 
import re
import json

regex = {
    'email': re.compile(r'^\w+@\w+.\w+$'),
    'beatmap': re.compile(r'https:\/\/osu\.ppy\.sh/b/(?P<mapid>[0-9]*)'),
}

s = OsuServer()
bancho = ("c.ppy.sh", "c4.ppy.sh", "c5.ppy.sh", "c6.ppy.sh")
web = ["osu.ppy.sh"]
avatar = ["a.ppy.sh"]

DIRECT_API = "https://beatconnect.io/api"

loginMsg = '\n'.join([
    "Welcome to Rain!",
    "",
    "This was made for the sole purpose of learning how to make a server.",
    "if your here welcome and enjoy your time.",
    "There are currently {} online users"
])

@s.handler(target = '/users', domains = web, method = ['POST'])
async def accountCreation(conn: Connection) -> bytes:
    body = b''
    errors = {
        'username': [],
        'user_email': [],
        'password': [],
    }

    credentials = conn.request['multipart']
    username = credentials[1][1][:-2]
    email = credentials[2][1][:-2]
    password = credentials[3][1][:-2]
    check = credentials[4][1][:-2] # idk what this does for now

    # you would have to do more checks but im not gonna do that lol
    if not regex['email'].match((email := email.decode())):
        errors['user_email'].append('Please enter a valid email.')
    
    if len((username := username.decode())) < 4:
        errors['username'].append(
            'Username is too short. Please make a username of at least 4 character'
        )
    
    async with AIOTinyDB('./data/users.json') as DB:
        if DB.get(lambda x: True if x['username'].lower() == username else False):
            errors['username'].append(
            'Username already exists!'
        )
        if DB.get(lambda x: True if x['email'] == email else False):
            errors['username'].append(
            'email already exists! Are you sure your making your first account ever? :D'
        )
    
    if len(password.decode()) < 2:
        errors['password'].append(
            'Password is too short. Please make a password of at least 2 character'
        )
    
    if True in [bool(errors[x]) for x in errors]:
        conn.set_status(400)
        body += json.dumps(
            {'form_error': {'user': errors}}
        ).encode()
        conn.set_body(body)
        return conn.response
    
    if check == b'0':
        password = hashlib.md5(password).hexdigest()
        async with AIOTinyDB('./data/users.json') as db:
            users = db.all()
            db.insert({
                'userid': len(users) + 4,
                'username': username,
                'passwordmd5': password,
                'email': email,
                'version': 0,
                'hwidMd5': [],
                'privs': 1,
                'std': {
                    'reg': {
                        'ranked_score': 0, 'acc': 0, 
                        'playcount': 0, 'total_score': 0, 
                        'rank': len(users) + 1, 'pp': 0, 
                        'max_combo': 0,
                        },
                    'rx': {
                        'ranked_score': 0, 'acc': 0, 
                        'playcount': 0, 'total_score': 0, 
                        'rank': len(users) + 1, 'pp': 0,
                        'max_combo': 0,
                    },
                    'ap': {
                        'ranked_score': 0, 'acc': 0, 
                        'playcount': 0, 'total_score': 0, 
                        'rank': len(users) + 1, 'pp': 0,
                        'max_combo': 0,
                    }
                },
                'taiko': {
                    'reg': {
                        'ranked_score': 0, 'acc': 0, 
                        'playcount': 0, 'total_score': 0, 
                        'rank': len(users) + 1, 'pp': 0,
                        'max_combo': 0,
                    },
                    'rx': {
                        'ranked_score': 0, 'acc': 0, 
                        'playcount': 0, 'total_score': 0, 
                        'rank': len(users) + 1, 'pp': 0 ,
                        'max_combo': 0,
                    }
                },
                'ctb': {
                    'reg': {
                        'ranked_score': 0, 'acc': 0, 
                        'playcount': 0, 'total_score': 0, 
                        'rank': len(users) + 1, 'pp': 0,
                        'max_combo': 0,
                    },
                    'rx': {
                        'ranked_score': 0, 'acc': 0, 
                        'playcount': 0, 'total_score': 0, 
                        'rank': len(users) + 1, 'pp': 0,
                        'max_combo': 0,
                    }
                },
                'mania': {
                        'ranked_score': 0, 'acc': 0, 
                        'playcount': 0, 'total_score': 0, 
                        'rank': len(users) + 1, 'pp': 0,
                        'max_combo': 0, 
                    }
                })
        printc(f'{username} has registered an account!', Colors.Blue)
        body += b'ok'
    else:
        body += b'ok'
    
    conn.set_status(200)
    conn.set_body(body)
    return conn.response

@s.handler(target = '/web/osu-submit-modular-selector.php', domains = web)
async def scoreSub(conn: Connection) -> bytes:
    # When osu sends 'replay bytes'
    # it doesn't actually send replay  bytes
    # it sends cursor movements or frames as a proper word
    #TODO: check if map is loved/unranked 
    # if so don't update stats besides total score
    conn.set_status(200)
    m = conn.request['multipart']
    score = await Score.from_submission({
        'iv': m[12][1][:-2], 'score': m[3][1][:-2],
        'osuver': m[9][1][:-2]
    })
    if score.map_md5 in cache.beatmap:
        bmap = cache.beatmap[score.map_md5]
    else:
        bmap = await Beatmap.from_db(lambda beatmap: True if beatmap['md5'] == score.map_md5 else False)
    
    p: Player = cache.online[score.userid]
    p.last_play = score

    if not bmap:
        ... # should never happen
    
    if not Privileges.Whitelisted & p.privileges and score.sub_type & ScoreStatus.SUBMITTED:
        cap = ()
        if p.mode in (GameMode.rx_std, GameMode.vn_std, GameMode.ap_std):
            cap = config.std_pp_cap
        elif p.mode in (GameMode.vn_taiko, GameMode.rx_taiko):
            cap = config.taiko_pp_cap

        if cap and score.pp > cap[int(bool(score.mods & Mods.RELAX)) + int(bool(score.mods & Mods.AUTOPILOT))]:
            ...
            # TODO: Restrict or Ban the user depending on how many times they've been restricted
        
    if score.sub_type in (ScoreStatus.FAILED, ScoreStatus.BEST):
        conn.set_body(b'error: no')
        return conn.response
    
    if bmap['rankedstatus'] not in (ServerRankedStatus.Ranked, ServerRankedStatus.Pending): # check if map is loved

        d = GameMode.to_db(p.mode)

        chart = [ #TODO: change system for loved
        "beatmapId:{mapid}|beatmapSetId:{setid}|beatmapPlaycount:0|beatmapPasscount:0|approvedDate:{approvedDate}".format(**bmap),
        f"chartId:beatmap|chartUrl:https://osu.ppy.sh/b/{bmap['mapid']}|chartName:Beatmap Ranking|rankBefore:|rankAfter:|maxComboBefore:|maxComboAfter:|accuracyBefore:|accuracyAfter:|rankedScoreBefore:|rankedScoreAfter:0|ppBefore:|ppAfter:|onlineScoreId:{score.scoreID}",
        f"chartId:overall|chartUrl:https://osu.ppy.sh/u/{p.userid}|chartName:Overall Ranking|rankBefore:|rankAfter:|rankedScoreBefore:0|rankedScoreAfter:0|totalScoreBefore:{p.stats.total_score}|totalScoreAfter:{p.stats.total_score + score.score}|maxComboBefore:|maxComboAfter:|accuracyBefore:|accuracyAfter:|ppBefore:|ppAfter:|achievements-new:|onlineScoreId:{score.scoreID}"
        ]

        with open(f'./data/replays/{score.scoreID}.osr', 'wb') as f:
            f.write(
                m[13][2][:-2]
            )

        p.stats.total_score +=  score.score

        async with AIOTinyDB('./data/users.json') as DB:
        
            for doc in (docs := DB.search(lambda x: x['userid'] == p.userid)):
                if isinstance(d, tuple):
                    doc[d[0]][d[1]]['pp'] = p.stats.pp
                    doc[d[0]][d[1]]['acc'] = p.stats.acc
                    doc[d[0]][d[1]]['playcount'] = p.stats.playcount
                    doc[d[0]][d[1]]['total_score'] = p.stats.total_score
                    doc[d[0]][d[1]]['ranked_score'] = p.stats.ranked_score
                    doc[d[0]][d[1]]['max_combo'] = p.max_combo
                    doc[d[0]][d[1]]['rank'] = p.stats.rank
                else:
                    doc[d]['pp'] = p.stats.pp
                    doc[d]['acc'] = p.stats.acc
                    doc[d]['playcount'] = p.stats.playcount
                    doc[d]['total_score'] = p.stats.total_score
                    doc[d]['ranked_score'] = p.stats.ranked_score
                    doc[d]['max_combo'] = p.max_combo
                    doc[d]['rank'] = p.stats.rank

            DB.write_back(docs)
        
        p.enqueue.append(packets.userStats(p))

        async with AIOTinyDB('./data/scores.json') as DB:
            x = DB.get(lambda sc: True if sc == score.__dict__ else False)
            if x:
                ... #TODO: restrict for duplicated score
            
            DB.insert(score.__dict__)

        if score.mods & Mods.RELAX or score.mods & Mods.AUTOPILOT:
            conn.set_body(b'error: no')
        else:
            conn.set_body('\n'.join(chart).encode())
        return conn.response

    if score.sub_type & ScoreStatus.SUBMITTED and \
    score.mods & Mods.RELAX or score.mods & Mods.AUTOPILOT:
        
        async with AIOTinyDB('./data/scores.json') as DB:
            x = DB.get(lambda sc: True if sc == score.__dict__ else False)
            if x:
                ... # restrict for duplicated score
            
            DB.insert(score.__dict__)
        
        # if not is_best_score(score):
        #     conn.set_body(b'error: no')
        #     return conn.response
        
        if score.mode in (GameMode.vn_std, GameMode.vn_taiko, GameMode.vn_catch, GameMode.vn_mania) and score.mods & Mods.RELAX:
            p.mode = GameMode(p.mode + 4) 
        elif score.mode in (GameMode.vn_std, GameMode.vn_taiko, GameMode.vn_catch, GameMode.vn_mania) and score.mods & Mods.AUTOPILOT:
            p.mode = GameMode(7)
            d = Mods.AUTOPILOT
        
        if score.mods & Mods.RELAX:
            d = Mods.RELAX
        elif score.mods & Mods.AUTOPILOT:
            d = Mods.AUTOPILOT
        
        previous_pp = p.stats.pp
        async with AIOTinyDB('./data/scores.json') as DB:
            mm = DB.search(
                lambda x: True if x['userid'] == p.userid and x['mods'] & d and ScoreStatus(x['sub_type']) == ScoreStatus.SUBMITTED else False
            )
        
        # calc acc & pp
        p.stats.pp = 0

        if not mm:
            p.stats.pp += round(score.pp)
            previous_acc = score.acc
            p.stats.acc = score.acc
        else:
            for i, row in enumerate((allscores := remove_duplicatess(sorted(mm, key = lambda sc: sc['pp'], reverse = True)))):
                p.stats.pp += row['pp'] * 0.95 ** i 
        
            p.stats.pp = round(p.stats.pp)
        
            t = 0
            for sc in allscores:
                t += sc['acc']
            
            previous_acc = p.stats.acc
            p.stats.acc = t / len(allscores)
            

        # total score
        previous_tscore = p.stats.total_score
        p.stats.total_score += score.score

        # max combo
        previous_maxCombo = p.max_combo
        p.max_combo = score.max_combo if score.max_combo and score.max_combo > p.max_combo else p.max_combo

        p.stats.playcount += 1 # playcount

        previous_rank = p.stats.rank

        d = GameMode.to_db(p.mode)
        p.stats.rank = await get_rank_for_pp(p.stats.pp, key = d) # rank

        async with AIOTinyDB('./data/users.json') as DB:
        
            for doc in (docs := DB.search(lambda x: x['userid'] == p.userid)):
                if isinstance(d, tuple):
                    doc[d[0]][d[1]]['pp'] = p.stats.pp
                    doc[d[0]][d[1]]['acc'] = p.stats.acc
                    doc[d[0]][d[1]]['playcount'] = p.stats.playcount
                    doc[d[0]][d[1]]['total_score'] = p.stats.total_score
                    doc[d[0]][d[1]]['ranked_score'] = p.stats.ranked_score
                    doc[d[0]][d[1]]['max_combo'] = p.max_combo
                    doc[d[0]][d[1]]['rank'] = p.stats.rank
                else:
                    doc[d]['pp'] = p.stats.pp
                    doc[d]['acc'] = p.stats.acc
                    doc[d]['playcount'] = p.stats.playcount
                    doc[d]['total_score'] = p.stats.total_score
                    doc[d]['ranked_score'] = p.stats.ranked_score
                    doc[d]['max_combo'] = p.max_combo
                    doc[d]['rank'] = p.stats.rank

            DB.write_back(docs)
        
        p.enqueue.append(packets.userStats(p))
        
        with open(f'./data/replays/{score.scoreID}.osr', 'wb') as f:
            f.write(
                m[13][2][:-2]
            )

        conn.set_body(b'error: no')
        return conn.response
    
    with open(f'./data/replays/{score.scoreID}.osr', 'wb') as f:
        f.write(
            m[13][2][:-2]
        )
    
    def x(scare):
        if scare['map_md5'] == bmap['md5'] and \
        ScoreStatus(scare['sub_type']) == ScoreStatus.SUBMITTED and \
        not Mods(scare['mods']) & Mods.RELAX and \
        not Mods(scare['mods']) & Mods.AUTOPILOT:
            return True
        else:
            return False
    
    async with AIOTinyDB('./data/scores.json') as DB:
        scores = DB.search(x)
        scores = addRanks((xx := remove_duplicates(sorted(scores, key = lambda sc: sc['pp'], reverse = True))))
        scores = get_scores(p.userid, scores)
        score.rankForScore = get_rank_for_score(score, xx)
    
    # TODO: fill in charts
    chart = [
        "beatmapId:{mapid}|beatmapSetId:{setid}|beatmapPlaycount:0|beatmapPasscount:0|approvedDate:{approvedDate}".format(**bmap),
    ]
    if not scores:
        chart.append(
            #TODO: Ranked Score
            f"chartId:beatmap|chartUrl:https://osu.ppy.sh/b/{bmap['mapid']}|chartName:Beatmap Ranking|rankBefore:|rankAfter:{score.rankForScore}|maxComboBefore:|maxComboAfter:{score.max_combo}|accuracyBefore:|accuracyAfter:{score.acc:.2f}|rankedScoreBefore:|rankedScoreAfter:0|ppBefore:|ppAfter:{score.pp:.2f}|onlineScoreId:{score.scoreID}"
        )
    else:
        chart.append(
            #TODO: Ranked Score
            f"chartId:beatmap|chartUrl:https://osu.ppy.sh/b/{bmap['mapid']}|chartName:Beatmap Ranking|rankBefore:|rankAfter:{score.rankForScore}|maxComboBefore:{scores['max_combo']}|maxComboAfter:{score.max_combo}|accuracyBefore:{scores['acc']:.2f}|accuracyAfter:{score.acc:.2f}|rankedScoreBefore:|rankedScoreAfter:0|ppBefore:{scores['pp']:.2f}|ppAfter:{score.pp:.2f}|onlineScoreId:{score.scoreID}"
        )

    previous_pp = p.stats.pp
    async with AIOTinyDB('./data/scores.json') as DB:
        mm = DB.search(
            lambda x: True if x['userid'] == p.userid and not x['mods'] & Mods.RELAX and not x['mods'] & Mods.AUTOPILOT and ScoreStatus(x['sub_type']) == ScoreStatus.SUBMITTED else False
        )
    
    # calc acc & pp
    p.stats.pp = 0

    if not mm:
        p.stats.pp += round(score.pp)
        previous_acc = score.acc
        p.stats.acc = score.acc
    else:
        for i, row in enumerate((allscores := remove_duplicatess(sorted(mm, key = lambda sc: sc['pp'], reverse = True)))):
            p.stats.pp += row['pp'] * 0.95 ** i 
    
        p.stats.pp = round(p.stats.pp)
    
        t = 0
        for sc in allscores:
            t += sc['acc']
        
        previous_acc = p.stats.acc
        p.stats.acc = t / len(allscores)
        

    # total score
    previous_tscore = p.stats.total_score
    p.stats.total_score += score.score

    # max combo
    previous_maxCombo = p.max_combo
    p.max_combo = score.max_combo if score.max_combo and score.max_combo > p.max_combo else p.max_combo

    p.stats.playcount += 1 # playcoun

    previous_rank = p.stats.rank

    d = GameMode.to_db(p.mode)
    p.stats.rank = await get_rank_for_pp(p.stats.pp, key = d) # rank

    async with AIOTinyDB('./data/users.json') as DB:
    
        for doc in (docs := DB.search(lambda x: x['userid'] == p.userid)):
            if isinstance(d, tuple):
                doc[d[0]][d[1]]['pp'] = p.stats.pp
                doc[d[0]][d[1]]['acc'] = p.stats.acc
                doc[d[0]][d[1]]['playcount'] = p.stats.playcount
                doc[d[0]][d[1]]['total_score'] = p.stats.total_score
                doc[d[0]][d[1]]['ranked_score'] = p.stats.ranked_score
                doc[d[0]][d[1]]['max_combo'] = p.max_combo
                doc[d[0]][d[1]]['rank'] = p.stats.rank
            else:
                doc[d]['pp'] = p.stats.pp
                doc[d]['acc'] = p.stats.acc
                doc[d]['playcount'] = p.stats.playcount
                doc[d]['total_score'] = p.stats.total_score
                doc[d]['ranked_score'] = p.stats.ranked_score
                doc[d]['max_combo'] = p.max_combo
                doc[d]['rank'] = p.stats.rank
                
        DB.write_back(docs)
    
    p.enqueue.append(packets.userStats(p))

    chart.append(
        #TODO: Ranked Score
        f"chartId:overall|chartUrl:https://osu.ppy.sh/u/{p.userid}|chartName:Overall Ranking|rankBefore:{previous_rank}|rankAfter:{p.stats.rank}|rankedScoreBefore:0|rankedScoreAfter:0|totalScoreBefore:{previous_tscore}|totalScoreAfter:{p.stats.total_score}|maxComboBefore:{previous_maxCombo}|maxComboAfter:{p.max_combo}|accuracyBefore:{previous_acc}|accuracyAfter:{p.stats.acc}|ppBefore:{previous_pp}|ppAfter:{p.stats.pp}|achievements-new:|onlineScoreId:{score.scoreID}"
    )
    
    async with AIOTinyDB('./data/scores.json') as DB:
        x = DB.get(lambda sc: True if sc == score.__dict__ else False)
        if x:
            ... #TODO: restrict for duplicated score
        
        DB.insert(score.__dict__)

    conn.set_body('\n'.join(chart).encode())
    return conn.response

@s.handler(target = '/web/osu-osz2-getscores.php', domains = web)
async def leaderboard(conn: Connection) -> bytes:
    conn.set_status(200)
    body = b''
    params = conn.request['params']
    p: Player = await cache.from_name(params['us'])
    if not p:
        return b''
    map_md5 = params['c']
    mods = Mods(int(params['mods']))
    mode = GameMode.from_params(int(params['m']), mods)
    map_set_id = int(params['i'])
    rank_type = RankingType(int(params['v']))
    filename = params['f'].replace('+', ' ').replace('%5b', '').replace('%5d', '')

    if p.mode != mode:
        p.mode = mode
        await p.update()
        p.enqueue.append(packets.userStats(p))
    
    lb = []
    async with AIOTinyDB('./data/beatmaps.json') as DB:
        if map_md5 in cache.beatmap:
            m = cache.beatmap[map_md5]
            lb.append(f'{m["rankedstatus"]}|false')
        elif (m := DB.get(lambda bmap: True if bmap['md5'] == map_md5 else False)) and \
        os.path.exists(f'./data/beatmaps/{filename}'):
            lb.append(f'{m["rankedstatus"]}|false')
            cache.beatmap[map_md5] = m
        elif (m := await Beatmap.from_md5(map_md5)):
            lb.append(f'{m.rankedstatus}|false')
            cache.beatmap[map_md5] = m.__dict__
            DB.insert(m.__dict__)
        elif os.path.exists(f'./data/beatmaps/{filename}'):
            lb.append(f'{ServerRankedStatus.UpdateAvailable}|false')
        else:
            lb.append(f'{ServerRankedStatus.NotSubmitted}|false')
    
    leader = Leaderboard()
    leader.md5 = map_md5
    leader.user = p
    leader.mods = mods
    if mods & Mods.RELAX or mods & Mods.AUTOPILOT:
        if mods & Mods.RELAX:
            x = Mods.RELAX
        else:
            x = Mods.AUTOPILOT
        cond = lambda score: score['pp']
        Skey = lambda score: bool(
            score['map_md5'] == map_md5 and 
            score['passed'] and
            GameMode(score['mode']) == mode and
            Mods(score['mods']) & x and
            ScoreStatus(score['sub_type']) == ScoreStatus.SUBMITTED
        )
    else:
        cond = lambda score: score['score']
        Skey = lambda score: bool(
            score['map_md5'] == map_md5 and 
            score['passed'] and
            GameMode(score['mode']) == mode and
            not Mods(score['mods']) & Mods.RELAX and
            not Mods(score['mods']) & Mods.AUTOPILOT and
            ScoreStatus(score['sub_type']) == ScoreStatus.SUBMITTED
        )
    
    if rank_type == RankingType.Top:
        await leader.from_top(Skey, cond)
    elif rank_type == RankingType.Mods:
        leader.mods = mods
        await leader.from_mods(Skey, cond)
    elif rank_type == RankingType.Friends:
        leader.userids = tuple(p.friends)
        await leader.from_friends(Skey, cond)
    
    if len(leader.lb) < 5:
        conn.set_body('\n'.join(lb).encode())
        return conn.response
    else:
        conn.set_body(repr(leader).encode())
        return conn.response

@s.handler(target = '/web/osu-search.php', domains = web)
async def direct(conn: Connection) -> bytes:
    args = conn.request['params']
    url = f'{config.mirror}/api/search/'
    params = {
        'token': config.api_keys['beatconnect']
    }

    if args['q'] and args['q'] != 'Newest':
        params['q'] = args['q'].replace('+', ' ')

    if args['m'] != '-1':
        params['m'] = GameMode.to_api(int(args['m']))

    params['s'] = RankedStatus.to_api(int(args['r']))

    async with aiohttp.request('GET', url, params = params) as req:
        if not req or req.status != 200 or not (r := await req.json()):
            return b"Failed to find maps!"

    beatmaps = r['beatmaps']
    lbeatmaps = len(beatmaps)
    maps = [f"{'101' if lbeatmaps == 100 else lbeatmaps}"]
    
    for bmap in beatmaps:
        diffs = []
        for row in sorted(bmap['beatmaps'], key = lambda x: x['difficulty']):
            diffs.append(
                '[{difficulty:.2f}⭐] {version} {{CS{cs} OD{accuracy} AR{ar} HP{drain}}}@{mode_int}'.format(
                **row)
            )

        diffs = ','.join(diffs)
        maps.append(
            '{id}.osz|{artist}|{title}|{creator}|'
            '{ranked}|10.0|{last_updated}|{id}|'
            '0|0|0|0|0|{diffs}'.format(**bmap, diffs=diffs)
        ) # 0s are threadid, has_vid, has_story, filesize, filesize_novid

    conn.set_status(200)
    conn.set_body('\n'.join(maps).encode())
    return conn.response

@s.handler(target = PacketIDS.OSU_RECEIVE_UPDATES, domains = bancho)
async def receiveUpdates(conn: Connection, p: Union[Player, bool]) -> bytes:
    conn.set_status(200)
    body = b''
    if not p:
        body += packets.notification('Server restarting!') 
        body += packets.systemRestart()
        conn.set_body(body)
        return conn.response
    if p.enqueue:
        for x in p.enqueue:
            body += x
        p.enqueue = []

    value = packets.read_packet(conn.request['body'], 'updates')
    if value not in list(PresenceFilter):
        return b''
    
    p.pres_filter = PresenceFilter(value)
    conn.set_body(body)
    return conn.response

@s.handler(target = PacketIDS.OSU_PART_LOBBY, domains = bancho)
async def partLobby(conn: Connection, p: Union[Player, bool]) -> bytes:
    # get out of lobby?
    conn.set_status(200)
    body = b''
    if not p:
        body += packets.notification('Server restarting!') 
        body += packets.systemRestart()
        conn.set_body(body)
        return conn.response
    
    print(PacketIDS.OSU_PART_LOBBY.name)

    conn.set_body(body)
    return conn.response

@s.handler(target = PacketIDS.OSU_CHANNEL_PART, domains = bancho)
async def channelPart(conn: Connection, p: Union[Player, bool]) -> bytes:
    # get out of channel
    conn.set_status(200)
    body = b''
    if not p:
        body += packets.notification('Server restarting!') 
        body += packets.systemRestart()
        conn.set_body(body)
        return conn.response
    
    channelname = packets.read_packet(conn.request['body'], 'string')
    body += packets.channelKick(channelname)
    
    conn.set_body(body)
    return conn.response

@s.handler(target = PacketIDS.OSU_REQUEST_STATUS_UPDATE, domains = bancho)
async def statusUpdate(conn: Connection, p: Union[Player, bool]) -> bytes:
    conn.set_status(200)
    body = b''
    if not p:
        body += packets.notification('Server restarting!') 
        body += packets.systemRestart()
        conn.set_body(body)
        return conn.response
    if p.enqueue:
        for x in p.enqueue:
            body += x
        p.enqueue = []
        
    for player in cache.online:
        player = cache.online[player]
        if player.userid != p.userid:
            body += packets.userStats(player)
    
    conn.set_body(body)
    return conn.response

@s.handler(target = PacketIDS.OSU_USER_STATS_REQUEST, domains = bancho)
async def action(conn: Connection, p: Union[Player, bool]) -> bytes:
    conn.set_status(200)
    body = b''
    if not p:
        body += packets.notification('Server restarting!') 
        body += packets.systemRestart()
        conn.set_body(body)
        return conn.response
    if p.enqueue:
        for x in p.enqueue:
            body += x
        p.enqueue = []

    userids = packets.read_packet(conn.request['body'], 'list_i32')
    users = await cache.from_userids(userids)
    for key in users:
        player = cache.online[key]
        player.enqueue.append(packets.userStats(player))
    conn.set_body(body)
    return conn.response

@s.handler(target = PacketIDS.OSU_SEND_PRIVATE_MESSAGE, domains = bancho)
async def privmsg(conn: Connection, p: Union[Player, bool]) -> bytes:
    conn.set_status(200)
    body = b''
    if not p:
        body += packets.notification('Server restarting!') 
        body += packets.systemRestart()
        conn.set_body(body)
        return conn.response
    msg = packets.read_packet(conn.request['body'], 'message')
    target = await cache.from_name(msg[2])

    if msg[1].startswith("\x01ACTION"):
        x = regex['beatmap'].search(msg[1])
        p.last_np = int(x['mapid'] or '0')
        if target.userid == 3: # if its the bot
            m = await oppai(p.last_np, Mods(p.mods).__repr__())
            body += packets.sendMessage(
                target.username, m, p.username, target.userid
            )
    
    if target.userid != 3: # if its not a bot
        target.enqueue.append(packets.sendMessage(
            p.username, msg[1], msg[2], p.userid
        ))
        conn.set_body(body)
        return conn.response
    
    if msg[1].startswith(config.prefix):
        if not (x := await process_cmd(msg[1], p)):
            body += b''
        else:
            body += packets.sendMessage(
                target.username, x, p.username, target.userid
            )
    
    conn.set_body(body)
    return conn.response

@s.handler(target = PacketIDS.OSU_SEND_PUBLIC_MESSAGE, domains = bancho)
async def publicmsg(conn: Connection, p: Union[Player, bool]) -> bytes:
    conn.set_status(200)
    body = b''
    if not p:
        body += packets.notification('Server restarting!') 
        body += packets.systemRestart()
        conn.set_body(body)
        return conn.response

    # 0: client
    # 1: msg
    # 2: target
    # 3: client_id
    msg = packets.read_packet(conn.request['body'], 'message')
    conn.set_status(200)
    for key in cache.online:
        if key == p.userid:
            continue
        client = cache.online[key]

        client.enqueue.append(packets.sendMessage(p.username, msg[1], msg[2], p.userid))
    
    if msg[1].startswith("\x01ACTION"):
        x = regex['beatmap'].search(msg[1])
        p.last_np = int(x['mapid'])

    conn.set_body(body)
    return conn.response

@s.handler(target = PacketIDS.OSU_CHANGE_ACTION, domains = bancho)
async def action(conn: Connection, p: Union[Player, bool]) -> bytes:
    # action: 'unB'
    # info_text: string
    # map_md5: string
    # mods: 'unI'
    # mode: 'unB'
    # map_id: 'int'
    
    conn.set_status(200)
    body = b''
    if not p:
        body += packets.notification('Server restarting!') 
        body += packets.systemRestart()
        conn.set_body(body)
        return conn.response
    if p.enqueue:
        for x in p.enqueue:
            body += x
        p.enqueue = []
    
    actions = packets.read_packet(conn.request['body'], 'action')
    p.action = actions['action']
    p.info_text = actions['info_text']
    p.map_md5 = actions['map_md5']
    p.mods = actions['mods']
    p.mode = actions['mode']
    p.map_id = actions['map_id']
    
    p.enqueue.append(packets.userStats(p))

    conn.set_body(body)
    return conn.response

@s.handler(target = PacketIDS.OSU_CHANNEL_JOIN, domains = bancho)
async def channelJoin(conn: Connection, p: Union[Player, bool]) -> bytes:
    # kinda broken
    channelName = packets.read_packet(conn.request['body'], 'channelJoin')
    if not (x := await cache.get_channel_from_name(channelName)):
        conn.set_status(404)
        body = b'no channel found my man'
    else:
        conn.set_status(200)
        body = packets.channelStart()
        body += packets.channelJoin(channelName)
        body += packets.channelInfo(x[0], x[1], x[2])

    conn.set_body(body)
    return conn.response

@s.handler(target = r'^/d/(?P<setid>[0-9]*)$', domains = web)
@lru_cache(maxsize=None)
async def download(conn: Connection) -> bytes:
    conn.set_status(200)
    setid = int(conn.args['setid'])
    async with aiohttp.request('GET', f'{config.mirror}/b/{setid}') as req:
        if not req or req.status != 200:
            conn.set_body(b"can't retrive map")
            return conn.response
        
        conn.set_body(await req.content.read())
    return conn.response

@s.handler(target = r'^/(?P<userid>[0-9]*)$', domains = avatar)
@lru_cache(maxsize=None)
async def ava(conn: Connection) -> bytes:
    conn.set_status(200)
    userid = int(conn.args['userid'])

    if os.path.exists(f'./data/avatars/{userid}.png'):
        with open(f'./data/avatars/{userid}.png', 'rb') as f:
            pfp = f.read()
    else:
        with open(f'./data/avatars/-1.png', 'rb') as f:
            pfp = f.read()
    
    conn.set_body(pfp)
    return conn.response

@s.handler(target = PacketIDS.OSU_PING, domains = bancho)
async def pong(conn: Connection, p: Union[Player, bool]) -> bytes:
    conn.set_status(200)
    body = b''
    if not p:
        body += packets.notification('Server restarting!') 
        body += packets.systemRestart()
        conn.set_body(body)
        return conn.response
    if p.enqueue:
        for x in p.enqueue:
            body += x
        p.enqueue = []
    conn.set_body(body)
    return conn.response

@s.handler(target = PacketIDS.OSU_LOGOUT, domains = bancho)
async def logout(conn: Connection, p: Union[Player, bool]) -> bytes:
    conn.set_status(200)
    if p:
        if (time.time() - p.loginTime) < 3:
            return b''
        del cache.online[p.userid]
        conn.set_body(packets.logout(p.userid))
        printc(f'{p.username} has logged out!', Colors.Blue)
    return conn.response

@s.handler(target = 'banchologin', domains = bancho)
async def login(conn: Connection) -> bytes:
    body = b''
    userid = -1
    # Getting all credentials details
    credentials = conn.request['body'].decode().replace('\n', '|').split('|', 5)
    credentials[2] = float(credentials[2][1:])
    credentials[5] = credentials[5].replace('|', ':').split(':')

    # 0 username
    # 1 password (hashed in md5)
    # 2 game version
    # 3 ?
    # 4 ?
    # 5 hardware data

    async with AIOTinyDB('./data/users.json') as DB:
        x = DB.get(lambda x: True if x['username'] == credentials[0] else False)
        if not x:
            pass
        elif x and (x['username'], x['passwordmd5']) == (credentials[0], credentials[1]):
            userid = x['userid']
        
    if userid < 0:
        conn.set_status(200)
        conn.add_header('cho-token', userid)
        body += packets.userID(userid)
        conn.set_body(body)   
        return conn.response
        
    if userid in cache.online:
        userid = -1
        body += packets.userID(userid)
        body += packets.notification("Your account is already logged in from somewhere else!")
    else:    
        body += packets.userID(userid)
        
        p = Player(
            userid, credentials[2], credentials[5], time.time()
        )
        await p.update()
        
        body += packets.menuIcon('|'.join(config.menuicon))
        body += packets.notification(loginMsg.format(len(cache.online) + 1))
        body += packets.protocolVersion()
        body += packets.banchoPrivs(p)
        body += packets.userStats(p)
        body += packets.userPresence(p)
        body += packets.channelStart()
        
        for c in cache.channels:
            if not p.privileges & c[3]: 
                continue
            
            if c[0] == 'lobby':
                continue

            body += packets.channelJoin(c[0])
            body += packets.channelInfo(c[0], c[1], c[2])
        
        body += packets.userStats(p)
        for x in cache.online:
            x = cache.online[x]
            if x.userid != 3: # bot
                x.enqueue.append(packets.userStats(p))
            if x.userid != p.userid:
                body += packets.userPresence(x) + packets.userStats(x)
        cache.online[userid] = p
        printc(f'{p.username} has logged in!', Colors.Blue)

    
    conn.set_status(200)
    conn.add_header('cho-token', userid)
    conn.set_body(body)
    return conn.response

def run(socket_type: Union[str, tuple] = ("127.0.0.1", 5000)):
    # BEFORE we run the server we want to add our
    # bot object so we the user logins, they see the bot
    bot = Player(3, 20201229.2, ['bot'], time.time())
    bot.action = Action.Afk
    bot.username = 'Lamp'
    cache.online[3] = bot
    s.run(socket_type)