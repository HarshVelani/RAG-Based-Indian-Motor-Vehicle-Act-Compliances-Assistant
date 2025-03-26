import streamlit as st
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
from langchain.prompts import ChatPromptTemplate

prompt="""
You are a traffic police inspector assisting the user about Motor Vehicle Act (MVA) Compliance.
Strictly follow the steps:
1. Ask a relevant question based on the history.
2. Wait for the user's response before proceeding.
3. Analyze the {question} and {history} to determine the next relevant question.
4. Repeat the above steps until satisfied.


Strictly follow these rules:
- Ask only one question at a time and wait for the user's response before proceeding to the next question.
- Strictly do not list multiple questions at once.
- Strictly if user's response is 'yes' or 'Yes' then accept it in Positive way and move forward.
- Strictly if user's response is 'no' or 'No' then accept it in Negative way and move forward.
- Strictly ignore and move forward if user's response is 'i dont know' or 'i dont know about that' or similar to this.
- Strictly Use history to ask related questions without repeating any previously asked questions.
- Strictly ask only the question without any introduction or repetition of greetings.
- do not ask this type of questions. example: "Was the vehicle involved in any kind of accident at the time of registration?"
- Strictly do not ask many questions.
- Greet the user only once.
- Never mention the name of the inspector.
- Strictly Never ask similar questions.
- Strictly Never stick to one question; ensure diversity in the questions asked.
- Strictly Never repeat any previously asked questions.
- Never ask for personal details.
- Strictly Never answer questions that fall outside the user's history or investigation.

history: {history}
incident:{question}

End the conversation strictly replying as **'MVA Sections = TRUE'**. example: "MVA Sections = TRUE".
- if you are satisfied with the interrogation with user regarding history or
- if user asks about MVA Sections.
- Do not ask for further assistance.
"""
SystemPrompt=ChatPromptTemplate.from_messages([
                ("system", prompt),
                ("human", "{question}")
            ])



RetrievalPrompt = ChatPromptTemplate.from_template("""
you are a traffic police inspector, advicing and explaining the MVA sections.
Based on the input, 
- if any section is ommited then mention and highlight that.
- Explain all the given context.
- provide punishment and fine only from "- Punishment and Fines" from context,
- specify and explain if there is any state amendment if provided for particular section, pecisely based only on the provided context.
- if you don't know then politely say 'I dont know'.
- Do not ask for further assistance.


Output should be:
===> Section number:
- Section Title:
- Definition:
- Detailed information: same as given in the context
- State Amendments: If provided
- Punishments and Fines: from "- Punishment and Fines:-" only if provided
then again start with the upper format for next section
                                                   
input: {input}
context: {context}""")

SummaryPrompt = """

Summarize the conversation by capturing key events, critical details, 
and relevant legal references discussed regarding a motor vehicle and 
traffic-related incident. Highlight the main concerns raised by the user, 
the assistant’s inquiries, and responses, ensuring clarity and coherence while 
avoiding redundancy. Focus on the accident details, including the date, time, 
location, parties involved, type of vehicle(s), nature of the collision, injuries, 
damages, weather, and road conditions. Cover legal implications such as applicable 
traffic laws, fault determination, insurance claims, liability, potential violations, 
penalties, and relevant legal precedents. Address investigative aspects, including 
police reports, witness statements, evidence collection 
(CCTV, dashcam footage, accident reconstruction), and procedural requirements. 
Capture the user’s concerns regarding legal rights, compensation, filing complaints, 
and interactions with law enforcement or insurance companies. Summarize the 
assistant’s responses, including clarifications on legal procedures, recommendations 
for documentation, guidance on next steps, and alternative resolutions. Finally, 
include actionable insights such as steps for legal recourse, safety measures, 
and best practices in handling post-accident legalities while ensuring all 
important words and phrases are retained and additional relevant 
terminology is incorporated where needed to enhance clarity and accuracy. 
Strictly do not miss the words related to **"Traffic signal violation, Excessive speed,
speed limit, traffic rules violation, traffic laws violation, traffic regulations, 
traffic signs violation, traffic signal violation, Overtaking, lane discipline,
overcrowded vehicle, overloading, driving under the influence of alcohol or drugs,
driving without a license, driving without insurance, driving without a helmet,
driving without a seatbelt, driving without a registration certificate,
driving without a pollution under control certificate, driving without a permit,
driving without a fitness certificate, driving without a valid permit, etc."**

"""

load_dotenv()

def chat_with_llm(llm, prompt_template, user_input, memory):
    history = memory.load_memory_variables({})["history"]
    prompt = prompt_template.format(history=history, question=user_input)
    response = llm.invoke([HumanMessage(content=prompt)])
    memory.save_context({"input": user_input}, {"output": response.content})
    return response.content

def conversation_memory():
    return ConversationSummaryMemory(
        llm=ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-70b-8192"),
        return_messages=True,
        summarypromt=SummaryPrompt
    )

def load_embedding():
    model_name = 'BAAI/bge-base-en'
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    return embeddings

def load_data_from_VectorDB(embeddings):
    url = os.getenv("QDRANT_VECTORDB_URL")
    collection_name = "MVA_db_bge_base_en"
    client = QdrantClient(url=url, prefer_grpc=False)
    db = QdrantVectorStore(client=client, embedding=embeddings, collection_name=collection_name)
    return db

def make_retieval_chain(llm, prompt, vector_data):
    '''
    - (search_type="similarity_score_threshold", similarity_score_threshold=0.3)
    - (search_type="mmr", search_kwargs={"k": 5})
    - (search_kwargs={"k": 1})'''
    
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vector_data.as_retriever(search_type="mmr", search_kwargs={"k": 5})
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    return retrieval_chain

def clean_retreived_response(response):
    raw_text = response['answer']
    clean_text = re.sub(r'\*\*', '', raw_text)
    return clean_text

# Initialize ChatGroq LLM (Replace with your API key)
'''
- llama3-8b-8192
- llama3-70b-8192
- deepseek-r1-distill-llama-70b
- qwen-2.5-32b
'''

llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="qwen-2.5-32b")
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

    if "MVA Sections = TRUE" in response or "mva section" in user_input.lower() or "mva sections" in user_input.lower() or user_input.lower() in ['quit', 'exit']:
        retrieval_chain = make_retieval_chain(llm, RetrievalPrompt, load_vectorDB)
        chat_summary = memory.load_memory_variables({})["history"][0]        
        history = chat_summary.content
        response = retrieval_chain.invoke({"input": history})
        clean_response = clean_retreived_response(response)
        
        print("=======CHAT MEMORY: ",history)
        # Clear chat memory
        memory.clear()
        if not memory:
            print("======================= EMPTY Memory  =======================")
        
        st.session_state.messages.append({"role": "assistant", "content": clean_response})
        with st.chat_message("assistant"):
            st.markdown(clean_response)

    elif "MVA Sections = TRUE" not in response or "mva section" not in user_input.lower() or "mva sections" not in user_input.lower():
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
    
            
    