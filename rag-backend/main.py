from fastapi import FastAPI, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from rag_impl import load_rag_chain
from utils.input_filteration_utils import classify_query, check_openai_moderation

app = FastAPI()
qa_chain = load_rag_chain()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory user auth
fake_users = {
    "zafar": "123"
}

def authenticate(username: str = Form(...), password: str = Form(...)):
    if fake_users.get(username) != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return username

@app.post("/login")
def login(user: str = Depends(authenticate)):
    return {"message": f"✅ Welcome, {user}!"}

@app.post("/query")
def query_rag(question: str = Form(...)):
    #question = "What are the vacation policies and who is Alice Johnson's manager?"
    
    allowed, reason = classify_query("employee", question)
    if not allowed:
        result = {"result": "Query is Invalid! Please modfiy your query."}
        return {"answer": result["result"]}

    flagged = check_openai_moderation(question)
    if flagged:
        result = {"result": "Query is Abusive! Please modfiy your query."}
        return {"answer": result["result"]}

    result = qa_chain.invoke({"query": question})

    # Show answer and source info
    print("\nSources:")
    for doc in result["source_documents"]:
        print(f"- {doc.metadata['source']} (AccessLevel: {doc.metadata['access_level']})")

    return {"answer": result["result"]}
