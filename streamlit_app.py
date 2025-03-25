import streamlit as st
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
import os
import re
from prompts import SummaryPrompt

load_dotenv()

def chat_with_llm(llm, prompt_template, user_input, memory):
    history = memory.load_memory_variables({})["history"]
    prompt = prompt_template.format(history=history, question=user_input)
    response = llm.invoke([HumanMessage(content=prompt)])
    memory.save_context({"input": user_input}, {"output": response.content})
    return response.content

def conversation_memory():
    return ConversationSummaryMemory(
        llm=ChatGroq(groq_api_key='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', model_name="llama3-70b-8192"),
        return_messages=True,
        summarypromt=SummaryPrompt
    )

def load_embedding():
    model_name = 'BAAI/bge-base-en'
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    return embeddings

def load_data_from_VectorDB(embeddings):
    url = "http://localhost:6333"
    collection_name = "MVA_db_bge_base_en"
    client = QdrantClient(url=url, prefer_grpc=False)
    db = QdrantVectorStore(client=client, embedding=embeddings, collection_name=collection_name)
    return db

def make_retieval_chain(llm, prompt, vector_data):
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vector_data.as_retriever(search_type="mmr", search_kwargs={"k": 5})
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    return retrieval_chain

def clean_retreived_response(response):
    raw_text = response['answer']
    clean_text = re.sub(r'\*\*', '', raw_text)
    return clean_text

llm = ChatGroq(groq_api_key='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', model_name="qwen-2.5-32b")
embedding = load_embedding()
load_vectorDB = load_data_from_VectorDB(embedding)
memory = conversation_memory()

st.title("Motor Vehicle Act Compliance LLM Chatbot")
st.subheader("A conversational AI chatbot powered by LLMs")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask me anything...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    response = chat_with_llm(llm, SystemPrompt, user_input, memory)

    if "MVA Sections = TRUE" in response or "mva section" in user_input.lower() or "mva sections" in user_input.lower() or user_input.lower() in ['quit','exit']:
        retrieval_chain = make_retieval_chain(llm, RetrievalPrompt, load_vectorDB)
        chat_summary = memory.load_memory_variables({})["history"][0]        
        history = chat_summary.content
        response = retrieval_chain.invoke({"input": history})
        clean_response = clean_retreived_response(response)
        st.session_state.messages.append({"role": "assistant", "content": clean_response})
        with st.chat_message("assistant"):
            st.markdown(clean_response)
    
    elif "MVA Sections = TRUE" not in response or "mva section" not in user_input.lower() or "mva sections" not in user_input.lower():
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
    
            
    