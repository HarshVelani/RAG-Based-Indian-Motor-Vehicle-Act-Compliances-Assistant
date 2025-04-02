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
load_dotenv()
import os
import re
from langchain.prompts import ChatPromptTemplate

prompt="""
You are a traffic police inspector helping user for incident faced related to Motor Vehicle Act (MVA) Compliance by gathering the details.

Strictly follow rules below:
- Greet the user only once.
- if user greets then greet them in return and ask them sto expalin brief about incident,
- Strictly ask only wh-questions starting with "what, where, when, why, how, etc" wherever required.
- Strictly ask only the question without any introduction or repetition of greetings.
- Ask the user the following questions one by one, in the order provided.
- do not repeat a question if it has already been asked or answered earlier in the history.
- Ask only one question at a time and wait for the user's response before proceeding to the next question.
- Strictly do not list multiple questions at once.
- Once all questions are answered or the user indicates they are done, end the conversation by replying 'MVA Sections = TRUE'.
- mention the options in the question. Example: "Which type of vehicle(s) was involved in the incident? (two-wheeler, three-wheeler, four-wheeler, heavy vehicle, etc.)"
- Strictly ignore and move forward if user's response is 'i dont know' or 'i dont know about that' or similar to this.
- Never mention the name of the inspector.
- Strictly use histroy to not repeat the questions.
- Strictly Never ask similar questions.
- Strictly Never stick to one question.
- Strictly Never repeat any previously asked questions.
- Do not ask for exact location.
- Never ask for personal details.
- Strictly Never answer questions that fall outside the user's history or investigation.
- never ask similar or repeated questions. go through history and analyse the questions asked and then ask the next question.



Questions to ask in this sequence:
- location, 
- date of the incident. Format: DD/MM/YYYY, 
- time of the incident. Format: HH:MM AM/PM (12-hour clock), 
- nature of the accident (Collision, hit-and-run, head-on collision, rear-end collision, overturn, Pedestrian Hit, Vehice Falls Into Gorge, caught fire, side-impact collision, etc.),  
- injuries or deaths, 
- damages (vehicle, property, etc.), 
- human condition (mentally or physically unfit to drive, drunken, influenced by drugs or alcohol,), 
- safety equipments (Safety belt, helmet, seatbelts, headgear, etc.), 
- Traffic rules violation (excessive speed, speed limit, traffic signal violation, overtaking, lane discipline, etc.),
- road conditions (normal conditioned, good conditioned, potholes, obstacles, Debris, etc.), 
- type of vehicle(s) (two wheeler, three wheeler, four wheeler, heavy vehicle, etc.), 
- Vehicle's make, model and color, 
- vehicle registration (license plate number, registration certificate, pollution under control certificate, permit, fitness certificate, etc.), 
- insurance,
- weather (clear, rainy, foggy, poor visibility, etc.), 
- Strictly end the conversation strictly replying as **'MVA Sections = TRUE'**. example: "MVA Sections = TRUE".
    - if user asks about MVA Sections.
    - Do not ask for further assistance.

user input: {question}
history: {history}
"""

SystemPrompt=ChatPromptTemplate.from_messages([
                ("system", prompt),
                ("human", "{question}")
            ])


RetrievalPrompt = ChatPromptTemplate.from_template("""
you are a traffic police inspector, advicing and explaining the MVA sections.
Based on the input, 

- Explain all the given context.
- provide punishment and fine only from "- Punishment and Fines" from context,
- specify and explain if there is any state amendment if provided for particular section, pecisely based only on the provided context.
- if you don't know then politely say 'I dont know'.
- Do not ask for further assistance.


Output should be:
>> **Section number**
- **Section Title:** same as given in the context
- **Definition:** same as given in the context
- **Detailed information:** same as given in the context
- **State Amendments:** If provided
- **Punishments and Fines:** from "- Punishment and Fines:-" only if provided
then again start with the upper format for next section
                                                   
input: {input}
context: {context}
""")


KeywordPrompt = """
Strictly do not include Date and time, Location, Parties involved, Type of vehicle(s), person name, address, phone number, email, etc.
strictly do not include the words like "MVA Sections","Quit", "Exit", "MVA Section", "mva section", "MVA Sections = TRUE".

Follow below rules:
- Smartly Extract only the key terms, phrases, and important entities which are present in the given context dynamically. Strictly do not include words or phrases which are not related to this Strictly. 
- Smartly add similar/synonymes words to the extracted keywords.
- Strictly include the words which are related to Motor Vehicle Act Compliance.
- Strictly do not include any word from expample if it is not related to history.
- Avoid forming sentences or narratives.
- Focus on capturing essential topics, names, concepts, and actions.
- Strictly do not include any personal information.
- Strictly do not include any irrelevant information.

Example keywords: type of vehicle(s), nature of the collision, injuries, 
damages, weather, and road conditions, Cover legal implications such as applicable 
traffic laws, fault determination, insurance claims, liability, potential violations, 
penalties, and relevant legal precedents, legal rights, compensation, filing complaints, 
and interactions with law enforcement or insurance companies, legal rights, compensation, 
filing complaints, Traffic signal violation, Excessive speed, mentally or physically unfit to drive,
speed limit, traffic rules violation, traffic laws violation, traffic regulations, 
traffic signs violation, traffic signal violation, Overtaking, lane discipline,
overcrowded vehicle, overloading, driving under the influence of alcohol or drugs,
driving without a license, driving without insurance, driving without a helmet,
driving without a seatbelt, driving without a registration certificate,
driving without a pollution under control certificate, driving without a permit,
driving without a fitness certificate, driving without a valid permit, alcohol or drugs,
drunken, etc.
{history}
{question}
"""


SummaryPrompt = """
Summarize the conversation based on the user's query and the assistant's responses capturing
semantic meaning. If the user says yes to any question, summarize it as a positive response and viceversa.
- Strictly do not refresher the conversation.
Summarize the conversation by capturing key events, critical details, 
and relevant legal references discussed regarding a motor vehicle and 
traffic-related incident. Highlight the main concerns raised by the user, 
the assistant’s inquiries, and responses, ensuring clarity and coherence while 
avoiding redundancy. Focus on accident details, legal aspects, and actionable insights.
"""

def chat_with_llm(llm, prompt_template, user_input, memory):
    history = memory.load_memory_variables({})["history"]
    prompt = prompt_template.format(history=history, question=user_input)
    response = llm.invoke([HumanMessage(content=prompt)])
    memory.save_context({"input": user_input}, {"output": response.content})
    return response.content

def conversation_memory(llm, SummaryPrompt):
    return ConversationSummaryMemory(llm=llm, return_messages=True, summarypromt=SummaryPrompt)


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

def make_retrieval_chain(llm, prompt, vector_data):
    '''
    - (similarity_score_threshold=0.3)
    - (search_type="mmr", search_kwargs={"k": 5})
    - (search_kwargs={"k": 1})
    '''
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vector_data.as_retriever(search_type="mmr", search_kwargs={"k": 8})
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    return retrieval_chain

def clean_retrieved_response(response):
    raw_text = response['answer']
    clean_text = re.sub(r'\*\*', '', raw_text)
    return clean_text

# Initialize ChatGroq LLM (Replace with your API key)
# - llama3-8b-8192
# - llama3-70b-8192
# - deepseek-r1-distill-llama-70b
# - qwen-2.5-32b

llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="qwen-2.5-32b")
summary_llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-70b-8192")
embedding = load_embedding()
load_vectorDB = load_data_from_VectorDB(embedding)
memory = conversation_memory(summary_llm, SummaryPrompt)

st.title("Motor Vehicle Act Compliance LLM Chatbot")
st.subheader("A conversational AI chatbot powered by LLMs")

# ✅ Ensure session state is initialized
if "memory" not in st.session_state:
    st.session_state.memory = conversation_memory(summary_llm, SummaryPrompt)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
user_input = st.chat_input("Ask me anything...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Load chat history from session memory
    chat_memory = st.session_state.memory.load_memory_variables({})
    history = chat_memory.get("history", [])

    # Generate LLM response for MVA Sections Retrieval
    prompt = SystemPrompt.format(history=history, question=user_input)
    response = llm.invoke([HumanMessage(content=prompt)])
    model_output = response.content

    # Save conversation history to session state memory
    st.session_state.memory.save_context({"input": user_input}, {"output": model_output})

    # Debugging: Display updated memory
    # updated_memory = st.session_state.memory.load_memory_variables({})
    # st.write(updated_memory["history"])

    # Check if retrieval is needed
    if any(keyword in user_input.lower() for keyword in ["mva section", "mva sections", "quit", "exit"]) or "MVA Sections = TRUE" in model_output:
        retrieval_chain = make_retrieval_chain(llm, RetrievalPrompt, load_vectorDB)

        # Reload chat history after saving
        chat_memory = st.session_state.memory.load_memory_variables({})
        history = chat_memory.get("history", [])

        chat_summary = history[0].content if history else ""

        # Generate LLM response for keywords extraction
        prompt = KeywordPrompt.format(history=history, question=user_input)
        response = llm.invoke([HumanMessage(content=prompt)])
        keywords = response.content

        # st.write("Keywords extracted:", keywords) # Debugging

        # Retrieve relevant information
        retrieval_response = retrieval_chain.invoke({"input": keywords})
        clean_response = clean_retrieved_response(retrieval_response)
        # final_response = chat_summary + "\n" + clean_response

        # Clear Chat Summary Memory
        st.session_state.memory.clear()

        # Check if memory is empty
        # if st.session_state.memory.load_memory_variables({})["history"][0].content == "":  # Works for lists, dicts, and other empty collections
            # st.write("\n\n========================Memory cleared!========================\n\n")

        # Append final response and display
        st.session_state.messages.append({"role": "assistant", "content": clean_response})
        with st.chat_message("assistant"):
            st.markdown(clean_response)

    else:
        st.session_state.messages.append({"role": "assistant", "content": model_output})
        with st.chat_message("assistant"):
            st.markdown(model_output)
