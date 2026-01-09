#!/usr/bin/env python3

import os
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email credentials
IMAP_HOST = os.getenv("IMAP_HOST", "imaps.aruba.it")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
IMAP_USERNAME = os.getenv("IMAP_USERNAME")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD")

if not IMAP_USERNAME or not IMAP_PASSWORD:
    print("Credenziali IMAP non configurate.")
    exit(1)

# Connect to IMAP
mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
mail.login(IMAP_USERNAME, IMAP_PASSWORD)

# Select Sent folder
mail.select('INBOX.Sent')

# Search for all emails, get the latest
status, messages = mail.search(None, 'ALL')
if status != 'OK':
    print("Errore nella ricerca.")
    exit(1)

email_ids = messages[0].split()
if not email_ids:
    print("Nessuna email trovata nella Sent.")
    exit(1)

# Get the latest email
latest_id = email_ids[-1]
status, msg_data = mail.fetch(latest_id, '(RFC822)')
if status != 'OK':
    print("Errore nel recupero dell'email.")
    exit(1)

# Parse email
raw_email = msg_data[0][1]
email_message = email.message_from_bytes(raw_email)

# Extract details
subject = decode_header(email_message['Subject'])[0][0]
if isinstance(subject, bytes):
    subject = subject.decode()

to = email_message['To']
cc = email_message.get('Cc', '')

print(f"Oggetto: {subject}")
print(f"A: {to}")
if cc:
    print(f"CC: {cc}")
print(f"Data: {email_message['Date']}")

# Get body
if email_message.is_multipart():
    for part in email_message.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True).decode()
            print(f"\nCorpo:\n{body}")
            break
else:
    body = email_message.get_payload(decode=True).decode()
    print(f"\nCorpo:\n{body}")

mail.logout()