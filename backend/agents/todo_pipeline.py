from .tools import fetch_email_by_query, generate_todo
import jsonify

def get_todolist():
    emails = fetch_email_by_query.func("is:important newer_than:1d")  # Get todo for all important emails
    todolist = []

    for email in emails:
        todo = generate_todo.func(email)
        if todo == []:
            continue
        todolist.append({
            "from": email["from"],
            "subject": email["subject"],
            "todo": " ".join(todo) if isinstance(todo, list) else todo,  # ensure string
            "date": email["date"]
        })
    return todolist