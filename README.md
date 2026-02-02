# Zero Trust Retrieval Augmented Generation

Lightweight reference implementation of a secure RAG pipeline with a React frontend and a FastAPI backend. The project demonstrates:
- Document ingestion + embedding-based retrieval.
- LLM-backed QA over retrieved context.
- Role-based access control, input/output filtering, and moderation hooks.

---

Contents
- Backend: FastAPI service that exposes a /query endpoint — see [rag-backend/main.py](rag-backend/main.py) and the [`query_rag`](rag-backend/main.py) handler.
- RAG chain: loader and vectorstore setup in [rag-backend/rag_impl.py](rag-backend/rag_impl.py) via the [`load_rag_chain`](rag-backend/rag_impl.py) function.
- Security helpers:
  - Input classification & validation: [`classify_query`](rag-backend/utils/input_filteration_utils.py), [`validate_input`](rag-backend/utils/input_filteration_utils.py), [`check_openai_moderation`](rag-backend/utils/input_filteration_utils.py)
  - Output post-processing & anonymization: [`presidio_post_process`](rag-backend/utils/output_filteration_utils.py), [`is_flagged_by_openai_moderation`](rag-backend/utils/output_filteration_utils.py)
  - RBAC helpers and logging: [`set_allowed_access_level`](rag-backend/utils/rag_utils.py), [`load_logger`](rag-backend/utils/rag_utils.py)
  - Token validation: [`get_current_user`](rag-backend/auth.py)

- Frontend: React app that authenticates with MSAL and calls the backend:
  - App entry: [rag-frontend/src/App.js](rag-frontend/src/App.js)
  - Authentication config: [rag-frontend/src/authConfig.js](rag-frontend/src/authConfig.js)
  - Pages: [rag-frontend/src/Home.js](rag-frontend/src/Home.js), [rag-frontend/src/QueryForm.js](rag-frontend/src/QueryForm.js)

- Example data documents (ingested into the vectorstore):
  - [rag-backend/data/employee_directory.txt](rag-backend/data/employee_directory.txt)
  - [rag-backend/data/policy_documents.txt](rag-backend/data/policy_documents.txt)
  - [rag-backend/data/salary_grades.txt](rag-backend/data/salary_grades.txt)

---

Quickstart (development)

1. Backend
- Create a .env containing your OpenAI API key:
  - OPENAI_API_KEY=your_api_key_here
- From project root start the backend (creates venv, installs deps and runs uvicorn):
  - bash rag-backend/demo.sh
- The backend listens on http://localhost:8000 and exposes:
  - POST /query — handled in [rag-backend/main.py](rag-backend/main.py)

2. Frontend
- From project root:
  - cd rag-frontend
  - npm install
  - npm start
- The frontend runs on http://localhost:3000 and uses MSAL configured in [rag-frontend/src/authConfig.js](rag-frontend/src/authConfig.js). It sends requests to the backend at http://localhost:8000/query (see [rag-frontend/src/QueryForm.js](rag-frontend/src/QueryForm.js)).

---

Important configuration & notes

- OpenAI
  - The RAG pipeline uses OpenAI embeddings and chat models in [rag-backend/rag_impl.py](rag-backend/rag_impl.py). Set $OPENAI_API_KEY before starting the backend.
- Authentication
  - The frontend uses MSAL and a configured client ID / authority in [rag-frontend/src/authConfig.js](rag-frontend/src/authConfig.js).
  - The backend validates incoming bearer tokens in [rag-backend/auth.py](rag-backend/auth.py) via Microsoft's JWKS endpoint (`get_current_user`).
- Access control
  - Access-level mapping is defined in [`set_allowed_access_level`](rag-backend/utils/rag_utils.py).
  - The retriever filter is set in [rag-backend/main.py](rag-backend/main.py) prior to invoking the QA chain.
- Input & output safety
  - Input classification (role policy) is performed by [`classify_query`](rag-backend/utils/input_filteration_utils.py).
  - Inputs are sent through an OpenAI moderation check via [`check_openai_moderation`](rag-backend/utils/input_filteration_utils.py).
  - Responses are post-processed by Presidio via [`presidio_post_process`](rag-backend/utils/output_filteration_utils.py) to redact sensitive entities (with special handling to avoid redacting the requesting employee's own name).
  - Output moderation is checked with [`is_flagged_by_openai_moderation`](rag-backend/utils/output_filteration_utils.py).

---

Development tips

- Rebuilding vectorstore: The vectorstore is created at runtime inside [`load_rag_chain`](rag-backend/rag_impl.py). If you change data files under [rag-backend/data/](rag-backend/data/), restart the backend to rebuild embeddings.
- Logging: Application activity is written to rag.log using the logger from [`load_logger`](rag-backend/utils/rag_utils.py).
- Tests: Frontend contains a basic test in [rag-frontend/src/App.test.js](rag-frontend/src/App.test.js).

---

Security considerations
- The system enforces role-based document access (public / internal / confidential) using metadata extracted by [`get_raw_data`](rag-backend/utils/rag_utils.py).
- The input classifier and moderation hooks aim to block prompt injection and abusive content before sending queries to the LLM.
- The output pipeline redacts PII using Presidio unless the user is an admin or the entity equals the requesting employee's name.

---

Files of interest (quick links)
- Backend: [rag-backend/main.py](rag-backend/main.py), [rag-backend/rag_impl.py](rag-backend/rag_impl.py), [rag-backend/auth.py](rag-backend/auth.py)
- Utils: [rag-backend/utils/rag_utils.py](rag-backend/utils/rag_utils.py), [rag-backend/utils/input_filteration_utils.py](rag-backend/utils/input_filteration_utils.py), [rag-backend/utils/output_filteration_utils.py](rag-backend/utils/output_filteration_utils.py)
- Frontend: [rag-frontend/src/App.js](rag-frontend/src/App.js), [rag-frontend/src/Home.js](rag-frontend/src/Home.js), [rag-frontend/src/QueryForm.js](rag-frontend/src/QueryForm.js), [rag-frontend/src/authConfig.js](rag-frontend/src/authConfig.js)

---

License & acknowledgements
- This is a sample/demo project. Review and adapt security controls before using with real data.
- Built with LangChain, OpenAI, Presidio, FastAPI, MSAL, React.
