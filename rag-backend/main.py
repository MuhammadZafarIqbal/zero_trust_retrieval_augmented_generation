from fastapi import FastAPI, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_impl import load_rag_chain
from utils.rag_utils import set_allowed_access_level, load_logger
from utils.input_filteration_utils import (
    classify_query, 
    check_openai_moderation,
    validate_input
)
from utils.output_filteration_utils import (
    presidio_post_process,
    is_flagged_by_openai_moderation
)
from auth import get_current_user
import json
from datetime import datetime, timezone

app = FastAPI()
qa_chain = load_rag_chain()
logger = load_logger()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    role: str

@app.post("/query")
def query_rag(data: QueryRequest, user=Depends(get_current_user)):
    user_role = data.role
    question = data.question
    user_name = user["name"]
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_name": user["name"],
        "query": question
    }

    allowed, reason = classify_query(user_role, question)
    log_entry["classifier_response"] = {"is_allowed": allowed, "reason":reason}
    if not allowed:
        result = {"result": "Query is Invalid! Please modfiy your query."}
        log_entry["forced-termination-response"] = result["result"]
        logger.info(json.dumps(log_entry))
        return {"answer": result["result"]}

    flagged = check_openai_moderation(question)
    log_entry["input-moderation-response"] = {"is_flagged" : flagged}
    if flagged:
        result = {"result": "Query is Abusive! Please modfiy your query."}
        log_entry["forced-termination-response"] = result["result"]
        logger.info(json.dumps(log_entry))
        return {"answer": result["result"]}

    is_valid, reason = validate_input(question)
    log_entry["input-validation-response"] = {"is-valid": is_valid, "reason": reason}
    if not is_valid:
        result = {"result": reason}
        log_entry["forced-termination-response"] = result["result"]
        logger.info(json.dumps(log_entry))
        return {"answer": result["result"]}
    
    system_prompt = """You are an HR assistant. You MUST answer only if the user is authorized. 
    Never reveal private data unless explicitly allowed. Current user role: {user_role}. 
    Only answer if the user is allowed to access the retrieved context. 
    Otherwise say 'Access Denied'."""
    ALLOWED_LEVELS = set_allowed_access_level(user_role)
    log_entry["allowed-documents-access-level"] = list(ALLOWED_LEVELS)
    qa_chain.retriever.search_kwargs["filter"] = {"access_level": {"$in": ALLOWED_LEVELS}}
    result = qa_chain.invoke({"query": question, "system_prompt": system_prompt})
    log_entry["raw-llm-output"] = result["result"]

    log_list = []
    for doc in result["source_documents"]:
        log_list.append(f"File: {doc.metadata['source']} (AccessLevel: {doc.metadata['access_level']})")
    log_entry["llm-source-documents"]=log_list

    llm_output = result["result"]
    # Post-process with Presidio
    result["result"] = presidio_post_process(user_role, user_name, llm_output)
    log_entry["anonymizer-processed-output"] = result["result"]
    
    flagged = is_flagged_by_openai_moderation(result["result"])
    log_entry["output-moderation-response"]= {"is-flagged": flagged}
    if flagged:
        result = {"result": "Sorry my response was Abusive! Please modfiy your query. or try again!"}
        log_entry["forced-termination-response"] = result["result"]
        logger.info(json.dumps(log_entry))
        return {"answer": result["result"]}
    
    logger.info(json.dumps(log_entry))
    return {"answer": result["result"]}
