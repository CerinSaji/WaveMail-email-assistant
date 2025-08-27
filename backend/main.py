from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.pipelines import get_notifications, sort, get_todolist
from agents.chat_agent import run_chat

app = FastAPI(title="WaveMail - Backend API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Notifications / Todo ----------------
@app.get("/notifications")
def notifications():
    return {"notifications": get_notifications()}

@app.get("/todolist")
def todo():
    return {"todolist": get_todolist()}

# ---------------- Chat Agent ----------------
@app.get("/chat")
def chat(query: str):
    response = run_chat(query)
    return {"response": response}

# ---------------- Automated Sorting ----------------
@app.get("/automatedsort")
def automatedsort():
    response = sort()
    return {"response": response}
