import websockets,asyncio,logging
class Websocket():
    """This class handles the websocket session 
    """
    def __init__(self,url,port):
        self.url = url
        self.port = port
        self.connected = set()
        logging.basicConfig(filename="server_log.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        
    async def register(self,websocket):
        """This method register the new client to socket

        Args:
            websocket (client): Websocket client address and port
        """
        try:
            self.connected.add(websocket)
            self.logger.warning(f"Client {websocket.remote_address} connected")
            print(f"Client {websocket.remote_address} connected")
        except Exception as e:
            self.logger.error(f"Error in registering client {websocket.remote_address}: {e}")

    async def unregister(self,websocket):
        """This method unregister the new client to socket

        Args:
            websocket (client): Websocket client address and port
        """
        try:
            self.connected.remove(websocket)
            self.logger.warning(f"Client {websocket.remote_address} disconnected")
            print(f"Client {websocket.remote_address} disconnected")

        except Exception as e:
            self.logger.critical(f"Error in unregistering client {websocket.remote_address}: {e}")
    
    async def broadcast(self,message):
        """This method is used to 
        Args:
            message (_type_): _description_
        """
        for websocket in self.connected.copy():
            try:
                await websocket.send(f"{message}") 
                self.logger.info(message)
            except websockets.ConnectionClosed:
                self.logger.info(f"Client {websocket.remote_address} disconnected unexpectedly")
                await self.unregister(websocket)
            except Exception as e:
                self.logger.info(e)
    
    async def my_handler(self,websocket, path):
        """_summary_

        Args:
            websocket (_type_): _description_
            path (_type_): _description_
        """
        try:
            await self.register(websocket)
            try:
                async for message in websocket:
                    self.logger.info(f"Received message from client: {message}")    
                    await self.broadcast(message)
            except websockets.ConnectionClosed:
                self.logger.critical(f"Client {websocket.remote_address} disconnected unexpectedly")
                await self.unregister(websocket)
            except Exception as e:
                self.logger.critical(f"Error in handling message from client {websocket.   remote_address}: {e}")
                await self.unregister(websocket)
        except Exception as e:
            self.logger.error(f"Error in connection with client {websocket.remote_address}: {e}")
            await self.unregister(websocket)
    async def main(self):
        try:
            print(self.url)
            async with websockets.serve(self.my_handler, self.url, self.port):
                await asyncio.Future()
        except Exception as e:
            self.logger.error(f"Error in WebSocket server: {e}")
    