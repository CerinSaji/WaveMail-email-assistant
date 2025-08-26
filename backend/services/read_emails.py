import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define the SCOPES. If modifying these, delete the file token.json.
# modification access
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

import base64
# You might need to install this library first: pip install beautifulsoup4
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

def main():
    """
    Lists the user's Gmail labels and fetches emails.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This is the line that uses your credentials.json file
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)

        # results = service.users().messages().list(userId='me', maxResults=5).execute() # Get the 5 most recent messages
        results = service.users().messages().list(userId='me').execute()
        messages = results.get('messages', [])
        #STOP HERE
        if not messages:
            print('No messages found.')
            return

        print('Fetching emails:\n')
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            
            # Get the headers
            headers = msg['payload']['headers']
            subject = next((d['value'] for d in headers if d['name'] == 'Subject'), 'No Subject')
            sender = next((d['value'] for d in headers if d['name'] == 'From'), 'Unknown Sender')
            body = get_body_from_google_api_payload(msg['payload'])

            print(f"---------------------------------")
            print(f"From: {sender}")
            print(f"Subject: {subject}")
            print(f"\nBody:\n{body[:500]}...") # Print first 500 chars of the body
            print(f"---------------------------------\n")

    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()