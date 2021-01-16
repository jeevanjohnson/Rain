from typing import Union, Callable
from WebLamp import Lamp, Connection
from WebLamp.utlies import printc as log, Colors
from packets import PacketIDS
import packets
import re

class OsuServer:
    def __init__(self) -> None:
        self.server = Lamp()
        self.handlers = {}
    
    def handler(self, target: Union[str, PacketIDS, re.Pattern], 
                domain: Union[str, re.Pattern] = 'osu.ppy.sh'):
        def inner(func):
            self.handlers[target] = func

            if isinstance(target, PacketIDS):
                @self.server.route('/', re.compile(r'^c([4-6e])\.ppy\.sh$'))
                async def bancho(conn: Connection) -> bytes:
                    if 'osu-token' not in conn.request:
                        l = await self.handlers['login'](conn)
                        return l.response

                    from cache import online
                    if (userid := int(conn.request['osu-token'])) not in online:
                        conn.set_status(200)
                        body = b''
                        body += packets.systemRestart()
                        body += packets.notification('Server is restarting!')
                        conn.set_body(body)
                        return conn.response

                    p = online[userid]
                    body = b''
                    packetid = PacketIDS(conn.request['body'][0])
                    conn = await self.handlers[packetid](conn, p)
                    del conn._response[1]
                    conn._response.insert(1, '')
                    body += conn._response[3]
                    if p.enqueue:
                        for data in p.enqueue:
                            body += data
                    conn.set_body(body)
                    return conn.response
                    
            elif domain == 'a.ppy.sh':
                @self.server.route(target, domain)
                async def ava(conn: Connection) -> bytes:
                    a = await func(conn)
                    return a.response
            else:
                @self.server.route(target, domain)
                async def web(conn: Connection) -> bytes:
                    # TODO: extra checks if the user is online or server
                    # restarted
                    w = await func(conn)
                    return w.response

            return func
        return inner

    def run(self, socket_type: Union[str, tuple] = ("127.0.0.1", 5000), **kwargs) -> None:
        self.server.run(socket_type, **kwargs)