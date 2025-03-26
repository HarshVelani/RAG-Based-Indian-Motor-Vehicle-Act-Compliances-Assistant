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




# initialize from client side
import asyncio
import websockets
import json
import uuid
import re
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain.schema import HumanMessage
from langchain.memory import ConversationSummaryMemory
from def_functions import *
from prompts import *

def chat_with_llm(llm, prompt_template, user_input, memory):
    history = memory.load_memory_variables({})["history"]
    prompt = prompt_template.format(history=history, question=user_input)
    response = llm.invoke([HumanMessage(content=prompt)])
    memory.save_context({"input": user_input}, {"output": response.content})
    return response.content

def conversation_memory():
    return ConversationSummaryMemory(llm=ChatGroq(groq_api_key="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", model_name="llama3-70b-8192"), return_messages=True, summary_prompt=SummaryPrompt)

def load_embedding():
    model_name = 'BAAI/bge-base-en'
    return HuggingFaceEmbeddings(model_name=model_name)

def load_data_from_VectorDB(embeddings):
    client = QdrantClient(url="http://localhost:6333", prefer_grpc=False)
    return QdrantVectorStore(client=client, embedding=embeddings, collection_name="MVA_db_bge_base_en")

def make_retrieval_chain(llm, prompt, vector_data):
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vector_data.as_retriever(search_type="mmr", search_kwargs={"k": 5})
    return create_retrieval_chain(retriever, document_chain)

def clean_retrieved_response(response):
    raw_text = response['answer']
    return re.sub(r'\*\*', '', raw_text)


llm = ChatGroq(groq_api_key="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", model_name="qwen-2.5-32b")

clients = {}  # Stores connected clients
client_sessions = {}  # Stores LLM instance & memory per client

async def process_client_messages(client_id, websocket, message_queue):
    while True:
        user_input = await message_queue.get()
        if user_input is None:
            break

        try:
            import pdb;pdb 
            if user_input.lower() in ["quit", "exit"]:
                final_response = "Goodbye! Your session has been closed."
                await websocket.send(json.dumps({"client_id": client_id, "response": final_response}))
                await websocket.close()
                break

            client_llm = client_sessions[client_id]["llm"]
            client_memory = client_sessions[client_id]["memory"]
            ai_response = await asyncio.to_thread(chat_with_llm, client_llm, SystemPrompt, user_input, client_memory)

            if "MVA Sections = TRUE" in ai_response or "mva section" in user_input.lower():
                final_response = await fetch_additional_info(client_id, client_memory, websocket)
                await websocket.send(json.dumps({"client_id": client_id, "response": final_response}))
                await websocket.close()
                break

            await websocket.send(json.dumps({"client_id": client_id, "response": ai_response}))
        except websockets.exceptions.ConnectionClosed:
            break
        except Exception as e:
            print(f"Error with client {client_id}: {e}")
            break

async def fetch_additional_info(client_id, client_memory, websocket):
    embedding = load_embedding()
    vector_db = load_data_from_VectorDB(embedding)
    retrieval_chain = make_retrieval_chain(llm, RetrievalPrompt, vector_db)
    history = client_memory.load_memory_variables({})["history"][0].content
    response = await asyncio.to_thread(retrieval_chain.invoke, {"input": history})
    response = clean_retrieved_response(response)
    return f"{response}\n====================\nGoodbye!\nChat Summary:\n{history}"

async def handle_client(websocket):
    client_id = str(uuid.uuid4())
    message_queue = asyncio.Queue()

    clients[client_id] = websocket
    client_sessions[client_id] = {"memory": conversation_memory(), "llm": llm}

    try:
        message_processor_task = asyncio.create_task(process_client_messages(client_id, websocket, message_queue))
        async for user_input in websocket:
            await message_queue.put(user_input)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.pop(client_id, None)
        client_sessions.pop(client_id, None)
        message_queue.put_nowait(None)
        await message_processor_task

async def main():
    async with websockets.serve(handle_client, "localhost", 8765):
        print("AI Server running on ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())