from fastapi import FastAPI
from agents.notifications_pipeline import get_notifications, sort
from agents.todo_pipeline import get_todolist
from agents.chat_agent import run_chat
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173", "http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/notifications")
def notifications():
    return {"notifications": get_notifications()}

@app.get("/todolist")
def todo():
    return {"todolist": get_todolist()}

@app.get("/chat")
def chat(query: str):
    response = run_chat(query)
    return {"response": response}

@app.get("/automatedsort")
def automatedsort():
    response = sort()
    return {"response": response}