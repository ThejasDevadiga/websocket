
import websockets,asyncio,queue
class MyQueue(queue.Queue):
    def clear(self):
        with self.mutex:
            self.queue.clear()
            self.not_full.notify()

class WebSocket:
    def __init__(self, mainApp):
        self.uri = "ws://192.168.37.228:3000/"  
        # self.uri = "ws://localhost:8765/"  
        self.websocket = None
        self.sending_messages = MyQueue()
        self.received_message = MyQueue()
        self.RECONNECT = "WebSocket connection closed. Reconnecting..."

    async def connect(self):
        try:
            print("WebSocket connecting.....")
            self.websocket = await websockets.connect(self.uri)
            self.sending_messages.put("Client-1") 
            print("WebSocket connected.")
        except Exception as e:
            print("WebSocket connection failed:", e)

    async def handle_sending(self):
        while True:
            await self.send_message()
            await asyncio.sleep(0.1)

    async def handle_reconnecting(self):
        while True:
            if self.websocket:
                try:
                    pong_waiter = await self.websocket.ping()
                    await asyncio.wait_for(pong_waiter, timeout=5)
                   
                    break
                except Exception as e:
                    print("WebSocket connection lost:", e)
                    self.websocket = None
                    await self.connect()
            else:
                await self.connect()
            await asyncio.sleep(1)

    async def handle_receiving(self):
        while True:
            await self.receive_message()
            await asyncio.sleep(0.1)

    async def send_message(self):
        try:
            sending_message = self.sending_messages.get(timeout=1)
            if sending_message is None:
                return
            if self.websocket:
                    await self.websocket.send(sending_message)
            else:
                print(self.RECONNECT)
                await self.handle_reconnecting()
        except queue.Empty:
            pass
        except websockets.exceptions.ConnectionClosed:
            print(self.RECONNECT)
            await self.handle_reconnecting()
        except Exception as e:
            print("Failed to send message:", e)

    async def receive_message(self):
        try:
            if self.websocket:
                while True:
                    message = await self.websocket.recv()
                    self.received_message.put(message)
                    self.handle_received_msg(message)
        except websockets.exceptions.ConnectionClosed:
            self.main_app.update_connection_status(
                self, "Not connected", "-----")
            print(self.RECONNECT)
            await self.handle_reconnecting()
        except Exception as e:
            print("Failed to receive message:", e)
            return None

    def handle_received_msg(self, msg):
        print("Recieved message :",msg)

            
    async def disconnect(self):
        try:
            if self.websocket:
                await self.websocket.close()
                print("WebSocket disconnected.")
        except Exception as e:
            print("Failed to disconnect WebSocket:", e)