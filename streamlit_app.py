import streamlit as st
import os
import mimetypes
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# ---------------- Gmail Authentication ----------------
def gmail_authenticate():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)

            # Detect headless / cloud environment
            if os.environ.get("STREAMLIT_SERVER_PORT"):
                st.info(
                    "Headless environment detected.\n"
                    "1. Copy the URL below into your browser.\n"
                    "2. Log in with your Gmail account and allow access.\n"
                    "3. Copy the verification code and paste it below."
                )
                creds = flow.run_console()  # Uses console flow in headless mode
            else:
                # Local environment (Mac)
                creds = flow.run_local_server(port=0)  # Opens browser automatically

        # Save token for future use
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

# ---------------- Create Email Message ----------------
def create_message(sender, to, subject, body_text, file):
    msg = EmailMessage()
    msg["To"] = to
    msg["From"] = sender
    msg["Subject"] = subject
    msg.set_content(body_text)

    if file:
        file_data = file.read()
        ctype, encoding = mimetypes.guess_type(file.name)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file.name)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}

# ---------------- Send Email ----------------
def send_message(service, message_body):
    sent = service.users().messages().send(userId="me", body=message_body).execute()
    return sent

# ---------------- Streamlit App ----------------
st.set_page_config(page_title="Gmail OAuth2 Email Sender", layout="centered")
st.title("📧 Gmail OAuth2 Email Sender")

# Authenticate Gmail
service = gmail_authenticate()
profile = service.users().getProfile(userId="me").execute()
sender_email = profile.get("emailAddress", "me")

# User Inputs
recipient = st.text_input("Recipient Email")
subject = st.text_input("Subject")
body = st.text_area("Message")
uploaded_file = st.file_uploader("Upload a file (optional)", type=["pdf", "jpg", "png", "docx", "txt"])

# Send Button
if st.button("Send Email"):
    if not recipient or not subject or not body:
        st.error("⚠️ Please fill all required fields.")
    else:
        try:
            message_body = create_message(sender_email, recipient, subject, body, uploaded_file)
            sent = send_message(service, message_body)
            st.success(f"✅ Email sent successfully! Message ID: {sent.get('id')}")
        except Exception as e:
            st.error(f"❌ Error sending email: {e}")

st.markdown("---")
st.markdown("💡 *This app uses Gmail OAuth2. Your credentials remain local and are never pushed to GitHub.*")
