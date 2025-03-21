import asyncio
import websockets
import json
import uuid
from def_functions import *
from prompts import *
from initialize_variables import *


# Store connected clients
clients = {}

async def handle_client(websocket):
    client_id = str(uuid.uuid4())  # Generate unique Client ID
    clients[client_id] = websocket
    print(f"Client {client_id} connected!")

    # response = chat_with_llm(llm, SystemPrompt, "Hii", memory)
    # response_data = json.dumps({"client_id": client_id, "response": response})
    # await websocket.send(response_data)  # Send response to client

    try:
        initial_ai_response = "Hii, How can I assist you?"
        await websocket.send(json.dumps({"client_id": client_id, "response": initial_ai_response}))

        while True:

            user_input = await asyncio.wait_for(websocket.recv(), timeout=1000)  # Receive message from client
            
            if user_input.lower() in ["quit", "exit"]:
                    print("Goodbye!")
                    print("Disconnected from AI Server.")
                    break
            print(f"Received from {client_id}: {user_input}")

            # AI Processing (Replace this with AI response logic)
            ai_response = chat_with_llm(llm, SystemPrompt, user_input, memory)
 
            if "MVA Sections = TRUE" in ai_response:
                embedding = load_embedding()
                load_vectorDB = load_data_from_VectorDB(embedding)
                retrieval_chain = make_retieval_chain(llm, RetrievalPrompt, load_vectorDB)

                chat_summary = memory.load_memory_variables({})["history"][0]        
                history = chat_summary.content
                response = retrieval_chain.invoke({"input":history})

                # # # Save conversation in memory
                # memory.save_context({"input": user_input}, {"output": response['answer']})

                response = clean_retreived_response(response)
                
                final_response = str(response) + "\n=============================================\n" + "\nGoodbye!\n" + "\nChat Summary:\n" + str(history)
                response_data = json.dumps({"client_id": client_id, "response": final_response})
                await websocket.send(response_data)  # Send response to client
                # print("\n=============================================\n")
                # print("Goodbye!")
                # print("Chat Summary:", memory.load_memory_variables({})["history"])
                break
            else:
                response_data = json.dumps({"client_id": client_id, "response": ai_response})
                await websocket.send(response_data)  # Send response to client
            
    except websockets.exceptions.ConnectionClosed:
        print(f"Client {client_id} disconnected.")
    except Exception as e:
        print(f"Error with client {client_id}: {e}")
    finally:
        clients.pop(client_id, None)  # Remove client from list

async def main():
    async with websockets.serve(
        handle_client, "localhost", 8765, ping_interval=500, ping_timeout=1000):  # Ping every 60s, timeout after 5min
        print("AI Server running on ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
