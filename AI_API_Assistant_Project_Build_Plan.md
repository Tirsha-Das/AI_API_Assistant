# AI API Assistant — Project Build Plan

## 1. Project Goal

Build a secure AI-powered API assistant that can:

- Understand API documentation
- Search documentation using RAG
- Store embeddings in a vector database
- Use an AI Agent to decide what to do
- Use MCP tools to interact with APIs
- Authenticate users with JWT
- Support OAuth2 / Google login
- Enforce user permissions before API actions
- Store chat history and tool execution history
- Run completely locally with free/open-source tools

The project should be built incrementally. Do NOT start with the AI Agent or MCP.

---

# 2. Recommended Tech Stack

## Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL

## Authentication
- JWT
- OAuth2 / Google OAuth

## AI
- Ollama
- Local open-source LLM
- sentence-transformers for embeddings

## RAG
- Qdrant (run locally)
- Document chunking
- Embeddings
- Similarity search

## Agent
- Python-based agent orchestration
- Tool calling
- RAG tool
- MCP tools

## MCP
- MCP Python SDK
- Custom MCP server exposing API tools

## Frontend
- React
- TypeScript

## Infrastructure
- Docker / Docker Compose
- Git + GitHub

---

# 3. Build Order

Follow this order:

```text
Phase 1  → Project setup
Phase 2  → Database + basic backend
Phase 3  → Authentication
Phase 4  → Fake API
Phase 5  → Documentation upload
Phase 6  → RAG + Vector DB
Phase 7  → Basic AI chat
Phase 8  → AI Agent
Phase 9  → MCP integration
Phase 10 → Authorization + safety
Phase 11 → Chat/tool history
Phase 12 → React frontend
Phase 13 → Docker
Phase 14 → Testing + documentation
```

---

# PHASE 1 — Project Setup

## Goal

Create the basic backend project.

Suggested structure:

```text
ai-api-assistant/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── agents/
│   │   ├── rag/
│   │   └── mcp/
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│
├── mcp-server/
│
├── fake-api/
│
├── docker-compose.yml
└── README.md
```

First make sure:

```text
GET /health
```

returns:

```json
{
  "status": "ok"
}
```

Do not add AI yet.

---

# PHASE 2 — PostgreSQL + Basic Backend

## Goal

Connect FastAPI to PostgreSQL.

Create initial tables:

```text
users
documents
conversations
messages
tool_executions
```

At this stage:

- Create DB connection
- Create SQLAlchemy models
- Create migrations if desired
- Create basic CRUD endpoints
- Test using Postman/Swagger

Keep it simple.

---

# PHASE 3 — Authentication

## Goal

Secure the backend before adding AI functionality.

Implement:

```text
POST /auth/register
POST /auth/login
POST /auth/refresh
GET  /users/me
```

Use:

- Password hashing
- JWT access token
- Refresh token
- Protected routes

Example:

```text
Login
  ↓
JWT access token
  ↓
Authorization: Bearer <token>
  ↓
Protected endpoint
```

Make sure unauthenticated users cannot access protected endpoints.

---

# PHASE 4 — OAuth

Add Google OAuth after normal JWT login works.

Flow:

```text
User
 ↓
Google Login
 ↓
OAuth callback
 ↓
Find/create user
 ↓
Issue JWT
 ↓
Frontend
```

Do not start with OAuth. JWT should work first.

---

# PHASE 5 — Build Your Own Fake API

## Goal

Create APIs that your AI assistant can eventually call.

Example:

```text
Customer API

POST   /customers
GET    /customers/{id}
PUT    /customers/{id}
DELETE /customers/{id}

Order API

GET    /orders/{id}
GET    /customers/{id}/orders
```

Use FastAPI.

Store fake data in PostgreSQL.

Example:

```json
{
  "id": 101,
  "name": "Rahul",
  "email": "rahul@test.com"
}
```

This is important because you do not need paid external APIs.

---

# PHASE 6 — API Documentation

Create documentation for your fake APIs.

Use:

```text
OpenAPI / Swagger JSON
Markdown
```

Example:

```text
customer-api.yaml
order-api.yaml
```

Your assistant should eventually understand these documents.

Add:

```text
POST /documents/upload
GET  /documents
DELETE /documents/{id}
```

Initially just save the uploaded document metadata/content.

Do not implement RAG yet.

---

# PHASE 7 — RAG + Vector Database

## Goal

Make API documentation searchable.

Pipeline:

```text
Document
   ↓
Extract text
   ↓
Chunk text
   ↓
Generate embeddings
   ↓
Qdrant
```

For a question:

```text
"How do I create a customer?"
```

Pipeline:

```text
Question
   ↓
Embedding
   ↓
Qdrant similarity search
   ↓
Relevant API documentation
```

Start with a simple `/search` endpoint.

Example:

```text
GET /rag/search?q=how to create customer
```

Return the most relevant chunks.

Only move forward after this works reliably.

---

# PHASE 8 — Basic AI Chat

Now connect Ollama.

Start WITHOUT an agent.

Flow:

```text
User question
     ↓
RAG search
     ↓
Relevant documentation
     ↓
LLM
     ↓
Answer
```

Example:

```text
User:
How do I create a customer?

RAG:
POST /customers
Required fields:
name
email
phone

LLM:
To create a customer, call POST /customers...
```

At this stage the AI should only explain APIs.

It should NOT execute APIs yet.

---

# PHASE 9 — AI Agent

Now introduce the Agent.

The agent should decide:

```text
Do I need documentation?
Do I need an API tool?
Do I need to ask the user for more information?
```

Example:

```text
User:
How do I create a customer?

Agent
 ↓
RAG search
 ↓
Explain API
```

Another request:

```text
User:
Create Rahul with rahul@test.com

Agent
 ↓
Understand intent
 ↓
Find required API
 ↓
Check required parameters
 ↓
Call appropriate tool
```

Start with only 1–2 tools.

Do NOT create 20 tools immediately.

---

# PHASE 10 — MCP Integration

Now convert API operations into MCP tools.

Start with:

```text
get_customer
create_customer
get_orders
```

Example:

```text
AI Agent
    ↓
MCP
    ↓
create_customer
    ↓
Fake Customer API
    ↓
Response
    ↓
AI Agent
    ↓
User
```

The important concept to understand:

```text
Agent ≠ MCP

Agent decides WHAT tool to use.

MCP provides a standard way for the agent to access tools/data.
```

After the basic tools work, add more tools.

---

# PHASE 11 — Authorization + Safety

This is an important backend feature.

Create permissions such as:

```text
READ_CUSTOMER
CREATE_CUSTOMER
UPDATE_CUSTOMER
DELETE_CUSTOMER
READ_ORDER
```

Before an MCP tool executes:

```text
JWT
 ↓
User
 ↓
Permission check
 ↓
MCP tool
 ↓
API
```

Example:

```text
User asks:
Delete customer 101

 ↓

Check JWT
 ↓
Check DELETE_CUSTOMER permission
 ↓
Ask confirmation
 ↓
MCP delete_customer
```

Never let the LLM itself decide whether the user is authorized.

Authorization must happen in backend code.

---

# PHASE 12 — Confirmation for Dangerous Operations

Require confirmation for:

```text
DELETE
UPDATE
financial actions
other irreversible actions
```

Example:

```text
AI:
Deleting customer 101 is an irreversible action.
Do you want to continue?

User:
Yes

 ↓

Backend verifies permission
 ↓
MCP tool executes
```

This gives you a strong security story for interviews.

---

# PHASE 13 — Chat + Tool History

Store:

```text
conversation
messages
tool executions
```

Example:

```text
Conversation
 ├── User message
 ├── Agent action
 ├── RAG search
 ├── MCP tool call
 ├── Tool response
 └── Final answer
```

Do not store private chain-of-thought.

Store useful execution information such as:

```text
tool name
input
output/status
timestamp
user
```

---

# PHASE 14 — React Frontend

Only build the frontend after the backend works.

Create:

```text
Login
Register
Google Login
Dashboard
Document Upload
Chat
Conversation History
API Tools
```

Chat UI example:

```text
------------------------------------------------
AI API Assistant

You:
Create a customer named Rahul.

AI:
I found POST /customers.
Please provide phone number.

You:
9876543210

AI:
Customer created successfully.
ID: 101.

Tool: create_customer
Status: Success
------------------------------------------------
```

---

# PHASE 15 — Docker

Containerize:

```text
FastAPI
PostgreSQL
Qdrant
Ollama
MCP Server
Fake API
React
```

Use:

```text
docker-compose.yml
```

Goal:

```bash
docker compose up
```

should start the application locally.

---

# PHASE 16 — Testing

Write tests for important backend functionality.

## Authentication

```text
register
login
invalid password
expired JWT
protected endpoint
```

## RAG

```text
document upload
chunking
embedding
vector search
```

## Agent

```text
correct tool selection
missing parameters
normal questions
```

## MCP

```text
create_customer
get_customer
get_orders
```

## Security

```text
unauthorized user
insufficient permissions
dangerous operation confirmation
```

---

# 4. Final Architecture

The final system should look approximately like:

```text
                         React
                           │
                           ▼
                    FastAPI Backend
                           │
             ┌─────────────┼──────────────┐
             │             │              │
          Auth/JWT       RAG Service     Agent
             │             │              │
             │          Qdrant            │
             │                            │
             │                     ┌──────┴──────┐
             │                     │             │
             │                   RAG Tool     MCP Tools
             │                                   │
             │                              MCP Server
             │                                   │
             │                              Fake APIs
             │                                   │
             └──────────── PostgreSQL ───────────┘
```

---

# 5. Features to Add Later

Do NOT build these initially.

After the core project works, consider:

- Streaming AI responses using SSE
- WebSockets
- API rate limiting
- Redis caching
- API request logs
- Retry handling
- MCP resources/prompts
- Multiple API environments
- API versioning
- OpenAPI automatic tool generation
- Evaluation of RAG quality
- Prompt injection protection
- Audit logs
- Docker deployment
- CI/CD
- Cloud deployment

---

# 6. MVP — Minimum Version

If the full project becomes too large, finish this version first:

```text
✓ JWT authentication
✓ PostgreSQL
✓ Fake Customer API
✓ Upload OpenAPI document
✓ Qdrant
✓ RAG search
✓ Ollama
✓ Basic AI agent
✓ 2 MCP tools
✓ Permission checking
✓ React chat
```

This alone is already a strong portfolio project.

---

# 7. Development Rule

Build ONE feature at a time.

After every feature:

```text
Code
 ↓
Run
 ↓
Test
 ↓
Understand
 ↓
Commit to Git
 ↓
Move to next feature
```

Do not copy a huge AI-agent tutorial and try to build everything simultaneously.

The main learning goal is to understand how:

```text
Authentication
       ↓
Backend
       ↓
RAG
       ↓
Vector DB
       ↓
AI Agent
       ↓
MCP
       ↓
Authorization
       ↓
API execution
```

fit together.

---

# 8. Suggested Git Commits

```text
01-initialize-fastapi
02-add-postgresql
03-add-user-auth
04-add-jwt
05-add-google-oauth
06-create-fake-customer-api
07-add-document-upload
08-add-qdrant
09-add-rag-search
10-connect-ollama
11-add-ai-agent
12-add-mcp-server
13-add-mcp-tools
14-add-permissions
15-add-action-confirmation
16-add-chat-history
17-add-react-ui
18-dockerize-project
19-add-tests
20-finalize-readme
```

---

# 9. Most Important Learning Order

Learn/build these in this order:

1. FastAPI
2. PostgreSQL
3. JWT
4. OAuth2
5. REST API integration
6. Embeddings
7. Vector databases
8. RAG
9. LLM
10. AI Agents
11. Tool calling
12. MCP
13. Authorization
14. AI security
15. Docker

You don't need to master everything before starting. Learn each concept when you reach that phase.

---

# 10. Final Portfolio Description

Once completed, describe it as:

> **AI API Assistant — Secure AI Agent for API Discovery and Execution**
>
> Built a backend platform that uses RAG and vector search to understand API documentation and an AI agent with MCP-based tools to interact with APIs. Implemented JWT/OAuth authentication, role/permission-based authorization, action confirmation, PostgreSQL persistence, local LLM inference, and a React chat interface.

