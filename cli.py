#!/usr/bin/env python3
"""Quick CLI wrapper for MCP Aruba tools."""

import sys
from src.mcp_aruba.email_client import ArubaEmailClient
from src.mcp_aruba.calendar_client import ArubaCalendarClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()


def list_emails(limit=5):
    """List recent emails."""
    with ArubaEmailClient(
        host=os.getenv('IMAP_HOST'),
        port=int(os.getenv('IMAP_PORT')),
        username=os.getenv('IMAP_USERNAME'),
        password=os.getenv('IMAP_PASSWORD'),
        smtp_host=os.getenv('SMTP_HOST'),
        smtp_port=int(os.getenv('SMTP_PORT'))
    ) as client:
        emails = client.list_emails(limit=limit)
        print(f'\n📧 Ultime {len(emails)} email:\n')
        print('=' * 80)
        for i, email in enumerate(emails, 1):
            print(f'\n{i}. ID: {email["id"]}')
            print(f'   Da: {email["from"]}')
            print(f'   Oggetto: {email["subject"]}')
            print(f'   Data: {email["date"]}')
            print(f'   Anteprima: {email["body"][:100]}...')
            print('-' * 80)


def list_calendar(days=7):
    """List upcoming calendar events."""
    with ArubaCalendarClient(
        url=os.getenv('CALDAV_URL'),
        username=os.getenv('CALDAV_USERNAME'),
        password=os.getenv('CALDAV_PASSWORD')
    ) as client:
        if not client.calendar:
            print("⚠️  No calendar available. Enable CalDAV sync in Aruba Webmail.")
            return
        
        start = datetime.now()
        end = start + timedelta(days=days)
        events = client.list_events(start_date=start, end_date=end)
        
        print(f'\n📅 Eventi prossimi {days} giorni:\n')
        print('=' * 80)
        for i, event in enumerate(events, 1):
            print(f'\n{i}. {event["summary"]}')
            print(f'   Inizio: {event["start"]}')
            print(f'   Fine: {event["end"]}')
            if event.get('location'):
                print(f'   Luogo: {event["location"]}')
            print('-' * 80)


def main():
    """Main CLI."""
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python cli.py emails [limit]       - Mostra ultime email")
        print("  python cli.py calendar [days]      - Mostra eventi calendario")
        print("\nEsempi:")
        print("  python cli.py emails 10")
        print("  python cli.py calendar 14")
        return
    
    command = sys.argv[1].lower()
    
    if command == "emails":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        list_emails(limit)
    
    elif command == "calendar":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        list_calendar(days)
    
    else:
        print(f"❌ Comando sconosciuto: {command}")
        print("Usa: emails o calendar")


if __name__ == "__main__":
    main()
