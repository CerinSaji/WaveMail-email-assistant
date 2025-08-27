from langchain.tools import tool
from services.gmail_service import get_gmail_service
from .llm import llm
from langchain_core.prompts import ChatPromptTemplate
import base64
from bs4 import BeautifulSoup 
from typing import List, Dict
import re

# The official Google API library might not return a standard email.message.Message object.
# The following function is tailored for the raw dictionary structure from the API.

#----------FETCH EMAILS AND PARSE BODY------------------------------------------------------

def get_body_from_google_api_payload(payload):
    """
    Parses the Google API 'payload' dictionary to find the email body.
    Prioritizes 'text/plain', falls back to 'text/html' and strips its tags.
    This is to avoid getting html content with images and other unwanted elements.
    """
    text_plain = None
    text_html = None

    def find_parts(parts):
        nonlocal text_plain, text_html
        for part in parts:
            if part.get('mimeType') == 'text/plain' and 'data' in part['body']:
                text_plain = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                # If we find plain text, we can often stop, as it's preferred
                return
            elif part.get('mimeType') == 'text/html' and 'data' in part['body']:
                text_html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            
            # Recursive call for nested parts
            if 'parts' in part:
                find_parts(part['parts'])

    # Start the search
    if 'parts' in payload:
        find_parts(payload['parts'])
    elif 'data' in payload['body']:
        if payload.get('mimeType') == 'text/plain':
            text_plain = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        elif payload.get('mimeType') == 'text/html':
            text_html = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

    # --- Prioritize and Clean ---
    if text_plain:
        return text_plain
    elif text_html:
        # We only have HTML, so we need to clean it
        soup = BeautifulSoup(text_html, "html.parser")
        # You can remove specific tags like this:
        for img in soup.find_all('img'):
            img.decompose() # Remove the <img> tag completely
        for script in soup.find_all('script'):
            script.decompose() # Remove <script> tags
        for style in soup.find_all('style'):
            style.decompose() # Remove <style> tags
            
        # Get the text, which is now free of images and other unwanted tags
        return soup.get_text(separator='\n', strip=True)
        
    return "No readable body found."

# --- Fetch Emails Tool ------
@tool("fetch_emails")
def fetch_emails(n: int = -1) -> list:
    """
    Fetch the last n emails with subject, sender, date, and body.
    - If n > 0, only fetch the last n emails.
    - If n <= 0 or omitted, fetch all emails.
    """
    service = get_gmail_service()

    n = int(n) #chat api may pass action input as string

    if n <= 0: # Fetch all emails (ie n is not mentioned)
        results = service.users().messages().list(userId="me").execute()
    else:
        results = service.users().messages().list(userId="me", maxResults=n).execute()
    messages = results.get("messages", [])

    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = msg_data["payload"]["headers"]

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "(Unknown Sender)")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "(Unknown Date)")
        #snippet = msg_data.get("snippet", "") -- instead of snippet, we'll get the entire body
        body = get_body_from_google_api_payload(msg_data['payload'])
        if len(body) > 500:
            body = body[:1000] + "..."  #Truncate long bodies for efficiency (usually spam bodies are unusually long)

        emails.append({"id": msg["id"], "subject": subject, "from": sender, "date": date, "snippet": body})
    return emails

@tool("fetch_emails_by_sender")
def fetch_emails_by_sender(user_query: str) -> list:
    """Fetches emails from a specific sender mentioned in the user query, which can then be used by other tools.
    """
    # 1: Extract sender from the user query using LLM ---
    prompt = f"""
    You are an assistant that extracts the sender from a user query about emails.
    Return only the sender's name or email, nothing else.

    User query: "{user_query}"
    """
    response = llm.invoke(prompt)
    sender_extracted = response.content.strip()

    #2: check if sender is found in any email
    service = get_gmail_service()

    search_query = f'from:"{sender_extracted}"'
    
    print(f"Searching for emails from '{sender_extracted}'...")

    results = service.users().messages().list(
        userId='me',
        q=search_query
    ).execute()
    
    messages = results.get('messages', [])

    if not messages:
        print(f"No emails found from '{sender_extracted}'.")
        return []

    #3: Extract no of responses required from the user query using LLM ---
    prompt = f"""
    You are an assistant that extracts the number of emails to fetch from a user query about emails.
    If 'latest' or 'recent' mentioned, return 1.
    Return only the integer number, nothing else.

    User query: "{user_query}"
    """
    response = llm.invoke(prompt)
    number_extracted = response.content.strip()

    n = int(number_extracted) if number_extracted.isdigit() else 1

    #4: Fetch emails from the sender
    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = msg_data["payload"]["headers"]

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "(Unknown Sender)")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "(Unknown Date)")
        #snippet = msg_data.get("snippet", "") -- instead of snippet, we'll get the entire body
        body = get_body_from_google_api_payload(msg_data['payload'])
        if len(body) > 500:
            body = body[:1000] + "..."  #Truncate long bodies for efficiency (usually spam bodies are unusually long)

        emails.append({"id": msg["id"], "subject": subject, "from": sender, "date": date, "snippet": body})

        if len(emails) >= n:
            break
    return emails

#-------------Custom email fetch tool based on user query---------
@tool("fetch_email_by_query")
def fetch_email_by_query(user_query: str) -> list:
    """Fetches emails in a custom manner based on a user query, which can then be used by other tools. """

    # 1: Extract search query from the user query using LLM ---
    prompt = f"""
    You are an assistant that extracts the search query from a user query about emails.
    Return only the search query, nothing else.
    refer to the Gmail search operators:
    Unread email: "is:unread"
    Emails with attachments: "has:attachment"
    Emails in Spam folder: "in:spam"
    Emails in Trash folder: "in:trash"
    Emails with high importance: "is:important"
    Emails received after a specific date: "after:YYYY/MM/DD"
    Emails received before a specific date: "before:YYYY/MM/DD"
    Emails in the last 24 hours: "newer_than:1d"
    Emails from a specific sender: "from:name or email"
    Emails to a specific recipient: "to:name or email"
    Emails with specific words in the subject: "subject:your words"
    Emails with specific words in the body: "your words"
    combination queries example: "is:unread from:jane.doe@example.com"

    If no search query can be extracted, return "None".

    User query: "{user_query}"
    """
    response = llm.invoke(prompt)
    search_query_extracted = response.content.strip()

    if search_query_extracted.lower() == "None":
        print("No valid custom search result obtained.")
        return []

    #2: check if any email matches the search query
    service = get_gmail_service()

    print(f"Searching for emails matching '{search_query_extracted}'...")

    results = service.users().messages().list(
        userId='me',
        q=search_query_extracted
    ).execute()
    
    messages = results.get('messages', [])

    if not messages:
        print(f"No emails found matching '{search_query_extracted}'.")
        return []
    
    #4: Fetch emails from the search query
    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = msg_data["payload"]["headers"]

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "(Unknown Sender)")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "(Unknown Date)")
        #snippet = msg_data.get("snippet", "") -- instead of snippet, we'll get the entire body
        body = get_body_from_google_api_payload(msg_data['payload'])
        if len(body) > 500:
            body = body[:1000] + "..."  #Truncate long bodies for efficiency (usually spam bodies are unusually long)

        emails.append({"id": msg["id"], "subject": subject, "from": sender, "date": date, "snippet": body})

    return emails

    
    
# -------------------------------------------------------------------------------------------
# --- Classify Email Tool -------------------------------------------------------------------

IMPORTANT_KEYWORDS = ["urgent", "asap", "deadline", "immediately", "launch", "quarterly", "meeting", "project", "update", "report", "invoice", "payment", "schedule", "appointment", "reminder", "action required", "follow up", "important", "priority", "quarter"]

def rule_based_check(subject: str, snippet: str, sender: str) -> bool:
    """Simple keyword and sender-based rules for importance."""
    text = f"{subject.lower()} {snippet.lower()}"
    if any(kw in text for kw in IMPORTANT_KEYWORDS):
        print(f"Rule-based: Found important keyword. - {subject}")
        return True
    if "boss@" in sender.lower() or "teamlead@" in sender.lower():
        return True
    return False

def llm_fallback_check(email_text: str) -> bool:
    """Use Groq LLM to classify importance if rule-based is inconclusive."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant that classifies emails as 'important' or 'not important'. Emails from work, company, HR, such as event updates, results, etc. are important. News  / newsletters / marketting emails are not important."),
        ("user", "Email: {email}\n\nAnswer with only one word: reply Yes if important, or reply No if Not Important.")
    ])
    chain = prompt | llm
    response = chain.invoke({"email": email_text})
    decision = response.content.strip().lower()
    if decision == "yes":
        print("LLM-based: Classified as important.\n")
        return True
    print("LLM-based: Classified as not important.\n")
    return False

@tool("classify_email", return_direct=False)
def classify_email(email: dict) -> str:
    """
    Classify if an email is important or not.
    Input: dict with subject, snippet, from
    Output: "important" or "not important"
    Receives an email dict from one of the fetch emails tools.
    """
    subject = email.get("subject", "")
    snippet = email.get("snippet", "")
    sender = email.get("from", "")

    if rule_based_check(subject, snippet, sender):
        return "important"
    elif llm_fallback_check(f"Subject: {subject}\nContent: {snippet}"):
        return "important"
    else:
        return f"not important - {subject}"
    
# -------------------------------------------------------------------------------------------
# --- Summarize Email Tool ------------------------------------------------------------------


@tool("summarize_email", return_direct=False)
def summarize_email(email: dict) -> str:
    """
    Summarize the given email (subject + snippet).
    Receives an email dict from one of the fetch emails tools.
    Output: short summary string
    """
    subject = email.get("subject", "")
    snippet = email.get("snippet", "")
    text = f"Subject: {subject}\nContent: {snippet}"

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant that summarizes emails in a single concise phrase."),
        ("user", "Summarize this email. Do not mention names or additional context:\n\n{email}")
    ])
    chain = prompt | llm
    response = chain.invoke({"email": text})
    return response.content.strip()

# -------------------------------------------------------------------------------------------
# --- Generate Todo List Tool --------------------------------------------------------------

def is_spam(email: Dict) -> bool:
    """
    Simple rule-based check to filter out spam emails.
    """
    subject = email.get("subject", "").lower()
    body = email.get("snippet", "").lower()
    spam_keywords = ["unsubscribe", "newsletter", "promo", "sale", "advertisement"]

    # Combine subject and body, lowercase everything
    text = (subject + " " + body).lower()

    # Remove punctuation for safer matching
    text = re.sub(r"[^\w\s]", " ", text)

    if any(keyword in text for keyword in spam_keywords):
        print(f"Filtered out as spam: {subject}")
        return True
    return False

@tool("generate_todo", return_direct=False)
def generate_todo(email: dict) -> list:
    """
    Generate a todo list from the given email (subject + snippet).
    Receives an email dict from one of the fetch emails tools.
    Output: list of todo items
    """
    subject = email.get("subject", "")
    body = email.get("snippet", "")
    text = f"Subject: {subject}\nContent: {body}"
    sender = email.get("from", "")

    if is_spam(email):
        return []
    print("Not spam!")

    if rule_based_check(subject, body, sender):
        print("important")
    elif llm_fallback_check(f"Subject: {subject}\nContent: {body}"):
        print("important")
    else:
        print("important")
        return []

    prompt = f"""
    Extract all actionable tasks from the following email ONLY IF IT CONTAINS ANY. IF it's a general informational email or a news-based email, return EMPTY STRING. 
    If no tasks, return an empty string and NO OTHER CONTEXT.
    if there are tasks, Return as a list of concise task statements. Start the list with the subject line as context.
    Email:
    {text}
    """
    response = llm.invoke(prompt)

    if response.content.strip().lower() in ["", "none", "no tasks", "no task", "no action", "empty string"]:
        return []

    return response.content.strip().split("\n")

# -------------------------------------------------------------------------------------------
# --- Sort Emails Tool ----------------------------------------------------------------------

@tool("sort_emails", return_direct=False)
def sort_emails() -> str:
    """
    Sort emails into trash / spam / as identified.
    """
    # Fetch all unread emails
    unread_emails = fetch_email_by_query.func("is:unread")

    # Sort emails into categories
    for email in unread_emails:
        subject = email.get("subject", "")
        snippet = email.get("snippet", "")
        message_id = email.get("id", "")
        text = f"Subject: {subject}\nContent: {snippet}"

        if classify_email.func(email) == "important":
            category = "inbox"
            print(f"Classified as important (inbox) - {subject}")
        else:
            # ask LLM
            prompt = f"""
            You are an assistant that classifies emails into categories - 'trash', 'spam', 'CATEGORY_PROMOTIONS', 'CATEGORY_SOCIAL', 'CATEGORY_UPDATES', 'CATEGORY_FORUMS', 
            and if nothing applies, 'inbox'. News come under updates. General informational emails come under forums.
            Choose an apt classification for this email: "{text}"
            Reply with only one word and no other context - trash, spam, CATEGORY_PROMOTIONS, CATEGORY_SOCIAL, CATEGORY_UPDATES, CATEGORY_FORUMS, inbox.
            """
            response = llm.invoke(prompt)
            category = response.content.strip()

            print(f"Classified as {category} - {subject}")
        

        # Move email to the appropriate category
        service = get_gmail_service()
        if category == "spam":
            service.users().messages().spam(userId='me', id=message_id).execute()
            print(f"Message with subject {subject} successfully reported as Spam.")
        elif category == "trash":
            service.users().messages().trash(userId='me', id=message_id).execute()
            print(f"Message with subject {subject} successfully moved to Trash.")
        else: #categories
            categories = ['CATEGORY_PROMOTIONS', 'CATEGORY_SOCIAL', 'CATEGORY_UPDATES', 'CATEGORY_FORUMS']
            if category in categories:
                service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'addLabelIds': [category], 'removeLabelIds': ['INBOX']}
                ).execute()
                print(f"Message with subject {subject} successfully moved to {category}.")
            else:
                print(f"Message with subject {subject} left in Inbox.")

    return "Sorting complete!"
