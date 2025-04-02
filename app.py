from prompts import *
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain.schema import HumanMessage
from langchain.memory import ConversationSummaryMemory
from dotenv import load_dotenv
load_dotenv()
import os
import re



# Define a function to chat with the LLM
def chat_with_llm(llm, prompt_template, user_input, memory):
    # Retrieve past conversation history
    history = memory.load_memory_variables({})["history"]
    # Format the prompt with history and current question
    prompt = prompt_template.format(history=history, question=user_input)
    # Get response from LLM
    response = llm.invoke([HumanMessage(content=prompt)])
    # Save conversation in memory
    memory.save_context({"input": user_input}, {"output": response.content})
    return response.content

def conversation_memory(llm):
    # Initialize memory to store conversation history
    return ConversationSummaryMemory(llm=llm, return_messages=True, summarypromt=SummaryPrompt)

def load_embedding():
    # LOCAL
    model_name = 'BAAI/bge-base-en'
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    # embedding = HuggingFaceEmbeddings()  # Initialize correctly
    # embedded_data = embedding.embed_documents(your_data)  # Use method to embed
    # load_vectorDB = load_data_from_VectorDB(embedded_data)  # Pass result correctly

    embeddings= HuggingFaceEmbeddings(
        model_name=model_name
        # model_kwargs=model_kwargs,
        # encode_kwargs=encode_kwargs
    )
    print("\n============================= Embedding Model Loaded...=============================\n")
    return embeddings

def load_data_from_VectorDB(embeddings):
    # Load Data from Vector-DB
    url = "http://localhost:6333"
    collection_name = "MVA_db_bge_base_en"

    client = QdrantClient(
        url = url,
        prefer_grpc = False
    )
    # print(client)
    print("\n============================= Client Loaded...=============================\n")

    db = QdrantVectorStore(
        client = client,
        embedding = embeddings,
        collection_name = collection_name
    )
    print("\n============================= Data Loaded =============================\n")
    return db

def make_retrieval_chain(llm, prompt, vector_data):
    # Create document chain
    document_chain = create_stuff_documents_chain(llm, prompt)

    # Input--->Retriever--->vectorstoredb
    # Create Retrieve    
    # - (similarity_score_threshold=0.3)
    # - (search_type="mmr", search_kwargs={"k": 5})
    # - (search_kwargs={"k": 1})
    retriever = vector_data.as_retriever(search_type="mmr", search_kwargs={"k": 5})
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    return retrieval_chain

def clean_retrieved_response(response):
    # Extract text from the response dictionary
    raw_text = response['answer']
    # Remove Markdown-style formatting (e.g., '**' for bold)
    clean_text = re.sub(r'\*\*', '', raw_text)
    return clean_text

def clean_deepseek_output(response: str) -> str:
    # Remove <think> tags and their content
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    
    # Extract only the output (assuming it follows the last </think> tag or is standalone)
    return response.strip()



# Initialize ChatGroq LLM (Replace with your API key)
# llama3-8b-8192
# llama3-70b-8192
# deepseek-r1-distill-llama-70b
# qwen-2.5-32b
# qwen-qwq-32b
# gemma2-9b-it

chat_llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="qwen-2.5-32b")
summary_llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-70b-8192")
retrieval_llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY2"), model_name="qwen-2.5-32b")

embedding = load_embedding()
load_vectorDB = load_data_from_VectorDB(embedding)
memory = conversation_memory(summary_llm)

while True:

    user_input = input("Enter: ")

    response = chat_with_llm(chat_llm, SystemPrompt, user_input, memory)
    print("\n=============================================\n")
    print(">>>>> " + clean_deepseek_output(response))

    chat_summary = memory.load_memory_variables({})["history"][0]        
    history = chat_summary.content
    print("\n===Chat Summary===\n", history)


    # Check if retrieval is needed
    if any(keyword in user_input.lower() for keyword in ["mva section", "mva sections", "quit", "exit"]) or "MVA Sections = TRUE" in response:
        retrieval_chain = make_retrieval_chain(chat_llm, RetrievalPrompt, load_vectorDB)

        # Generate LLM response for keywords extraction
        prompt = KeywordPrompt.format(history=history, question=user_input)
        response = chat_llm.invoke([HumanMessage(content=prompt)])
        keywords = response.content

        print("\n\nKeywords extracted:", keywords) # Debugging

        # Retrieve relevant information
        retrieval_response = retrieval_chain.invoke({"input": keywords})

        memory.clear()

        # Check if memory is empty
        if memory.load_memory_variables({})["history"][0].content == "":  # Works for lists, dicts, and other empty collections
            print("\n\n======================== Memory cleared! ========================\n\n")

        print("\n\nRetrieval Response:\n", retrieval_response["answer"]) # Debugging
        print("\n=============================================\n")
        # print(clean_retrieved_response(retrieval_response))
        # print(clean_deepseek_output(retrieval_response["answer"]))
        # print("\n=============================================\n")
        print("Goodbye!")
        break

# challan was issued by traffic police even after i followed the traffic rules
# please provide details about MVA Sections