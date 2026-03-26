# Graph-Based Data Modeling and Query System

This project is a context graph system built with an LLM-powered query interface. It ingests disconnected supply chain and business datasets (orders, deliveries, invoices, payments, etc.), unifies them into a graph of connected entities, and provides a chat system to answer questions using natural language.

## Architecture

The system is built as a lightweight, single-page web application.

1. **Frontend**: Plain HTML, CSS, and JS. Chosen to avoid heavy abstractions and keep the demo extremely fast. The UI incorporates dark mode, glassmorphism, and responsive CSS flexbox to create a premium visual experience.
2. **Graph Visualization**: `vis-network` (via CDN) to render the interactive physics-based context graph dynamically based on our backend node/edge feeds.
3. **Backend API**: Python with `FastAPI`. It serves static assets, provides endpoints for graph structural data (`/api/graph`), and handles conversational AI logic (`/api/chat`).
4. **Data Analytics engine**: We simultaneously load data into `NetworkX` (for structured node mappings and relational plotting) and an **in-memory SQLite Database** (for robust querying and analytics). 
5. **LLM Orchestration**: `langchain` and `langchain-google-genai` (utilizing Gemini Free Tier).

## Database Choice

I chose an **In-Memory SQLite Database** combined with an **In-Memory NetworkX Graph**. 
*Why not Neo4j?*
- For a fast prototyping context, spinning up a local Neo4j database natively with Docker or JVM overhead creates deployment friction. 
- A relational structure (SQLite) is actually superior for complex analytical aggregations (e.g., "Which products are associated with the highest number of billing documents?") because LLMs excel at generating standard SQL (Text-to-SQL paradigm).
- By loading Pandas data frames into SQLite, we enable the LangChain agent to see the exact schema via `db.get_table_info()` and accurately write dynamic traversal logic without hallucinating syntax. `NetworkX` effectively serves as the "read-replica" dedicated purely to UI Graph visualization, satisfying both analytics and modeling.

## Graph Modeling Strategy

We model standard transactional artifacts as nodes linked hierarchically.
- **Nodes**: Each entity instance (Customer, Order, Delivery, Invoice). Formatted with a unified ID (e.g. `ORD_102`) and color-coded.
- **Edges**: We parse relational columns (like `order_id` in the `deliveries` table) to build directed edges (`placed_by`, `fulfilled_by`, `billed_in`). This naturally creates a visual chain tracing a single transaction end-to-end.

## LLM Prompting Strategy

We use LangChain's `create_sql_query_chain` which implements an ReAct-style query formulation. Our custom wrapping prompt:
1. Receives the user's natural language question.
2. Receives a live snapshot of the schema (`table_info`).
3. Formulates a SQL query to interact with the SQLite DB.
4. If execution succeeds, the raw data row output is piped back to the LLM to format a conversational answer. If it fails, the agent reports the underlying query attempt for transparency.

## Guardrails

To prevent the system from answering non-domain questions (general knowledge, creative writing, or off-topic prompts), guardrails are enforced on two levels:
1. **Heuristic Pre-Check**: Before hitting the LLM API, a lightweight Python function checks the input string against banned phrases and intent markers (e.g. "joke", "poem", "write a"). If detected, the request is instantly rejected, saving latency and cost.
2. **System Prompt Restriction**: The core prompt contains strict instructions: 
   > "IF the user asks about ANYTHING NOT related to the dataset... you MUST ONLY reply: 'This system is designed to answer questions related to the provided dataset only.'"

## Running Locally

1. Setup environment variables: `export GEMINI_API_KEY="your-api-key"`
2. Install Python dependencies:
   ```bash
   pip install fastapi uvicorn pandas networkx langchain langchain-google-genai langchain-community python-dotenv
   ```
3. Load datasets into the `data/` folder. Ensure the JSONL filenames correspond to entities (e.g. `orders.jsonl`, `deliveries.jsonl`).
4. Start the backend:
   ```bash
   python backend/main.py
   ```
5. Navigate to `http://localhost:8000` to interact with the visual canvas and query system.
