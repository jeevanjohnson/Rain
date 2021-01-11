from helpers import BEATMAPS
from objects.const import ServerRankedStatus
from aiohttp import request
import config

class Beatmap:
    def __init__(self) -> None:
        self.setid: int = None
        self.mapid: int = None
        self.rankedstatus: ServerRankedStatus = None
        self.md5: str = None
        self.creator: str = None
        self.total_length: int = None
        self.hit_length: int = None
        self.title: str = None
        self.title_unicode: str = None
        self.artist: str = None
        self.artist_unicode: str = None
        self.diff_name: str = None
        self.max_combo: int = None
        self.cs: float = None
        self.od: float = None
        self.hp: float = None
        self.ar: float = None
    
    @staticmethod
    async def from_md5(md5: str): 
        b = Beatmap()
        params = {'k': config.api_keys['osu'], 'h': md5}
        url = 'https://old.ppy.sh/api/get_beatmaps'
        async with request('GET', url, params = params) as req:
            if not req or req.status != 200 or not (r := await req.json()):
                return None

            bmap = r[0]

        b.setid = int(bmap['beatmapset_id'])
        b.mapid = int(bmap['beatmap_id'])
        b.creator = bmap['creator']
        b.rankedstatus = ServerRankedStatus.from_api(int(bmap['approved']))
        b.md5 = md5
        b.total_length = int(bmap['total_length'])
        b.hit_length = int(bmap['hit_length'])
        b.title = bmap['title']
        b.title_unicode = bmap['title_unicode']
        b.artist = bmap['artist']
        b.artist_unicode = bmap['artist_unicode']
        b.diff_name = bmap['version']
        b.max_combo = int(bmap['max_combo'] or 0)
        b.cs = float(bmap['diff_size'])
        b.od = float(bmap['diff_overall'])
        b.hp = float(bmap['diff_drain'])
        b.ar = float(bmap['diff_approach'])

        url = f"https://old.ppy.sh/osu/{b.mapid}"
        async with request('GET', url) as req:
            if not req or req.status != 200 or not (r := await req.content.read()):
                return None

        filename = f'{b.artist} - {b.title} ({b.creator}) {b.diff_name}'
        with open(f'./data/beatmaps/{filename}.osu', 'wb') as f:
            f.write(r)

        return b
