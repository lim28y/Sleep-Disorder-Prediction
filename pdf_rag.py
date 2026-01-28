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
    """ Checks if the Vector DB exists. If not, creates it from PDFs. """
    if os.path.exists(DB_PATH) and os.listdir(DB_PATH):
        print(f"Vector DB found at '{DB_PATH}'. Using existing knowledge.")
        embeddings = OllamaEmbeddings(model="llama3.2")
        return Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
        print(f"Created folder '{PDF_FOLDER}'. Please put your PDFs inside it.")
        return None

    print(f"Scanning '{PDF_FOLDER}' for PDFs...")
    all_docs = []
    files = [f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')]
    
    if not files:
        print("No PDF files found. RAG cannot work.")
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
    print(" Knowledge Base Updated!")
    return vectorstore

def ask_rag_advice(data, prediction_result):
    
    vectorstore = setup_rag()
    if not vectorstore:
        return "System Tip: Please upload a PDF to the 'knowledge_base' folder."

    # Temperature 0.3 keeps it strict (so it follows the format)
    llm = ChatOllama(model="llama3.2", temperature=0.3)
    
    retriever = vectorstore.as_retriever()
    
    # 1. USER DATA BLOCK (Context for the AI)
    user_desc = (
        f"PATIENT DATA:\n"
        f"- Sleep Duration: {data['duration']} hours\n"
        f"- Sleep Quality: {data['quality']}/10\n"
        f"- Stress Level: {data['stress']}/10\n"
        f"- Daily Steps: {data['daily_steps']}\n"
        f"- Blood Pressure: {data['bp_sys']}/{data['bp_dia']}\n"
        f"- Diagnosis: {prediction_result}\n"
    )

    # 2. THE "FORMATTING" PROMPT
    # This instructs the AI to copy the exact style you want.
    system_prompt = (
        "You are 'SleepSync AI', a professional sleep coach.\n"
        "Your goal is to analyze the Patient Data and provide advice using the specific format below.\n\n"

        "RULES:\n"
        "1. **Use Arrows:** When listing stats, use '→' to explain what the number means (e.g., '4 hours → Significantly below average').\n"
        "2. **Be Specific:** Do not just say 'Sleep more.' Say 'Aim for 6 hours first.'\n"
        "3. **Use the PDF:** Incorporate medical facts from the context if possible.\n\n"

        "REQUIRED RESPONSE FORMAT:\n"
        "🛌 Sleep Overview\n"
        "- Sleep duration: [Value] → [Short Analysis]\n"
        "- Sleep quality: [Value]/10 → [Short Analysis]\n"
        "- Stress level: [Value]/10 → [Short Analysis]\n"
        "💡 [One sentence summary of how these 3 things interact]\n\n"

        "❤️ Physical Health Indicators\n"
        "- Blood pressure: [Value] mmHg\n"
        "  [Bullet point explaining if this is high/normal]\n"
        "- Daily steps: [Value]\n"
        "  [Bullet point explaining if this is sedentary/active]\n\n"

        "Key Areas to Improve\n"
        "1. **[Goal 1 Title]**\n"
        "   [Specific advice based on PDF context]\n"
        "2. **[Goal 2 Title]**\n"
        "   [Specific advice based on PDF context]\n"
        "3. **[Goal 3 Title]**\n"
        "   [Specific advice based on PDF context]\n\n"

        "Final Encouragement\n"
        "[One motivating sentence]\n\n"

        "MEDICAL CONTEXT:\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Patient Data:\n{input}")
    ])

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    try:
        response = rag_chain.invoke({
            "input": user_desc
        })
        return response["answer"]
    except Exception as e:
        print(f"RAG Error: {e}")
        return "System Tip: Try to maintain a consistent sleep schedule."





