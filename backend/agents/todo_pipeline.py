from .tools import fetch_emails, generate_todo

def get_todolist():
    emails = fetch_emails.func(n=5)  # Get todo for all emails (set it to 5 for now)
    todolist = []

    for email in emails:
        todo = generate_todo.func(email)
        if todo == []:
            continue
        todolist.append({
            "from": email["from"],
            "subject": email["subject"],
            "todo": todo,
            "date": email["date"]
        })
    return todolist