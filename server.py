import asyncio
import websockets
import json

# Dictionary to store connected clients
clients = {}

async def handler(websocket, path):
    client_id = f"Client-{len(clients) + 1}"  # Assign unique ID
    clients[websocket] = client_id
    
    try:
        print(f"{client_id} connected.")
        await websocket.send(json.dumps({"type": "system", "message": f"Welcome {client_id}!"}))
        
        async for message in websocket:
            data = json.loads(message)
            broadcast_message = json.dumps({"type": "chat", "client_id": client_id, "message": data["message"]})
            
            # Broadcast message to all clients
            await asyncio.gather(*[client.send(broadcast_message) for client in clients if client != websocket])
    
    except websockets.exceptions.ConnectionClosed:
        pass  # Handle disconnect
    
    finally:
        print(f"{client_id} disconnected.")
        del clients[websocket]

async def main():
    server = await websockets.serve(handler, "localhost", 8765)
    print("WebSocket Server Started on ws://localhost:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
