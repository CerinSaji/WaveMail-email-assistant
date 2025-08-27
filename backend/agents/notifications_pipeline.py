from .tools import fetch_email_by_query, classify_email, summarize_email, sort_emails

def get_notifications():
    emails = fetch_email_by_query.func("is:important newer_than:1d")  # Get notification for important emails in the last 1 day
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

def sort():
    print("Sorting emails...")
    return sort_emails.func()