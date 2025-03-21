import asyncio
import websockets
import json
from def_functions import *
from initialize_variables import *
from prompts import *

async def chat_with_ai():
    uri = "ws://localhost:8765"

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to AI Server!")

            while True:
                try:
                    response = await websocket.recv()  # Receive AI response
                    data = json.loads(response)
                    

                    if "MVA SECTION" in data['response']:
                        print(f"AI ({data['client_id']}): {data['response']}")
                        break
                    
                    user_input = input("You: ")  # Get user input
                    print(f"AI ({data['client_id']}): {data['response']}")
                    
                    # if "MVA Sections = TRUE" in response:
                    #     embedding = load_embedding()
                    #     load_vectorDB = load_data_from_VectorDB(embedding)
                    #     retrieval_chain = make_retieval_chain(llm, RetrievalPrompt, load_vectorDB)

                    #     chat_summary = memory.load_memory_variables({})["history"][0]        
                    #     history = chat_summary.content
                    #     response = retrieval_chain.invoke({"input":history})

                    #     # # # Save conversation in memory
                    #     # memory.save_context({"input": user_input}, {"output": response['answer']})

                    #     clean_retreived_response(response)
                    #     print("\n=============================================\n")
                    #     print("Goodbye!")
                    #     print("Chat Summary:", memory.load_memory_variables({})["history"])
                
                except json.JSONDecodeError:
                    print("Error: Invalid JSON received from server.")
                except websockets.exceptions.ConnectionClosed:
                    print("Server disconnected unexpectedly.")
                    break

                

                if user_input.lower() in ["quit", "exit"]:
                    print("Goodbye!")
                    print("Disconnected from AI Server.")
                    break

                await websocket.send(user_input)  # Send message to server


    except websockets.exceptions.ConnectionClosedError as e:
        print(f"WebSocket Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")


asyncio.run(chat_with_ai())
