from aiotinydb import AIOTinyDB
USERS = AIOTinyDB('./data/users.json')
SCORES = AIOTinyDB('./data/scores.json')
BEATMAPS = AIOTinyDB('./data/beatmaps.json')