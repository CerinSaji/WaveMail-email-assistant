from .tools import fetch_emails, classify_email, summarize_email

def get_notifications(n):
    emails = fetch_emails.func(n=n)
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
