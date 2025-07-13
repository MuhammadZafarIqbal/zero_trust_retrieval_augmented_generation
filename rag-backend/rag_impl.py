import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains.retrieval_qa.base import RetrievalQA
from utils.rag_utils import get_raw_data, set_allowed_access_level

# Load your OpenAI API key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY", None)
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

def load_rag_chain():
    user_role = "admin"
    # Paths and filenames
    data_folder = Path("data")
    file_names = [
        "employee_directory.txt",
        "policy_documents.txt",
        "salary_grades.txt"
    ]

    # Load files and extract metadata
    raw_documents = get_raw_data(data_folder, file_names)
    
    # Split into chunks
    text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0)
    split_docs = text_splitter.split_documents(raw_documents)

    #Embed and store in FAISS
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.from_documents(split_docs, embeddings)

    #Create a retriever with access-level filtering
    ALLOWED_LEVELS = set_allowed_access_level(user_role)
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 4,
            "filter": {"access_level": {"$in": ALLOWED_LEVELS}}  # Zero Trust style enforcement
        }
    )

    #Build QA chain
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_api_key)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    return qa_chain