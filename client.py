import asyncio
import websockets
import json
from def_functions import *
from prompts import *

async def chat_with_ai():
    uri = "ws://localhost:8765"

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to AI Server!")
            response = await websocket.recv()  # Receive initial AI greeting
            response_data = json.loads(response)
            print(f"AI: {response_data['response']}")
            # response = await websocket.recv()  # Receive AI response
            while True:
                # response = await websocket.recv()  # Receive AI response

                if response == False or "MVA Sections = TRUE" not in response:
                    user_input = input("You: ")  # Get user input
                    if user_input.lower() in ["quit", "exit"]:
                        print("Goodbye!")
                        print("Disconnected from AI Server.")
                        break
                    await websocket.send(user_input)  # Send message to server

                    response = await websocket.recv()  # Receive initial AI greeting
                    response_data = json.loads(response)
                    print(f"AI: {response_data['response']}")

                else:
                    try:
                        response = await websocket.recv()  # Receive AI response
                        data = json.loads(response)
                        if "MVA Sections = TRUE" in response:
                            data = json.loads(response)
                            print(f"AI ({data['client_id']}): {data['response']}")
                            break  # End chat session for this case

                        else:
                            print(f"AI ({data['client_id']}): {data['response']}")
                    
                    except json.JSONDecodeError:
                        print("Error: Invalid JSON received from server.")
                    except websockets.exceptions.ConnectionClosed:
                        print("Server disconnected unexpectedly.")
                        break
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"WebSocket Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")


asyncio.run(chat_with_ai())
