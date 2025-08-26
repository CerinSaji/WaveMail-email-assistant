from langchain.tools import tool
from services.gmail_service import get_gmail_service
from .llm import llm
from langchain_core.prompts import ChatPromptTemplate
import base64
from bs4 import BeautifulSoup 


def get_message_body(msg):
    """
    Decodes an email message and returns the body content.
    Prioritizes 'text/plain', falls back to 'text/html' and strips its tags.
    """
    # If the message is multipart, recursively search for the parts
    if msg.is_multipart():
        # A multipart message will have a list of parts
        for part in msg.get_payload():
            # Recursively call this function for each part
            body = get_message_body(part)
            if body: # If a body was found in a subpart, return it
                return body
        return "" # If no body found in any part
    
    # If the message is not multipart, it has a single payload
    content_type = msg.get_content_type()
    payload = msg.get_payload(decode=True) # decode=True handles base64
    
    if payload is None:
        return ""
        
    # Check the content type
    if content_type == 'text/plain':
        try:
            return payload.decode('utf-8')
        except UnicodeDecodeError:
            return payload.decode('latin-1') # Fallback encoding

    elif content_type == 'text/html':
        # If we only have HTML, use BeautifulSoup to strip tags
        soup = BeautifulSoup(payload, "html.parser")
        # Find all image tags and remove them
        for img_tag in soup.find_all('img'):
            img_tag.decompose()
        # Return the text content of the cleaned HTML
        return soup.get_text(separator='\n', strip=True)
        
    # If it's another content type (like an attachment), ignore it
    return ""

# IMPORTANT NOTE:
# The official Google API library might not return a standard email.message.Message object.
# The following function is tailored for the raw dictionary structure from the API.

def get_body_from_google_api_payload(payload):
    """
    Parses the Google API 'payload' dictionary to find the email body.
    Prioritizes 'text/plain', falls back to 'text/html' and strips its tags.
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

# --- Fetch Emails Tool ---
@tool("fetch_emails")
def fetch_emails(n: int = 5) -> list:
    """Fetch last n emails with subject, sender, date, and snippet."""
    service = get_gmail_service()
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

        emails.append({"id": msg["id"], "subject": subject, "from": sender, "date": date, "snippet": body})
    return emails


# --- Classify Email Tool ---

IMPORTANT_KEYWORDS = ["urgent", "asap", "deadline", "payment", "immediately"]

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
        ("system", "You are an assistant that classifies emails as 'important' or 'not important'. News / updates / newsletters / marketting emails are not important."),
        ("user", "Email: {email}\n\nAnswer with only one word: Important or Not Important.")
    ])
    chain = prompt | llm
    response = chain.invoke({"email": email_text})
    decision = response.content.strip().lower()
    return "important" in decision

@tool("classify_email", return_direct=False)
def classify_email(email: dict) -> str:
    """
    Classify if an email is important or not.
    Input: dict with subject, snippet, from
    Output: "important" or "not important"
    """
    subject = email.get("subject", "")
    snippet = email.get("snippet", "")
    sender = email.get("from", "")

    if rule_based_check(subject, snippet, sender):
        return "important"
    elif llm_fallback_check(f"Subject: {subject}\nContent: {snippet}"):
        print(f"LLM-based: Classified as important. - {subject}")
        return "important"
    else:
        return "not important"

def llm_summarize(email_text: str) -> str:
    """Use Groq LLM to summarize email into 1-2 sentences."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant that summarizes emails in a single concise phrase."),
        ("user", "Summarize this email. Do not mention names or additional context:\n\n{email}")
    ])
    chain = prompt | llm
    response = chain.invoke({"email": email_text})
    return response.content.strip()

@tool("summarize_email", return_direct=False)
def summarize_email(email: dict) -> str:
    """
    Summarize the given email (subject + snippet).
    Input: dict with subject, snippet
    Output: short summary string
    """
    subject = email.get("subject", "")
    snippet = email.get("snippet", "")
    text = f"Subject: {subject}\nContent: {snippet}"
    return llm_summarize(text)
