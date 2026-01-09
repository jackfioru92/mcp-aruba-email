#!/usr/bin/env python3

import os
import smtplib
import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import json
from pathlib import Path

# Load environment variables
load_dotenv()

# Email credentials
IMAP_USERNAME = os.getenv("IMAP_USERNAME")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD")
SMTP_HOST = os.getenv("SMTP_HOST", "smtps.aruba.it")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))

# Signature
SIGNATURE_FILE = Path.home() / ".config" / "mcp_aruba" / "signature.json"
signature = ""
if SIGNATURE_FILE.exists():
    with open(SIGNATURE_FILE, 'r', encoding='utf-8') as f:
        signatures = json.load(f)
        signature = signatures.get("default", "")

# Email details
to = "james@ruihuaevcharger.com"
cc = "e.mancinelli@emotion-team.com"
subject = "Charging Stations – POS Test Results and Open Points"
body = """Hi James,

thank you for sending us the charging stations.

As mentioned earlier on WeChat, we have tested the units and we can confirm that charging sessions started via POS are working correctly.

However, during our analysis we identified two important points that we would like to clarify with you:

Stopping a charge without authentication
At the moment, a charging session that has been started via POS can be stopped without any authentication.
This means that anyone can stop an ongoing charge, even if they are not the user who started it.
Could you please let us know if there is a way to require authentication (POS, RFID, or other method) also for stopping the charge?

Price management
We would like to understand how pricing is managed:

If an operator wants to change the price remotely, how can this be done?

Is it possible to add a parking fee (for example, an extra cost based on time after charging is completed)?

We look forward to your feedback and technical details on these points.

Best regards,"""

from_name = "Giacomo Fiorucci"

# Prepare body with signature
final_body = body
is_html = False
if signature:
    if signature.strip().startswith('<'):
        is_html = True
        final_body = f"<div>{body.replace(chr(10), '<br>')}</div>{signature}"
    else:
        final_body = f"{body}\n\n{signature}"

# Create message
msg = MIMEMultipart('alternative')
msg['Subject'] = subject
msg['From'] = f"{from_name} <{IMAP_USERNAME}>"
msg['To'] = to
msg['Cc'] = cc
msg['Date'] = email.utils.formatdate(localtime=True)

# Add parts
if is_html:
    from email.mime.text import MIMEText
    plain_part = MIMEText(body, 'plain', 'utf-8')
    html_part = MIMEText(final_body, 'html', 'utf-8')
    msg.attach(plain_part)
    msg.attach(html_part)
else:
    msg.attach(MIMEText(final_body, 'plain', 'utf-8'))

# Send
with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
    smtp.login(IMAP_USERNAME, IMAP_PASSWORD)
    recipients = [to, cc]
    smtp.send_message(msg, to_addrs=recipients)

print("Email sent successfully!")