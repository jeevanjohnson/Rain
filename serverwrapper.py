from typing import Union, Callable
from WebLamp import Lamp, Connection
from WebLamp.utlies import printc, Colors
from packets import PacketIDS

class OsuServer:
    def __init__(self) -> None:
        self.server = Lamp()
        self.handlers = {}
    
    def handler(self, target: Union[str, PacketIDS], 
                domains: Union[tuple, list], 
                method: list = []) -> Callable:
        def inner(func):
            
            if not isinstance(target, str) or target == 'banchologin':
                self.handlers[target] = func

            p = target if isinstance(target, str) else '/'
            if isinstance(target, str) and target != 'banchologin':
                for domain in domains:
                    @self.server.route(route = p, domain = domain, method = method)
                    async def ff(conn: Connection) -> bytes:
                        return await func(conn)
            else:
                for domain in domains:
                    @self.server.route(route = '/', domain = domain, method = method)
                    async def ff(conn: Connection) -> bytes:
                        if 'osu-token' not in conn.request:
                            f = self.handlers['banchologin']
                            return await f(conn)
                        else:
                            t = PacketIDS(conn.request['body'][0]) # read first byte in body
                            if t not in self.handlers:
                                printc(f'Unhandled Request: {t.name}', Colors.Red)
                                return b'error: :c'
                            else:
                                f = self.handlers[t] # get handler for packet

                            from cache import online
                            userid = int(conn.request['osu-token'])
                            if userid not in online:
                                player = None
                            else:
                                player = online[userid]
                            return await f(conn, player)

            return func
        return inner

    def run(self, socket_type: Union[str, tuple] = ("127.0.0.1", 5000)) -> None:
        self.server.run(socket_type)