import os
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama  
#from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
#from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain

# --- CONFIGURATION ---
PDF_FOLDER = "knowledge_base"   
DB_PATH = "chroma_db"

def setup_rag():
    """
    Checks if the Vector DB exists. If not, creates it from PDFs.
    """
    # 1. Check if DB already exists to avoid re-scanning every time (Speed Boost)
    if os.path.exists(DB_PATH) and os.listdir(DB_PATH):
        print(f"✅ Vector DB found at '{DB_PATH}'. Using existing knowledge.")
        embeddings = OllamaEmbeddings(model="llama3.2")
        return Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

    # 2. Check if PDF folder exists
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
        print(f"⚠️ Created folder '{PDF_FOLDER}'. Please put your PDFs inside it.")
        return None

    # 3. Load PDFs
    print(f"Scanning '{PDF_FOLDER}' for PDFs...")
    all_docs = []
    files = [f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')]
    
    if not files:
        print("❌ No PDF files found. RAG cannot work.")
        return None

    for file_name in files:
        file_path = os.path.join(PDF_FOLDER, file_name)
        try:
            loader = PyPDFLoader(file_path)
            all_docs.extend(loader.load())
        except Exception as e:
            print(f"   Error loading {file_name}: {e}")

    if not all_docs:
        return None

    # 4. Process and Index
    print(f"Processing {len(all_docs)} pages...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(all_docs)

    print("Creating Chroma Search Index...")
    embeddings = OllamaEmbeddings(model="llama3.2")
    
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    print("✅ Knowledge Base Updated!")
    return vectorstore

def ask_rag_advice(data, prediction_result):
    
    # 1. Setup the Brain
    vectorstore = setup_rag()
    if not vectorstore:
        return "System Tip: Please upload a PDF to the 'knowledge_base' folder to get AI advice."

    retriever = vectorstore.as_retriever()
    llm = ChatOllama(model="llama3.2", temperature=0.7)

    # 2. Convert Data to Descriptive Text
    user_desc = (
        f"The user is a {data['age']} year old {'Male' if int(data['gender'])==1 else 'Female'}.\n"
        f"Current Status: {prediction_result}.\n"
        f"Stats:\n"
        f"- Sleep Duration: {data['duration']} hours (Low if < 7)\n"
        f"- Sleep Quality: {data['quality']}/10\n"
        f"- Stress Level: {data['stress']}/10 (High if > 5)\n"
        f"- Daily Steps: {data['daily_steps']}\n"
        f"- Blood Pressure: {data['bp_sys']}/{data['bp_dia']}"
    )

    # 3. STRICT System Prompt to prevent hallucinations
    system_prompt = (
        "You are an empathetic, professional Sleep Health Coach. "
        "Your goal is to give ONE practical tip based on the provided Context and the User's specific stats.\n\n"
        
        "ANALYSIS RULES:\n"
        "1. Identify the user's WORST metric from the stats (e.g., Is stress high? Is sleep duration low?).\n"
        "2. Retrieve advice from the Context that specifically targets that worst metric.\n"
        "3. **CRITICAL:** If the user has NOT explicitly reported using alcohol, caffeine, or smoking, **DO NOT mention them**.\n"
        "4. **FORMATTING:** Do NOT use citations like (ref: Context) or [1]. Write naturally.\n\n"
        
        "Context:\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "User Data: {input}\n\nPlease provide a short, personalized sleep recommendation.")
    ])

    # 4. Run the Chain
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    try:
        response = rag_chain.invoke({
            "input": user_desc
        })
        return response["answer"]
    except Exception as e:
        print(f"RAG Error: {e}")
        return "Sleep Tip: Try to maintain a consistent sleep schedule."


# --- TEST BLOCK ---
if __name__ == "__main__":
    print("--- 🧪 TESTING RAG SYSTEM ISOLATED ---")
    
    # 1. Fake Data (High Stress, Low Sleep)
    fake_data = {
        'age': 30, 'gender': 1, 'duration': 5, 'quality': 4,
        'stress': 8, 'daily_steps': 3000, 'bp_sys': 120, 'bp_dia': 80
    }
    
    # 2. Fake Prediction
    fake_prediction = "Insomnia Detected"

    # 3. Run
    print(" Asking AI...")
    result = ask_rag_advice(fake_data, fake_prediction)
    
    print("\n--- 🤖 AI RESPONSE ---")
    print(result)


# --- TEST BLOCK (Add this to the bottom) ---
if __name__ == "__main__":
    print("--- 🧪 TESTING RAG SYSTEM ISOLATED ---")
    
    # 1. Fake Data (Simulating what the App sends)
    fake_data = {
        'age': 30,
        'gender': 1,       # Male
        'duration': 5,     # Low sleep
        'quality': 4,
        'stress': 8,
        'daily_steps': 3000
    }
    
    # 2. Fake Prediction
    fake_prediction = "Sleep Disorder Detected (Insomnia)"

    # 3. Run the function
    print(" Asking AI...")
    result = ask_rag_advice(fake_data, fake_prediction)
    
    print("\n--- 🤖 AI RESPONSE ---")
    print(result)