from .tools import fetch_email_by_query, classify_email, summarize_email, sort_and_move_emails, generate_todo

def get_todolist():
    emails = fetch_email_by_query.func("is:important")  # Get todo for all important emails
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

def get_notifications():
    emails = fetch_email_by_query.func("is:important")  # Get notification for important emails
    notifications = []

    for email in emails:
        importance = classify_email.func(email)
        if importance == "important":
            summary = summarize_email(email)
            notifications.append({
                "from": email["from"],
                "subject": email["subject"],
                "summary": summary,
                "date": email["date"]
            })
    return notifications

def sort():
    print("Sorting emails...")
    return sort_and_move_emails.func()