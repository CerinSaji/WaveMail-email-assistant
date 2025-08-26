from fastapi import FastAPI
from agents.notifications_pipeline import get_notifications
from agents.todo_pipeline import get_todolist
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
def notifications(n: int = 4):
    return {"notifications": get_notifications(n)}

@app.get("/todolist")
def todo(n: int = 2):
    return {"todolist": get_todolist(n)}
