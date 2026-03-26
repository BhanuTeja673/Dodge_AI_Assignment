from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from graph_builder import data_manager
from llm_agent import QuerySystem

# Initialize
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")

if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Load data into RAM
data_manager.load_data()
# Init Query System
query_system = QuerySystem(data_manager.db_conn)

class QueryRequest(BaseModel):
    query: str

@app.post("/api/chat")
async def chat_endpoint(request: QueryRequest):
    # Pass natural language query to LangChain + Google Gemini agent
    response = query_system.process_query(request.query)
    return {"reply": response}

@app.get("/api/graph")
async def get_graph():
    # Serve NetworkX computed nodes and edges to Vis-Network UI
    graph_data = data_manager.get_graph_data()
    return graph_data

@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
