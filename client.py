# import asyncio
# import websockets
# import json
# from def_functions import *
# from prompts import *

# async def chat_with_ai():
#     uri = "ws://localhost:8765"

#     try:
#         async with websockets.connect(uri) as websocket:
#             print("Connected to AI Server!")
#             response = await websocket.recv()  # Receive initial AI greeting
#             response_data = json.loads(response)
#             print(f"AI: {response_data['response']}")
#             # response = await websocket.recv()  # Receive AI response
#             while True:
#                 # response = await websocket.recv()  # Receive AI response

#                 if "MVA Sections = TRUE" not in response or response == False:
#                     user_input = input("You: ")  # Get user input
#                     if user_input.lower() in ["quit", "exit"]:                    
#                         print("Goodbye! Disconnecting from AI Server.")
#                         await websocket.close(reason="Client requested disconnection.")  # Close connection
#                         break

#                     await websocket.send(user_input)  # Send message to server

#                     response = await websocket.recv()  
#                     response_data = json.loads(response)
#                     print(f"AI: {response_data['response']}")

#                 elif "MVA SECTION" in response_data['response']:
#                     # try:
#                     # response = await websocket.recv()  # Receive AI response
#                     data = json.loads(response)
#                     print(f"AI ({data['client_id']}): {data['response']}")
#                     print("Goodbye! Disconnecting from AI Server.")
#                     await websocket.close(reason="Client requested disconnection.")  # Close connection
#                     break  # End chat session for this case

#                         # else:
#                         #     print(f"AI ({data['client_id']}): {data['response']}")
#     except Exception as e:
#         print(f"Unexpected Error: {e}")                 
#     except json.JSONDecodeError:
#         print("Error: Invalid JSON received from server.")
#     except websockets.exceptions.ConnectionClosed:
#         print("Server disconnected unexpectedly.")

#     except websockets.exceptions.ConnectionClosedError as e:
#         print(f"WebSocket Error: {e}")



# asyncio.run(chat_with_ai())




import asyncio
import websockets
import json

async def chat_with_ai():
    uri = "ws://localhost:8765"

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to AI Server!")

            # Receive initial AI greeting
            response = await asyncio.wait_for(websocket.recv(), timeout=3000)  # Receive message from client
            response_data = json.loads(response)
            print(f"AI: {response_data['response']}")

            while True:
                user_input = input("You: ").strip()

                # Handle client-initiated exit
                if user_input.lower() in ["quit", "exit"]:
                    print("Goodbye! Disconnecting from AI Server.")
                    await websocket.close(reason="Client requested disconnection.")  
                    break

                await websocket.send(user_input)  # Send message to server

                # Receive AI response
                response = await websocket.recv()
                response_data = json.loads(response)

                print(f"AI: {response_data['response']}")

                # If AI response contains "MVA Sections = TRUE", disconnect the client
                if "MVA Sections = TRUE" in response_data['response']:
                    print("MVA Sections detected. Conversation ending...")
                    await websocket.close(reason="MVA session completed.")
                    break  

    except websockets.exceptions.ConnectionClosed:
        print("Server disconnected unexpectedly.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON received from server.")
    except Exception as e:
        print(f"Unexpected Error: {e}")

# Run client
asyncio.run(chat_with_ai())
