from .tools import fetch_emails, generate_todo

def get_todolist(n):
    emails = fetch_emails.func(n=n)
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