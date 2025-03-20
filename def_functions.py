from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant
from langchain.schema import HumanMessage
from langchain.memory import ConversationSummaryMemory
from dotenv import load_dotenv
load_dotenv()
import os
import re
from prompts import SummaryPrompt



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



def conversation_memory():
    # Initialize ChatGroq LLM (Replace with your API key)
    llm = ChatGroq(groq_api_key="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", model_name="llama3-8b-8192")

    # Initialize memory to store conversation history
    return ConversationSummaryMemory(llm=llm, return_messages=True, summarypromt=SummaryPrompt)



def quit_conversation(user_input, memory):
    if user_input.lower() in ["quit", "bye"]:
        print("Good Bye")
        print("Chat Summary:")
        print(memory.load_memory_variables({})["history"])
        return False



def load_embedding():
    # LOCAL
    model_name = 'BAAI/bge-base-en'
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}

    embeddings= HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
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

    db = Qdrant(
        client = client,
        embeddings = embeddings,
        collection_name = collection_name
    )
    print("\n============================= Data Loaded =============================\n")
    return db



def make_retieval_chain(llm, prompt, vector_data):
    # Create document chain
    document_chain = create_stuff_documents_chain(llm, prompt)

    # Input--->Retriever--->vectorstoredb
    # Create Retrieve    
    # - (search_type="similarity_score_threshold", similarity_score_threshold=0.3)
    # - (search_type="mmr")
    # - (search_kwargs={"k": 1})
    retriever = vector_data.as_retriever(search_type="mmr", search_kwargs={"k": 5})
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    return retrieval_chain



def clean_retreived_response(response):
    # Extract text from the response dictionary
    raw_text = response['answer']
    # Remove Markdown-style formatting (e.g., '**' for bold)
    clean_text = re.sub(r'\*\*', '', raw_text)
    print(clean_text)
    print("\n============================= Response Loaded =============================\n")