from fastapi import FastAPI
from agents.notifications_pipeline import get_notifications

app = FastAPI()

@app.get("/notifications")
def notifications(n: int = 5):
    return {"notifications": get_notifications(n)}
