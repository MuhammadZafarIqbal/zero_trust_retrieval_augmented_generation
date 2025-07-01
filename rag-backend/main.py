from fastapi import FastAPI, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from rag_impl import load_rag_chain
from utils.input_filteration_utils import (
    classify_query, 
    check_openai_moderation,
    validate_input
)
from auth import get_current_user

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
def query_rag(question: str = Form(...), user=Depends(get_current_user)):
    #question = "What are the vacation policies and who is Alice Johnson's manager?"
    user_role = "admin"
    
    allowed, reason = classify_query(user_role, question)
    if not allowed:
        result = {"result": "Query is Invalid! Please modfiy your query."}
        return {"answer": result["result"]}

    flagged = check_openai_moderation(question)
    if flagged:
        result = {"result": "Query is Abusive! Please modfiy your query."}
        return {"answer": result["result"]}

    is_valid, reason = validate_input(question)
    if not is_valid:
        print(reason)
        result = {"result": reason}
        return {"answer": result["result"]}
    
    system_prompt = """You are an HR assistant. You MUST answer only if the user is authorized. 
    Never reveal private data unless explicitly allowed. Current user role: {user_role}. 
    Only answer if the user is allowed to access the retrieved context. 
    Otherwise say 'Access Denied'."""
    result = qa_chain.invoke({"query": question, "system_prompt": system_prompt})

    # Show answer and source info
    print("\nSources:")
    for doc in result["source_documents"]:
        print(f"- {doc.metadata['source']} (AccessLevel: {doc.metadata['access_level']})")

    #print(f"User: {user['name']} ({user['preferred_username']})")
    return {"answer": result["result"]}
