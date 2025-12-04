#!/usr/bin/env python
"""Quick test script to verify IMAP connection to Aruba."""

import sys
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()

# Test connection
from src.mcp_aruba.email_client import ArubaEmailClient

print("Testing Aruba IMAP connection...")
print(f"Host: {os.getenv('IMAP_HOST')}")
print(f"Username: {os.getenv('IMAP_USERNAME')}")
print()

try:
    with ArubaEmailClient(
        host=os.getenv('IMAP_HOST'),
        port=int(os.getenv('IMAP_PORT')),
        username=os.getenv('IMAP_USERNAME'),
        password=os.getenv('IMAP_PASSWORD')
    ) as client:
        print("✅ Successfully connected to IMAP server!")
        
        # Test listing emails
        print("\nFetching last 3 emails from INBOX...")
        emails = client.list_emails(limit=3)
        
        print(f"Found {len(emails)} emails:")
        for i, email in enumerate(emails, 1):
            print(f"\n{i}. From: {email['from']}")
            print(f"   Subject: {email['subject']}")
            print(f"   Date: {email['date']}")
            print(f"   ID: {email['id']}")
        
        # Test searching for Denisa's emails
        print("\n\nSearching for emails from denisa@c-tic.it...")
        denisa_emails = client.list_emails(sender_filter="denisa@c-tic.it", limit=5)
        
        print(f"Found {len(denisa_emails)} emails from Denisa:")
        for i, email in enumerate(denisa_emails, 1):
            print(f"\n{i}. Subject: {email['subject']}")
            print(f"   Date: {email['date']}")
        
        print("\n✅ All tests passed!")
        sys.exit(0)
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
