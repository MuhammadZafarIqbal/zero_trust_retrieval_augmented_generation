from fastapi import FastAPI, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from rag_impl import load_rag_chain

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
    #query = "What did Einstein win the Nobel Prize for?"
    result = qa_chain.invoke({"query": question})
    return {"answer": result["result"]}
