"""Send calendar event invitation via email."""

import os
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from dotenv import load_dotenv
from icalendar import Calendar, Event as ICalEvent, vCalAddress, vText
import uuid

# Load environment variables
load_dotenv()

def send_calendar_invite():
    """Send calendar invitation via email with .ics attachment."""
    print("Sending calendar invitation via email...")
    print("=" * 60)
    
    # Email configuration
    smtp_host = "smtps.aruba.it"
    smtp_port = 465
    username = os.getenv("IMAP_USERNAME")
    password = os.getenv("IMAP_PASSWORD")
    
    if not username or not password:
        print("❌ Error: Email credentials not configured")
        return
    
    # Event details
    tomorrow = datetime.now() + timedelta(days=1)
    start = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)
    end = tomorrow.replace(hour=15, minute=30, second=0, microsecond=0)
    
    organizer_email = username
    attendee_email = username  # Send to yourself
    event_title = "Domani non faccio una sega"
    
    print(f"From: {organizer_email}")
    print(f"To: {attendee_email}")
    print(f"Event: {event_title}")
    print(f"Start: {start.strftime('%d/%m/%Y %H:%M')}")
    print(f"End: {end.strftime('%d/%m/%Y %H:%M')}")
    print()
    
    # Create iCalendar event
    cal = Calendar()
    cal.add('prodid', '-//MCP Aruba Calendar//EN')
    cal.add('version', '2.0')
    cal.add('method', 'REQUEST')
    
    event = ICalEvent()
    event.add('uid', str(uuid.uuid4()))
    event.add('dtstamp', datetime.now())
    event.add('dtstart', start)
    event.add('dtend', end)
    event.add('summary', event_title)
    event.add('description', 'Evento creato tramite MCP Aruba Calendar')
    event.add('location', 'Ufficio')
    event.add('status', 'CONFIRMED')
    event.add('sequence', 0)
    
    # Add organizer
    organizer = vCalAddress(f'MAILTO:{organizer_email}')
    organizer.params['cn'] = vText('Giacomo Fiorucci')
    organizer.params['role'] = vText('CHAIR')
    event.add('organizer', organizer)
    
    # Add attendee
    attendee = vCalAddress(f'MAILTO:{attendee_email}')
    attendee.params['cn'] = vText('Christopher Caponi')
    attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
    attendee.params['PARTSTAT'] = vText('NEEDS-ACTION')
    attendee.params['RSVP'] = vText('TRUE')
    event.add('attendee', attendee)
    
    cal.add_component(event)
    
    # Create email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Invito: {event_title}"
    msg['From'] = f"Giacomo Fiorucci <{organizer_email}>"
    msg['To'] = attendee_email
    
    # Plain text version
    text_body = f"""
Invito a un evento del calendario

Evento: {event_title}
Data: {start.strftime('%d/%m/%Y')}
Ora: {start.strftime('%H:%M')} - {end.strftime('%H:%M')}
Luogo: Ufficio

Organizzatore: Giacomo Fiorucci ({organizer_email})

Accetta o declina questo invito aprendo l'allegato .ics
"""
    
    # HTML version
    html_body = f"""
<html>
<body>
<h2>📅 Invito a un evento del calendario</h2>
<table border="1" cellpadding="10" style="border-collapse: collapse;">
<tr><td><strong>Evento:</strong></td><td>{event_title}</td></tr>
<tr><td><strong>Data:</strong></td><td>{start.strftime('%d/%m/%Y')}</td></tr>
<tr><td><strong>Ora:</strong></td><td>{start.strftime('%H:%M')} - {end.strftime('%H:%M')}</td></tr>
<tr><td><strong>Luogo:</strong></td><td>Ufficio</td></tr>
<tr><td><strong>Organizzatore:</strong></td><td>Giacomo Fiorucci ({organizer_email})</td></tr>
</table>
<br>
<p>Apri l'allegato <strong>invite.ics</strong> per accettare o declinare questo invito.</p>
</body>
</html>
"""
    
    msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
    
    # Attach .ics file
    ics_attachment = MIMEBase('text', 'calendar', method='REQUEST', name='invite.ics')
    ics_attachment.set_payload(cal.to_ical())
    ics_attachment.add_header('Content-Disposition', 'attachment', filename='invite.ics')
    msg.attach(ics_attachment)
    
    # Send email
    try:
        print("Connecting to SMTP server...")
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(username, password)
            print("✅ Connected and authenticated")
            
            print("Sending invitation...")
            server.send_message(msg)
            print("✅ Calendar invitation sent successfully!")
            print()
            print(f"📧 Christopher Caponi dovrebbe ricevere l'invito via email")
            print(f"📎 L'email contiene un file invite.ics che può aprire con il suo calendario")
            print(f"📅 L'evento apparirà nel suo calendario dopo l'accettazione")
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    send_calendar_invite()
