"""
Aruba Calendar Client using CalDAV protocol.
"""

import caldav
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from icalendar import Calendar, Event as ICalEvent, vCalAddress, vText
import logging

logger = logging.getLogger(__name__)


class ArubaCalendarClient:
    """Client for interacting with Aruba calendar via CalDAV."""
    
    def __init__(self, url: str, username: str, password: str):
        """
        Initialize the Aruba CalDAV client.
        
        Args:
            url: CalDAV server URL (e.g., https://caldav.aruba.it)
            username: Email address for authentication
            password: Account password
        """
        self.url = url
        self.username = username
        self.password = password
        self.client = None
        self.principal = None
        self.calendar = None
        
    def connect(self):
        """Connect to the CalDAV server and get the default calendar."""
        try:
            self.client = caldav.DAVClient(
                url=self.url,
                username=self.username,
                password=self.password
            )
            self.principal = self.client.principal()
            
            # Get calendars
            calendars = self.principal.calendars()
            
            if not calendars:
                logger.warning("No calendars found. Calendar sync may not be enabled.")
                logger.info("To enable: Log into Aruba Webmail → Calendar → 'Sincronizza calendario' → Choose CalDAV")
                # Don't raise exception, just log warning
                return
            
            # Use the first calendar by default
            self.calendar = calendars[0]
            logger.info(f"Connected to calendar: {self.calendar.name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to CalDAV: {e}")
            raise
    
    def disconnect(self):
        """Close the CalDAV connection."""
        self.client = None
        self.principal = None
        self.calendar = None
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def create_event(
        self,
        summary: str,
        start: datetime,
        end: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None
    ) -> Dict:
        """
        Create a new calendar event.
        
        Args:
            summary: Event title
            start: Start datetime
            end: End datetime
            description: Event description (optional)
            location: Event location (optional)
            attendees: List of attendee email addresses (optional)
        
        Returns:
            Dict with event details including UID
        """
        if not self.calendar:
            raise Exception("Not connected to calendar. Call connect() first.")
        
        # Create iCalendar event
        cal = Calendar()
        cal.add('prodid', '-//MCP Aruba Calendar//EN')
        cal.add('version', '2.0')
        
        event = ICalEvent()
        event.add('summary', summary)
        event.add('dtstart', start)
        event.add('dtend', end)
        event.add('dtstamp', datetime.now())
        
        if description:
            event.add('description', description)
        
        if location:
            event.add('location', location)
        
        # Add attendees
        if attendees:
            organizer = vCalAddress(f'MAILTO:{self.username}')
            organizer.params['cn'] = vText(self.username)
            event.add('organizer', organizer)
            
            for attendee_email in attendees:
                attendee = vCalAddress(f'MAILTO:{attendee_email}')
                attendee.params['cn'] = vText(attendee_email)
                attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
                attendee.params['PARTSTAT'] = vText('NEEDS-ACTION')
                attendee.params['RSVP'] = vText('TRUE')
                event.add('attendee', attendee)
        
        cal.add_component(event)
        
        # Save event to calendar
        try:
            caldav_event = self.calendar.save_event(cal.to_ical().decode('utf-8'))
            
            return {
                "success": True,
                "uid": str(event.get('uid', '')),
                "summary": summary,
                "start": start.isoformat(),
                "end": end.isoformat(),
                "url": caldav_event.url if hasattr(caldav_event, 'url') else None
            }
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            raise
    
    def list_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        List calendar events within a date range.
        
        Args:
            start_date: Start date for filtering (default: today)
            end_date: End date for filtering (default: 30 days from now)
            limit: Maximum number of events to return
        
        Returns:
            List of event dictionaries
        """
        if not self.calendar:
            raise Exception("Not connected to calendar. Call connect() first.")
        
        # Default date range
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = datetime.now() + timedelta(days=30)
        
        try:
            # Search for events in date range
            events = self.calendar.date_search(start=start_date, end=end_date)
            
            result = []
            for caldav_event in events[:limit]:
                try:
                    ical = Calendar.from_ical(caldav_event.data)
                    
                    for component in ical.walk():
                        if component.name == "VEVENT":
                            event_data = {
                                "uid": str(component.get('uid', '')),
                                "summary": str(component.get('summary', '')),
                                "start": component.get('dtstart').dt.isoformat() if component.get('dtstart') else None,
                                "end": component.get('dtend').dt.isoformat() if component.get('dtend') else None,
                                "description": str(component.get('description', '')),
                                "location": str(component.get('location', '')),
                                "status": str(component.get('status', '')),
                                "organizer": str(component.get('organizer', '')),
                            }
                            
                            # Extract attendees
                            attendees = []
                            for attendee in component.get('attendee', []):
                                if isinstance(attendee, list):
                                    for att in attendee:
                                        attendees.append({
                                            "email": str(att).replace('MAILTO:', ''),
                                            "status": att.params.get('PARTSTAT', 'UNKNOWN')
                                        })
                                else:
                                    attendees.append({
                                        "email": str(attendee).replace('MAILTO:', ''),
                                        "status": attendee.params.get('PARTSTAT', 'UNKNOWN')
                                    })
                            
                            event_data["attendees"] = attendees
                            result.append(event_data)
                            
                except Exception as e:
                    logger.warning(f"Failed to parse event: {e}")
                    continue
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to list events: {e}")
            raise
    
    def get_event_by_uid(self, uid: str) -> Optional[object]:
        """
        Get a CalDAV event object by UID.
        
        Args:
            uid: Event UID
        
        Returns:
            CalDAV event object or None if not found
        """
        if not self.calendar:
            raise Exception("Not connected to calendar. Call connect() first.")
        
        try:
            # Search all events and find by UID
            events = self.calendar.events()
            
            for caldav_event in events:
                try:
                    ical = Calendar.from_ical(caldav_event.data)
                    for component in ical.walk():
                        if component.name == "VEVENT":
                            if str(component.get('uid', '')) == uid:
                                return caldav_event
                except Exception as e:
                    logger.warning(f"Failed to parse event: {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get event: {e}")
            raise
    
    def respond_to_event(
        self,
        event_uid: str,
        response: str,
        comment: Optional[str] = None
    ) -> Dict:
        """
        Respond to a calendar event invitation (accept/decline/tentative).
        
        Args:
            event_uid: UID of the event to respond to
            response: Response status ('ACCEPTED', 'DECLINED', 'TENTATIVE')
            comment: Optional comment for the response
        
        Returns:
            Dict with response status
        """
        if not self.calendar:
            raise Exception("Not connected to calendar. Call connect() first.")
        
        if response.upper() not in ['ACCEPTED', 'DECLINED', 'TENTATIVE']:
            raise ValueError("Response must be 'ACCEPTED', 'DECLINED', or 'TENTATIVE'")
        
        try:
            # Get the event
            caldav_event = self.get_event_by_uid(event_uid)
            
            if not caldav_event:
                return {
                    "success": False,
                    "error": f"Event with UID {event_uid} not found"
                }
            
            # Parse the event
            ical = Calendar.from_ical(caldav_event.data)
            
            for component in ical.walk():
                if component.name == "VEVENT":
                    # Update attendee status
                    attendees = component.get('attendee', [])
                    if not isinstance(attendees, list):
                        attendees = [attendees]
                    
                    user_email = f'MAILTO:{self.username}'
                    updated = False
                    
                    for attendee in attendees:
                        if str(attendee).upper() == user_email.upper():
                            attendee.params['PARTSTAT'] = vText(response.upper())
                            if comment:
                                attendee.params['COMMENT'] = vText(comment)
                            updated = True
                            break
                    
                    if not updated:
                        return {
                            "success": False,
                            "error": f"User {self.username} is not an attendee of this event"
                        }
                    
                    # Save updated event
                    caldav_event.data = ical.to_ical()
                    caldav_event.save()
                    
                    return {
                        "success": True,
                        "event_uid": event_uid,
                        "response": response.upper(),
                        "comment": comment
                    }
            
            return {
                "success": False,
                "error": "Event component not found"
            }
            
        except Exception as e:
            logger.error(f"Failed to respond to event: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_event(self, event_uid: str) -> Dict:
        """
        Delete a calendar event.
        
        Args:
            event_uid: UID of the event to delete
        
        Returns:
            Dict with deletion status
        """
        if not self.calendar:
            raise Exception("Not connected to calendar. Call connect() first.")
        
        try:
            caldav_event = self.get_event_by_uid(event_uid)
            
            if not caldav_event:
                return {
                    "success": False,
                    "error": f"Event with UID {event_uid} not found"
                }
            
            caldav_event.delete()
            
            return {
                "success": True,
                "event_uid": event_uid
            }
            
        except Exception as e:
            logger.error(f"Failed to delete event: {e}")
            return {
                "success": False,
                "error": str(e)
            }
