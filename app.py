from def_functions import *
from prompts import *

# Initialize ChatGroq LLM (Replace with your API key)
# llama3-8b-8192
# llama3-70b-8192
# deepseek-r1-distill-llama-70b
# qwen-2.5-32b

llm = ChatGroq(groq_api_key="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", model_name="qwen-2.5-32b")
embedding = load_embedding()
load_vectorDB = load_data_from_VectorDB(embedding)
memory = conversation_memory()

while True:

    user_input = input("Enter: ")

    if user_input.lower() in ["quit", "bye"]:
        print("Goodbye!")
        print("Chat Summary:", memory.load_memory_variables({})["history"])
        break
    
    response = chat_with_llm(llm, SystemPrompt, user_input, memory)
    print("1.======"+response)
    print("\n=============================================\n")

    if "MVA Sections = TRUE" in response:
        
        retrieval_chain = make_retieval_chain(llm, RetrievalPrompt, load_vectorDB)

        chat_summary = memory.load_memory_variables({})["history"][0]        
        history = chat_summary.content
        response = retrieval_chain.invoke({"input":history})

        # # # Save conversation in memory
        # memory.save_context({"input": user_input}, {"output": response['answer']})

        clean_retreived_response(response)
        print("\n=============================================\n")
        print("Goodbye!")
        print("Chat Summary:", memory.load_memory_variables({})["history"])
        break

# challan was issued by traffic police even after i followed the traffic rules
# please provide details about MVA Sections