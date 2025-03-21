import asyncio
import websockets
import json

async def listen_messages(websocket):
    async for message in websocket:
        data = json.loads(message)
        if data["type"] == "system":
            print(f"[SYSTEM]: {data['message']}")
        elif data["type"] == "chat":
            print(f"[{data['client_id']}]: {data['message']}")

async def chat_client():
    uri = "ws://localhost:8765"
    
    async with websockets.connect(uri) as websocket:
        # Start listening for messages
        asyncio.create_task(listen_messages(websocket))
        
        print("Connected to the chat server. Type your message and press Enter.")
        
        while True:
            msg = input()
            if msg.lower() in ["exit", "quit"]:
                print("Disconnecting...")
                break
            
            await websocket.send(json.dumps({"message": msg}))

if __name__ == "__main__":
    asyncio.run(chat_client())
