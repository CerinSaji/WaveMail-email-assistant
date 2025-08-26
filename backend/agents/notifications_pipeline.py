from .tools import fetch_emails, classify_email, summarize_email

def get_notifications():
    emails = fetch_emails.func(n=5)  # Get notification for all UNREAD emails (unread not implemented yet, set it to 5 for now)
    notifications = []

    for email in emails:
        importance = classify_email.func(email)
        if importance == "important":
            summary = summarize_email.func(email)
            notifications.append({
                "from": email["from"],
                "subject": email["subject"],
                "summary": summary,
                "date": email["date"]
            })
    return notifications
