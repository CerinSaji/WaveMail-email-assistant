from fastapi import FastAPI
from agents.notifications_pipeline import get_notifications
from agents.todo_pipeline import get_todolist

app = FastAPI()

@app.get("/notifications")
def notifications(n: int = 4):
    return {"notifications": get_notifications(n)}

@app.get("/todolist")
def todo(n: int = 2):
    return {"todolist": get_todolist(n)}
