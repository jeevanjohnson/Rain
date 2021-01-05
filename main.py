from WebLamp import Connection
from server import OsuServer
import packets
from packets import PacketIDS

s = OsuServer()
bancho = ("c.ppy.sh", "c4.ppy.sh", "c5.ppy.sh", "c6.ppy.sh")
web = ("osu.ppy.sh")
avatar = ("a.ppy.sh")

@s.handler(target = 'banchologin', domains = bancho, method = ['GET', 'POST'])
async def login(conn: Connection):
    body = b''
    # Getting all password details
    credentials = conn.request['body'].decode().replace('\n', '|').split('|', 5)
    credentials[2] = float(credentials[2][1:])
    credentials[5] = credentials[5].replace('|', ':').split(':')

    # 0 username
    # 1 password (hashed in md5)
    # 2 game version
    # 3 ?
    # 4 ?
    # 5 hardware data

    # Check credentials to see if anything is wrong
    if not username: # this would check db but we are not at this part yet
        ... # will do eventually
    else:
        body += packets.userID(3)
    
    conn.set_status(200)
    conn.add_header('Content-Length', len(body))
    conn.set_body(body)
    conn.add_header('cho-token', 'abc')
    return conn.response

s.run()