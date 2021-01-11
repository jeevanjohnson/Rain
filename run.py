from server import run
import config
import os
import shutil

os.chdir(os.path.dirname(os.path.realpath(__file__))) # sets our director in the console to /rain
p = './data' 

if not os.path.exists(p):
    os.mkdir(p)
p += '/'
for x in (f'{p}replays', f'{p}beatmaps', f'{p}screenshots', f'{p}avatars'):
    if x == f'{p}beatmaps':
        shutil.rmtree(x)
    if not os.path.exists(x):
        os.mkdir(x)
        if x == f'{p}avatars': print('Get a default profile picture and save it as "-1.png"')
run(config.socket_type)