"""Test creating a calendar event."""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from src.mcp_aruba.calendar_client import ArubaCalendarClient

# Load environment variables
load_dotenv()

def create_test_event():
    """Create a test event for tomorrow."""
    print("Creating test calendar event...")
    print("=" * 60)
    
    # Get credentials from environment
    url = os.getenv("CALDAV_URL")
    username = os.getenv("CALDAV_USERNAME")
    password = os.getenv("CALDAV_PASSWORD")
    
    if not username or not password:
        print("❌ Error: CalDAV credentials not configured")
        return
    
    print(f"URL: {url}")
    print(f"Username: {username}")
    print()
    
    try:
        with ArubaCalendarClient(url, username, password) as client:
            if not client.calendar:
                print("❌ No calendar available. Please enable CalDAV sync in Aruba Webmail first.")
                print("\nTo enable:")
                print("1. Go to https://webmail.aruba.it")
                print("2. Calendar → 'Sincronizza calendario'")
                print("3. Choose CalDAV and select calendars to sync")
                return
            
            # Event details
            tomorrow = datetime.now() + timedelta(days=1)
            start = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)
            end = tomorrow.replace(hour=15, minute=30, second=0, microsecond=0)
            
            print("Creating event:")
            print(f"  Title: Domani non faccio una sega")
            print(f"  Start: {start.strftime('%d/%m/%Y %H:%M')}")
            print(f"  End: {end.strftime('%d/%m/%Y %H:%M')}")
            print(f"  Attendees: christopher.caponi@emotion-team.com")
            print()
            
            result = client.create_event(
                summary="Domani non faccio una sega",
                start=start,
                end=end,
                description="Evento di test creato tramite MCP Aruba Calendar",
                location="Ufficio",
                attendees=["christopher.caponi@emotion-team.com"]
            )
            
            if result.get('success'):
                print("✅ Event created successfully!")
                print(f"   UID: {result['uid']}")
                print(f"   Summary: {result['summary']}")
                print(f"   Start: {result['start']}")
                print(f"   End: {result['end']}")
                print()
                print("Christopher Caponi dovrebbe ricevere un invito via email!")
            else:
                print(f"❌ Failed to create event: {result}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    create_test_event()
