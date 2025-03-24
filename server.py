# import asyncio
# import websockets
# import json
# import uuid
# from def_functions import *
# from prompts import *

# llm = ChatGroq(groq_api_key="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", 
#                model_name="qwen-2.5-32b")
# clients = {}   # Store connected clients
# client_sessions = {}  # Stores LLM instance and memory for each client

# async def handle_client(websocket):
#     client_id = str(uuid.uuid4())  # Generate unique Client ID
#     clients[client_id] = websocket
#     client_sessions[client_id] = {
#         "memory": conversation_memory(),  # Separate memory for each client
#         "llm": llm  # Separate LLM session
#     }

#     print(f"Client {client_id} connected!")


#     # response = chat_with_llm(llm, SystemPrompt, "Hii", memory)
#     # response_data = json.dumps({"client_id": client_id, "response": response})
#     # await websocket.send(response_data)  # Send response to client

#     try:
#         initial_ai_response = "Hii, How can I assist you?"
#         await websocket.send(json.dumps({"client_id": client_id, "response": initial_ai_response}))

#         while True:
#             try:
#                 user_input = await asyncio.wait_for(websocket.recv(), timeout=1000)  # Receive message from client
#                 print(f"Received from {client_id}: {user_input}")

#                 if not user_input:
#                     continue

#                 if user_input.lower() in ["quit", "exit"]:
#                     print("Goodbye!")
#                     print("Disconnected from AI Server.")
#                     final_response = "Goodbye! Your session has been closed."
#                     await websocket.send(json.dumps({"client_id": client_id, "response": final_response}))
#                     await websocket.close(reason="Session ended by client request.")  # Close connection
#                     break  # Stop loop
                
#                 # Retrieve client-specific LLM session and memory
#                 client_llm = client_sessions[client_id]["llm"]
#                 client_memory = client_sessions[client_id]["memory"]

#                 # AI Processing (Replace this with AI response logic)
#                 ai_response = chat_with_llm(client_llm, SystemPrompt, user_input, client_memory)

#                 if "MVA Sections = TRUE" in ai_response or user_input == '':
#                     embedding = load_embedding()
#                     load_vectorDB = load_data_from_VectorDB(embedding)
#                     retrieval_chain = make_retieval_chain(llm, RetrievalPrompt, load_vectorDB)

#                     chat_summary = client_memory.load_memory_variables({})["history"][0]        
#                     history = chat_summary.content
#                     response = retrieval_chain.invoke({"input":history})

#                     # # # Save conversation in memory
#                     # memory.save_context({"input": user_input}, {"output": response['answer']})

#                     response = clean_retreived_response(response)
#                     final_response = f"{str(response)}\n=============================================\n\nGoodbye!\n\nChat Summary:\n{str(history)}"
                    
#                     response_data = json.dumps({"client_id": client_id, "response": final_response})
#                     await websocket.send(response_data)  # Send response to client
#                     # print("\n=============================================\n")
#                     # print("Goodbye!")
#                     # print("Chat Summary:", memory.load_memory_variables({})["history"])
#                     print("Goodbye! Disconnecting from AI Server.")
#                     await websocket.send(response_data)  # Send final response
#                     await websocket.close(reason="MVA session completed.")  # Close connection
#                     break

#                 else:
#                     response_data = json.dumps({"client_id": client_id, "response": ai_response})
#                     await websocket.send(response_data)  # Send response to client
#                     print(f"Sent to {client_id}: {ai_response}")
            
#             except Exception as e:
#                 print(f"Error with client {client_id}: {e}")
#                 break
#             except websockets.exceptions.ConnectionClosed:
#                 print(f"Client {client_id} disconnected.")
#                 break
            
#     finally:
#         # Cleanup after client disconnects
#         clients.pop(client_id, None)
#         client_memory.pop(client_id, None)
#         print(f"Client {client_id} session ended.")

# async def main():
#     async with websockets.serve(
#         handle_client, "localhost", 8765, ping_interval=1000, ping_timeout=1500):  # Ping every 60s, timeout after 5min
#         print("AI Server running on ws://localhost:8765")
#         await asyncio.Future()  # Run forever

# if __name__ == "__main__":
#     asyncio.run(main())



# import asyncio
# import websockets
# import json
# import uuid
# from def_functions import *
# from prompts import *

# llm = ChatGroq(groq_api_key="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", 
#                model_name="qwen-2.5-32b")

# clients = {}   # Store connected clients
# client_sessions = {}  # Stores LLM instance and memory for each client

# async def handle_client(websocket):
#     client_id = str(uuid.uuid4())  # Generate unique Client ID
#     clients[client_id] = websocket
#     client_sessions[client_id] = {
#         "memory": conversation_memory(),  # Separate memory for each client
#         "llm": llm  # Separate LLM session
#     }

#     print(f"Client {client_id} connected!")

#     try:
#         initial_ai_response = "Hi, how can I assist you?"
#         await websocket.send(json.dumps({"client_id": client_id, "response": initial_ai_response}))

#         while True:
#             try:
#                 # Receive user input
#                 user_input = await asyncio.wait_for(websocket.recv(), timeout=3000)  # Receive message from client
#                 print(f"Received from {client_id}: {user_input}")

#                 if not user_input:
#                     continue

#                 # Handle client-initiated exit
#                 if user_input.lower() in ["quit", "exit"]:
#                     print(f"Client {client_id} requested disconnection.")
#                     final_response = "Goodbye! Your session has been closed."
#                     await websocket.send(json.dumps({"client_id": client_id, "response": final_response}))
#                     await websocket.close(reason="Session ended by client request.")
#                     break
                
#                 # Retrieve client-specific LLM session and memory
#                 client_llm = client_sessions[client_id]["llm"]
#                 client_memory = client_sessions[client_id]["memory"]

#                 # Generate AI response
#                 # ai_response = chat_with_llm(client_llm, SystemPrompt, user_input, client_memory)
#                 ai_response = await asyncio.to_thread(chat_with_llm, client_llm, SystemPrompt, user_input, client_memory)

#                 # If "MVA Sections = TRUE" is detected, fetch additional info & end session
#                 if "MVA Sections = TRUE" in ai_response:
#                     embedding = load_embedding()
#                     load_vectorDB = load_data_from_VectorDB(embedding)
#                     retrieval_chain = make_retieval_chain(llm, RetrievalPrompt, load_vectorDB)

#                     chat_summary = client_memory.load_memory_variables({})["history"][0]        
#                     history = chat_summary.content
#                     response = retrieval_chain.invoke({"input": history})

#                     response = clean_retreived_response(response)
#                     final_response = f"{response}\n=============================================\n\nGoodbye!\n\nChat Summary:\n{history}"
                    
#                     response_data = json.dumps({"client_id": client_id, "response": final_response})
#                     await websocket.send(response_data)
#                     print(f"Client {client_id} - MVA Sections detected. Closing session.")
#                     await websocket.close(reason="MVA session completed.")  
#                     break

#                 else:
#                     response_data = json.dumps({"client_id": client_id, "response": ai_response})
#                     await websocket.send(response_data)  
#                     print(f"Sent to {client_id}: {ai_response}")

#             except websockets.exceptions.ConnectionClosed:
#                 print(f"Client {client_id} disconnected.")
#                 break
#             except Exception as e:
#                 print(f"Error with client {client_id}: {e}")
#                 break

#     finally:
#         # Cleanup after client disconnects
#         clients.pop(client_id, None)
#         client_sessions.pop(client_id, None)
#         print(f"Client {client_id} session ended.")

# async def main():
#     async with websockets.serve(handle_client, "localhost", 8765, ping_interval=1000, ping_timeout=3000):
#         print("AI Server running on ws://localhost:8765")
#         await asyncio.Future()  # Keep server running

# if __name__ == "__main__":
#     asyncio.run(main())




import asyncio
import websockets
import json
import uuid
from def_functions import *
from prompts import *

llm = ChatGroq(groq_api_key="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", 
               model_name="qwen-2.5-32b")

clients = {}  # Stores connected clients
client_sessions = {}  # Stores LLM instance & memory per client

async def process_client_messages(client_id, websocket, message_queue):
    """ Processes messages for a specific client asynchronously """
    while True:
        user_input = await message_queue.get()  # Get message from queue
        if user_input is None:
            break  # Exit if None (Client disconnected)

        try:
            print(f"Received from {client_id}: {user_input}")

            # Handle client-initiated exit
            if user_input.lower() in ["quit", "exit"]:
                print(f"Client {client_id} requested disconnection.")
                final_response = "Goodbye! Your session has been closed."
                await websocket.send(json.dumps({"client_id": client_id, "response": final_response}))
                await websocket.close(reason="Session ended by client request.")
                break

            # Retrieve client-specific LLM session & memory
            client_llm = client_sessions[client_id]["llm"]
            client_memory = client_sessions[client_id]["memory"]

            # Generate AI response asynchronously
            ai_response = await asyncio.to_thread(chat_with_llm, client_llm, SystemPrompt, user_input, client_memory)

            # If "MVA Sections = TRUE" is detected, fetch additional info & end session
            if "MVA Sections = TRUE" in ai_response:
                final_response = await fetch_additional_info(client_id, client_memory, websocket)
                await websocket.send(json.dumps({"client_id": client_id, "response": final_response}))
                await websocket.close(reason="MVA session completed.")
                break

            # Send AI response
            response_data = json.dumps({"client_id": client_id, "response": ai_response})
            await websocket.send(response_data)
            print(f"Sent to {client_id}: {ai_response}")

        except websockets.exceptions.ConnectionClosed:
            print(f"Client {client_id} disconnected.")
            break
        except Exception as e:
            print(f"Error with client {client_id}: {e}")
            break


async def fetch_additional_info(client_id, client_memory, websocket):
    """ Fetches additional info when 'MVA Sections = TRUE' is detected """
    embedding = load_embedding()
    load_vectorDB = load_data_from_VectorDB(embedding)
    retrieval_chain = make_retieval_chain(llm, RetrievalPrompt, load_vectorDB)

    chat_summary = client_memory.load_memory_variables({})["history"][0]        
    history = chat_summary.content
    response = await asyncio.to_thread(retrieval_chain.invoke, {"input": history})

    response = clean_retreived_response(response)
    final_response = f"{response}\n=============================================\n\nGoodbye!\n\nChat Summary:\n{history}"

    print(f"Client {client_id} - MVA Sections detected. Closing session.")
    return final_response


async def handle_client(websocket):
    """ Manages individual client connections asynchronously """
    client_id = str(uuid.uuid4())  # Unique Client ID
    message_queue = asyncio.Queue()  # Queue for handling client messages

    clients[client_id] = websocket
    client_sessions[client_id] = {
        "memory": conversation_memory(),  # Separate memory per client
        "llm": llm
    }

    print(f"Client {client_id} connected!")

    try:
        # Send initial greeting
        initial_ai_response = "Hi, how can I assist you?"
        await websocket.send(json.dumps({"client_id": client_id, "response": initial_ai_response}))

        # Start message processing task
        message_processor_task = asyncio.create_task(process_client_messages(client_id, websocket, message_queue))

        # Continuously receive client messages and add them to the queue
        async for user_input in websocket:
            await message_queue.put(user_input)

    except websockets.exceptions.ConnectionClosed:
        print(f"Client {client_id} disconnected.")
    finally:
        # Cleanup resources when client disconnects
        clients.pop(client_id, None)
        client_sessions.pop(client_id, None)
        message_queue.put_nowait(None)  # Signal message processor to stop
        await message_processor_task  # Wait for cleanup
        print(f"Client {client_id} session ended.")


async def main():
    """ Starts WebSocket server to handle multiple clients concurrently """
    async with websockets.serve(handle_client, "localhost", 8765, ping_interval=30, ping_timeout=60):
        print("AI Server running on ws://localhost:8765")
        await asyncio.Future()  # Keep server running

if __name__ == "__main__":
    asyncio.run(main())
