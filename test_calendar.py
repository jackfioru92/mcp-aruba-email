"""Test script for Aruba CalDAV calendar functionality."""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from src.mcp_aruba.calendar_client import ArubaCalendarClient

# Load environment variables
load_dotenv()

def test_calendar():
    """Test calendar operations."""
    print("Testing Aruba CalDAV Calendar Connection...")
    print("=" * 60)
    
    # Get credentials from environment
    url = os.getenv("CALDAV_URL", "https://syncdav.aruba.it/calendars/user@domain.com/")
    username = os.getenv("CALDAV_USERNAME", os.getenv("IMAP_USERNAME", ""))
    password = os.getenv("CALDAV_PASSWORD", os.getenv("IMAP_PASSWORD", ""))
    
    if not username or not password:
        print("❌ Error: CalDAV credentials not configured")
        print("Please set CALDAV_USERNAME and CALDAV_PASSWORD in .env file")
        return
    
    print(f"URL: {url}")
    print(f"Username: {username}")
    print()
    
    try:
        # Test connection
        print("1. Testing connection...")
        with ArubaCalendarClient(url, username, password) as client:
            print(f"✅ Connected successfully!")
            print(f"   Principal: {client.principal}")
            
            # Get calendars
            calendars = client.principal.calendars()
            print(f"   Found {len(calendars)} calendars")
            
            if not calendars:
                print("\n⚠️  No calendars found. You may need to:")
                print("   1. Log into Aruba Webmail (https://webmail.aruba.it)")
                print("   2. Go to Calendar section")
                print("   3. Click 'Sincronizza calendario' (Sync calendar)")
                print("   4. Follow the wizard and select CalDAV option")
                print("   5. Select which calendars to sync")
                return
            
            print(f"✅ Connected successfully to calendar: {client.calendar.name if client.calendar else 'Unknown'}")
            print()
            
            # Test listing events
            print("2. Listing upcoming events (next 30 days)...")
            start_date = datetime.now()
            end_date = datetime.now() + timedelta(days=30)
            
            events = client.list_events(start_date=start_date, end_date=end_date, limit=10)
            print(f"Found {len(events)} upcoming events:")
            
            for i, event in enumerate(events[:5], 1):  # Show first 5
                print(f"\n   Event {i}:")
                print(f"   - UID: {event.get('uid', 'N/A')}")
                print(f"   - Summary: {event.get('summary', 'N/A')}")
                print(f"   - Start: {event.get('start', 'N/A')}")
                print(f"   - End: {event.get('end', 'N/A')}")
                print(f"   - Location: {event.get('location', 'N/A')}")
                
                attendees = event.get('attendees', [])
                if attendees:
                    print(f"   - Attendees: {len(attendees)}")
                    for att in attendees[:3]:  # Show first 3
                        print(f"     • {att.get('email', 'N/A')} ({att.get('status', 'UNKNOWN')})")
            
            print()
            
            # Test creating an event
            print("3. Testing event creation...")
            test_summary = "Test Event - MCP Aruba Calendar"
            test_start = datetime.now() + timedelta(days=7)
            test_end = test_start + timedelta(hours=1)
            
            try:
                result = client.create_event(
                    summary=test_summary,
                    start=test_start,
                    end=test_end,
                    description="This is a test event created by MCP Aruba Calendar Client",
                    location="Virtual Meeting"
                )
                
                if result.get('success'):
                    print(f"✅ Event created successfully!")
                    print(f"   - UID: {result.get('uid')}")
                    print(f"   - Summary: {result.get('summary')}")
                    print(f"   - Start: {result.get('start')}")
                    print()
                    
                    # Try to delete the test event
                    print("4. Cleaning up test event...")
                    delete_result = client.delete_event(result.get('uid'))
                    if delete_result.get('success'):
                        print("✅ Test event deleted successfully")
                    else:
                        print(f"⚠️  Could not delete test event: {delete_result.get('error')}")
                else:
                    print(f"❌ Failed to create event: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"⚠️  Event creation test skipped: {e}")
            
            print()
            print("=" * 60)
            print("✅ Calendar tests completed successfully!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Common issues:")
        print("1. Check that CalDAV URL is correct (try: https://caldav.aruba.it)")
        print("2. Verify credentials are correct")
        print("3. Ensure calendar access is enabled in your Aruba account")
        print("4. Check firewall/network settings")


if __name__ == "__main__":
    test_calendar()
