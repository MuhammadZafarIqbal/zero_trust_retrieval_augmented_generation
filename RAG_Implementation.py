import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains.retrieval_qa.base import RetrievalQA

# Load your OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY", None)
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

# Load and split the document
loader = TextLoader("docs.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

# Embed and store in FAISS
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
vectorstore = FAISS.from_documents(docs, embeddings)

# Create retriever and QA chain
retriever = vectorstore.as_retriever()
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_api_key)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# Ask a question
query = "What did Einstein win the Nobel Prize for?"
result = qa_chain.invoke(query)
print("Answer:", result)
