from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from openai import OpenAI
from fastapi import HTTPException
import json
import re

MAX_QUERY_LENGTH = 1000

FORBIDDEN_PATTERNS = [
    r"(?i)ignore.*instruction",
    r"(?i)forget.*instruction",
    r"(?i)you are now",
    r"(?i)act as",
    r";",  # semicolon, common in injections
]

"""
| User Role | Allowed Queries                | Blocked Queries                        |
| --------- | ------------------------------ | -------------------------------------- |
| employee  | General HR questions, own info | Other employees' salaries / PII        |
| external  | Public HR policies             | Any employee data (salary, SSN, email) |
"""

# Define prompt template
system_prompt_for_input_filteration = PromptTemplate(
    input_variables=["user_role", "user_query"],
    template="""
You are a security policy checker for an HR chatbot.
Your job is to decide if a question is allowed for the given user role.

Company Policy:
- External users may only ask about public HR policies.
- External users may NOT ask about employee salaries, SSNs, emails, or personal records.

- Employees may ask about HR policies or their own info.
- Employees may NOT ask for other employees' salaries, SSNs, emails, or personal records.

- Admin may ask about anything inside the HR policeis, other's info, their own info, employee salaries, SSNs, emails, or personal records.
- Admin is not restricted from anything.
-
Decide if this query is allowed.

User Role: {user_role}
Query: {user_query}

Answer in JSON:

{{
  "allowed": true,
  "reason": "explanation"
}}
"""
)

# Build Classifier chain
llm = ChatOpenAI(temperature=0.0, model="gpt-3.5-turbo")
classifier_chain = LLMChain(llm=llm, prompt=system_prompt_for_input_filteration)

# Function to classify
def classify_query(user_role, user_query):
    result = classifier_chain.run({
        "user_role": user_role,
        "user_query": user_query
    })
    try:
        parsed = json.loads(result)
        return parsed["allowed"], parsed["reason"]
    except Exception:
        return False, "Failed to parse classifier output"

def check_openai_moderation(query: str) -> bool:
    client = OpenAI()
    response = client.moderations.create(model="omni-moderation-latest", input=query)
    flagged = response.results[0].flagged
    return flagged

def validate_input(query: str):
    if len(query) > MAX_QUERY_LENGTH:
        return (False, "Query too long")
    if contains_forbidden_patterns(query):
        return (False, "Query blocked by policy")
    return (True, None)

def contains_forbidden_patterns(query: str) -> bool:
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, query):
            return True
    return False