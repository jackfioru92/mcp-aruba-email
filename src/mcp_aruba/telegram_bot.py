"""Telegram Bot for Aruba Email - Query your emails via Telegram chat."""

import os
import asyncio
import logging
import json
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

from telegram import Update, BotCommand
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    ContextTypes,
    filters
)

from .email_client import ArubaEmailClient
from .calendar_client import ArubaCalendarClient
from .signature import get_signature

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Try to import OpenAI (also works with Ollama via compatible API)
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# Try to import ollama
try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False
    
logger = logging.getLogger(__name__)


class ArubaTelegramBot:
    """Telegram Bot per gestire email Aruba via chat."""
    
    def __init__(self, telegram_token: str, authorized_users: list[int] = None):
        """
        Inizializza il bot Telegram.
        
        Args:
            telegram_token: Token del bot Telegram (@BotFather)
            authorized_users: Lista di Telegram user_id autorizzati (opzionale, per sicurezza)
        """
        self.telegram_token = telegram_token
        self.authorized_users = authorized_users or []
        
        # Email client configuration
        self.email_client: Optional[ArubaEmailClient] = None
        self.calendar_client: Optional[ArubaCalendarClient] = None
        
        # Pending emails waiting for confirmation (user_id -> email_data)
        self.pending_emails: dict = {}
        
        # LLM client for AI interpretation (Ollama or OpenAI)
        self.llm_type = None  # 'ollama' or 'openai'
        self.openai_client = None
        self.ollama_model = None
        self._setup_llm()
        
        self._setup_email_client()
        self._setup_calendar_client()
    
    def _setup_llm(self) -> None:
        """Setup LLM client for AI interpretation (Ollama preferred, OpenAI fallback)."""
        # Try Ollama first (free, local)
        if HAS_OLLAMA:
            self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2:1b')
            try:
                # Test connection
                ollama.list()
                self.llm_type = 'ollama'
                logger.info(f"Ollama configured with model {self.ollama_model} - AI interpretation enabled (FREE)")
                return
            except Exception as e:
                logger.warning(f"Ollama not available: {e}")
        
        # Fallback to OpenAI
        if HAS_OPENAI:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
                self.llm_type = 'openai'
                logger.info("OpenAI client configured - AI interpretation enabled")
                return
        
        logger.warning("No LLM available - using basic interpretation")
    
    def _setup_email_client(self) -> None:
        """Setup email client from environment variables."""
        try:
            self.email_client = ArubaEmailClient(
                host=os.getenv('IMAP_HOST', 'imaps.aruba.it'),
                port=int(os.getenv('IMAP_PORT', 993)),
                username=os.getenv('IMAP_USERNAME') or os.getenv('EMAIL_ADDRESS'),
                password=os.getenv('IMAP_PASSWORD') or os.getenv('EMAIL_PASSWORD'),
                smtp_host=os.getenv('SMTP_HOST', 'smtps.aruba.it'),
                smtp_port=int(os.getenv('SMTP_PORT', 465))
            )
            logger.info("Email client configured")
        except Exception as e:
            logger.error(f"Failed to setup email client: {e}")
    
    def _setup_calendar_client(self) -> None:
        """Setup calendar client from environment variables."""
        try:
            caldav_url = os.getenv('CALDAV_URL')
            if caldav_url:
                self.calendar_client = ArubaCalendarClient(
                    url=caldav_url,
                    username=os.getenv('CALDAV_USERNAME') or os.getenv('IMAP_USERNAME') or os.getenv('EMAIL_ADDRESS'),
                    password=os.getenv('CALDAV_PASSWORD') or os.getenv('IMAP_PASSWORD') or os.getenv('EMAIL_PASSWORD')
                )
                logger.info("Calendar client configured")
        except Exception as e:
            logger.error(f"Failed to setup calendar client: {e}")
    
    def _is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized to use the bot."""
        if not self.authorized_users:
            return True  # No restrictions
        return user_id in self.authorized_users
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user = update.effective_user
        
        if not self._is_authorized(user.id):
            await update.message.reply_text("⛔ Non sei autorizzato ad usare questo bot.")
            return
        
        welcome_message = f"""
👋 Ciao {user.first_name}!

Sono il tuo assistente per le email Aruba. Ecco cosa posso fare:

📧 **Email:**
• /emails - Ultime 10 email
• /emails 5 - Ultime 5 email
• /cerca [termine] - Cerca nelle email
• /da [email] - Email da un mittente
• /leggi [id] - Leggi email completa
• /rispondi [id] [testo] - Rispondi a un'email
• /invia [email] [oggetto] | [testo] - Invia email

📅 **Calendario:**
• /eventi - Eventi prossimi
• /oggi - Eventi di oggi

ℹ️ **Info:**
• /help - Mostra questo messaggio
• /status - Stato connessione

Oppure scrivimi in linguaggio naturale! 💬
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        await self.start_command(update, context)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command."""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Non autorizzato.")
            return
        
        status_text = "📊 **Status Connessione**\n\n"
        
        # Check email
        if self.email_client:
            try:
                self.email_client.connect()
                status_text += "✅ Email: Connesso\n"
                self.email_client.disconnect()
            except Exception as e:
                status_text += f"❌ Email: Errore - {str(e)[:50]}\n"
        else:
            status_text += "⚠️ Email: Non configurato\n"
        
        # Check calendar
        if self.calendar_client:
            try:
                self.calendar_client.connect()
                status_text += "✅ Calendario: Connesso\n"
            except Exception as e:
                status_text += f"❌ Calendario: Errore - {str(e)[:50]}\n"
        else:
            status_text += "⚠️ Calendario: Non configurato\n"
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def emails_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /emails command - List recent emails."""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Non autorizzato.")
            return
        
        if not self.email_client:
            await update.message.reply_text("❌ Client email non configurato.")
            return
        
        # Get limit from args
        limit = 10
        if context.args and context.args[0].isdigit():
            limit = min(int(context.args[0]), 50)
        
        await update.message.reply_text(f"📬 Recupero ultime {limit} email...")
        
        try:
            self.email_client.connect()
            emails = self.email_client.list_emails(folder="INBOX", limit=limit)
            self.email_client.disconnect()
            
            if not emails:
                await update.message.reply_text("📭 Nessuna email trovata.")
                return
            
            response = f"📧 **Ultime {len(emails)} email:**\n\n"
            
            for i, email_item in enumerate(emails, 1):
                # Format date
                date_str = email_item.get('date', 'N/A')
                if isinstance(date_str, datetime):
                    date_str = date_str.strftime('%d/%m %H:%M')
                
                # Truncate subject and sender
                subject = email_item.get('subject', '(Nessun oggetto)')[:40]
                sender = email_item.get('from', 'Sconosciuto')[:30]
                email_id = email_item.get('id', '?')
                
                response += f"**{i}.** `{email_id}`\n"
                response += f"   📩 {sender}\n"
                response += f"   📝 {subject}\n"
                response += f"   🕐 {date_str}\n\n"
            
            response += f"\n💡 Usa `/leggi [id]` per leggere un'email completa"
            
            # Split message if too long
            if len(response) > 4000:
                chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk, parse_mode='Markdown')
            else:
                await update.message.reply_text(response, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            await update.message.reply_text(f"❌ Errore: {str(e)}")
    
    async def read_email_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /leggi command - Read full email."""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Non autorizzato.")
            return
        
        if not self.email_client:
            await update.message.reply_text("❌ Client email non configurato.")
            return
        
        if not context.args:
            await update.message.reply_text("⚠️ Specifica l'ID email: /leggi 123")
            return
        
        email_id = context.args[0]
        
        await update.message.reply_text(f"📖 Leggo email {email_id}...")
        
        try:
            self.email_client.connect()
            email_content = self.email_client.read_email(email_id=email_id, folder="INBOX")
            self.email_client.disconnect()
            
            if not email_content:
                await update.message.reply_text("❌ Email non trovata.")
                return
            
            # Build header (safe text)
            header = f"📧 Email {email_id}\n\n"
            header += f"Da: {email_content.get('from', 'N/A')}\n"
            header += f"A: {email_content.get('to', 'N/A')}\n"
            header += f"Oggetto: {email_content.get('subject', 'N/A')}\n"
            header += f"Data: {email_content.get('date', 'N/A')}\n"
            header += f"\n{'─'*30}\n\n"
            
            body = email_content.get('body', '(Nessun contenuto)')
            # Limit body length for Telegram
            if len(body) > 3000:
                body = body[:3000] + "\n\n... (troncato)"
            
            response = header + body
            
            # Split if too long - NO Markdown to avoid parsing errors
            if len(response) > 4000:
                chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(response)
                
        except Exception as e:
            logger.error(f"Error reading email: {e}")
            await update.message.reply_text(f"❌ Errore: {str(e)}")
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /cerca command - Search emails."""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Non autorizzato.")
            return
        
        if not self.email_client:
            await update.message.reply_text("❌ Client email non configurato.")
            return
        
        if not context.args:
            await update.message.reply_text("⚠️ Specifica cosa cercare: `/cerca fattura`", parse_mode='Markdown')
            return
        
        query = ' '.join(context.args)
        
        await update.message.reply_text(f"🔍 Cerco '{query}'...")
        
        try:
            self.email_client.connect()
            emails = self.email_client.search_emails(query=query, folder="INBOX", limit=10)
            self.email_client.disconnect()
            
            if not emails:
                await update.message.reply_text(f"📭 Nessuna email trovata per '{query}'.")
                return
            
            response = f"🔍 **Risultati per '{query}':**\n\n"
            
            for i, email_item in enumerate(emails, 1):
                subject = email_item.get('subject', '(Nessun oggetto)')[:40]
                sender = email_item.get('from', 'Sconosciuto')[:30]
                email_id = email_item.get('id', '?')
                
                response += f"**{i}.** `{email_id}` - {subject}\n"
                response += f"   Da: {sender}\n\n"
            
            await update.message.reply_text(response, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            await update.message.reply_text(f"❌ Errore: {str(e)}")
    
    async def from_sender_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /da command - List emails from a specific sender."""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Non autorizzato.")
            return
        
        if not self.email_client:
            await update.message.reply_text("❌ Client email non configurato.")
            return
        
        if not context.args:
            await update.message.reply_text("⚠️ Specifica l'email del mittente: `/da mario@esempio.it`", parse_mode='Markdown')
            return
        
        sender_filter = context.args[0]
        limit = 10
        if len(context.args) > 1 and context.args[1].isdigit():
            limit = min(int(context.args[1]), 50)
        
        await update.message.reply_text(f"🔍 Cerco email da '{sender_filter}'...")
        
        try:
            self.email_client.connect()
            emails = self.email_client.list_emails(folder="INBOX", sender_filter=sender_filter, limit=limit)
            self.email_client.disconnect()
            
            if not emails:
                await update.message.reply_text(f"📭 Nessuna email trovata da '{sender_filter}'.")
                return
            
            response = f"📧 **Email da {sender_filter}:**\n\n"
            
            for i, email_item in enumerate(emails, 1):
                subject = email_item.get('subject', '(Nessun oggetto)')[:40]
                date_str = email_item.get('date', 'N/A')
                email_id = email_item.get('id', '?')
                
                response += f"**{i}.** `{email_id}`\n"
                response += f"   📝 {subject}\n"
                response += f"   🕐 {date_str}\n\n"
            
            response += f"\n💡 Usa `/leggi [id]` per leggere, `/rispondi [id] [testo]` per rispondere"
            
            await update.message.reply_text(response, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Error fetching emails from sender: {e}")
            await update.message.reply_text(f"❌ Errore: {str(e)}")
    
    async def reply_email_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /rispondi command - Reply to an email."""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Non autorizzato.")
            return
        
        if not self.email_client:
            await update.message.reply_text("❌ Client email non configurato.")
            return
        
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "⚠️ Formato: `/rispondi [id] [testo risposta]`\n\n"
                "Esempio: `/rispondi 42 Grazie per l'email, ti rispondo presto!`",
                parse_mode='Markdown'
            )
            return
        
        email_id = context.args[0]
        reply_body = ' '.join(context.args[1:])
        
        await update.message.reply_text(f"📤 Preparo risposta all'email {email_id}...")
        
        try:
            # First, read the original email to get sender and subject
            self.email_client.connect()
            original_email = self.email_client.read_email(email_id=email_id, folder="INBOX")
            
            if not original_email:
                self.email_client.disconnect()
                await update.message.reply_text("❌ Email non trovata.")
                return
            
            # Prepare reply
            to_address = original_email.get('from', '')
            original_subject = original_email.get('subject', '')
            
            # Add Re: prefix if not already present
            if not original_subject.lower().startswith('re:'):
                reply_subject = f"Re: {original_subject}"
            else:
                reply_subject = original_subject
            
            # Build reply body with quote
            original_body = original_email.get('body', '')
            original_date = original_email.get('date', '')
            
            full_reply = f"{reply_body}\n\n" \
                        f"---\n" \
                        f"Il {original_date}, {to_address} ha scritto:\n" \
                        f"> {original_body[:500]}{'...' if len(original_body) > 500 else ''}"
            
            # Send the reply
            result = self.email_client.send_email(
                to=to_address,
                subject=reply_subject,
                body=full_reply
            )
            self.email_client.disconnect()
            
            await update.message.reply_text(
                f"✅ **Risposta inviata!**\n\n"
                f"📧 A: {to_address}\n"
                f"📝 Oggetto: {reply_subject}\n\n"
                f"💬 {reply_body[:100]}{'...' if len(reply_body) > 100 else ''}",
                parse_mode='Markdown'
            )
                
        except Exception as e:
            logger.error(f"Error replying to email: {e}")
            await update.message.reply_text(f"❌ Errore nell'invio: {str(e)}")
    
    async def send_email_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /invia command - Send a new email."""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Non autorizzato.")
            return
        
        if not self.email_client:
            await update.message.reply_text("❌ Client email non configurato.")
            return
        
        # Parse: /invia email@dest.it Oggetto della mail | Corpo del messaggio
        if not context.args:
            await update.message.reply_text(
                "⚠️ **Formato:** `/invia [email] [oggetto] | [testo]`\n\n"
                "**Esempio:**\n"
                "`/invia mario@esempio.it Ciao! | Come stai? Volevo sapere...`\n\n"
                "Il carattere `|` separa l'oggetto dal corpo.",
                parse_mode='Markdown'
            )
            return
        
        # Get full text after command
        full_text = ' '.join(context.args)
        
        # Extract email address (first argument)
        to_address = context.args[0]
        
        # Validate email format
        if '@' not in to_address:
            await update.message.reply_text("⚠️ Indirizzo email non valido.")
            return
        
        # Rest of the text is subject | body
        rest = ' '.join(context.args[1:])
        
        if '|' in rest:
            parts = rest.split('|', 1)
            subject = parts[0].strip()
            body = parts[1].strip()
        else:
            # No | separator, use all as subject and ask for body
            subject = rest.strip() if rest.strip() else "(Senza oggetto)"
            body = ""
        
        if not body:
            await update.message.reply_text(
                f"📝 **Bozza email:**\n\n"
                f"📧 A: {to_address}\n"
                f"📋 Oggetto: {subject}\n\n"
                f"⚠️ Manca il corpo! Usa il formato:\n"
                f"`/invia {to_address} {subject} | Il tuo messaggio qui`",
                parse_mode='Markdown'
            )
            return
        
        await update.message.reply_text(f"📤 Invio email a {to_address}...")
        
        try:
            self.email_client.connect()
            result = self.email_client.send_email(
                to=to_address,
                subject=subject,
                body=body
            )
            self.email_client.disconnect()
            
            await update.message.reply_text(
                f"✅ **Email inviata!**\n\n"
                f"📧 A: {to_address}\n"
                f"📋 Oggetto: {subject}\n"
                f"💬 {body[:100]}{'...' if len(body) > 100 else ''}",
                parse_mode='Markdown'
            )
                
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            await update.message.reply_text(f"❌ Errore nell'invio: {str(e)}")
    
    async def events_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /eventi command - List calendar events."""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Non autorizzato.")
            return
        
        if not self.calendar_client:
            await update.message.reply_text("❌ Calendario non configurato.")
            return
        
        await update.message.reply_text("📅 Recupero eventi...")
        
        try:
            self.calendar_client.connect()
            events = self.calendar_client.list_events(limit=10)
            
            if not events:
                await update.message.reply_text("📭 Nessun evento in programma.")
                return
            
            response = "📅 **Prossimi eventi:**\n\n"
            
            for event in events:
                summary = event.get('summary', 'Evento senza titolo')
                start = event.get('start', 'N/A')
                response += f"• **{summary}**\n  🕐 {start}\n\n"
            
            await update.message.reply_text(response, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            await update.message.reply_text(f"❌ Errore: {str(e)}")
    
    async def today_events_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /oggi command - Today's events."""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Non autorizzato.")
            return
        
        if not self.calendar_client:
            await update.message.reply_text("❌ Calendario non configurato.")
            return
        
        await update.message.reply_text("📅 Recupero eventi di oggi...")
        
        try:
            today = datetime.now().replace(hour=0, minute=0, second=0)
            end_of_day = today.replace(hour=23, minute=59, second=59)
            
            self.calendar_client.connect()
            events = self.calendar_client.list_events(
                start_date=today.isoformat(),
                end_date=end_of_day.isoformat()
            )
            
            if not events:
                await update.message.reply_text("📭 Nessun evento oggi.")
                return
            
            response = f"📅 **Eventi di oggi ({today.strftime('%d/%m/%Y')}):**\n\n"
            
            for event in events:
                summary = event.get('summary', 'Evento senza titolo')
                start = event.get('start', 'N/A')
                response += f"• **{summary}**\n  🕐 {start}\n\n"
            
            await update.message.reply_text(response, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Error fetching today's events: {e}")
            await update.message.reply_text(f"❌ Errore: {str(e)}")
    
    def _resolve_contact(self, name: str) -> Optional[str]:
        """Resolve contact name to email address."""
        # Contact book - add your frequent contacts here!
        contacts = {
            # Nome -> email
            'christopher': 'christopher.caponi@emotion-team.com',
            'christopher caponi': 'christopher.caponi@emotion-team.com',
            'chris': 'christopher.caponi@emotion-team.com',
            'caponi': 'christopher.caponi@emotion-team.com',
            # Add more contacts as needed
        }
        
        name_lower = name.lower().strip()
        
        # Direct match
        if name_lower in contacts:
            return contacts[name_lower]
        
        # Partial match
        for contact_name, email in contacts.items():
            if contact_name in name_lower or name_lower in contact_name:
                return email
        
        return None
    
    async def natural_language_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle natural language messages."""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Non autorizzato.")
            return
        
        import re
        text = update.message.text
        text_lower = text.lower().strip()
        user_id = update.effective_user.id
        
        # === CHECK FOR PENDING EMAIL CONFIRMATION ===
        if user_id in self.pending_emails:
            pending = self.pending_emails[user_id]
            
            # Confirm send
            if text_lower in ['sì', 'si', 'yes', 'ok', 'invia', 'manda', 'conferma', 'vai']:
                await self._do_send_email(update, pending['to'], pending['subject'], pending['body'])
                del self.pending_emails[user_id]
                return
            
            # Cancel
            if text_lower in ['no', 'annulla', 'cancel', 'cancella', 'stop']:
                del self.pending_emails[user_id]
                await update.message.reply_text("❌ Email annullata.")
                return
            
            # Modify message
            if text_lower.startswith('modifica:') or text_lower.startswith('cambia:'):
                new_body = text.split(':', 1)[1].strip()
                if new_body:
                    pending['body'] = new_body
                    pending['subject'] = self._generate_subject(new_body)
                    
                    preview = f"""📧 **Email Modificata**

**A:** {pending['to']}
**Oggetto:** {pending['subject']}

**Messaggio:**
{pending['body']}

❓ **Confermi l'invio?** (sì/no)"""
                    await update.message.reply_text(preview, parse_mode='Markdown')
                    return
            
            # Modify subject
            if text_lower.startswith('oggetto:'):
                new_subject = text.split(':', 1)[1].strip()
                if new_subject:
                    pending['subject'] = new_subject
                    await update.message.reply_text(f"✏️ Oggetto cambiato in: {new_subject}\n\nConfermi l'invio? (sì/no)")
                    return
            
            # If not a confirmation command, ask again
            await update.message.reply_text(
                "⚠️ Hai un'email in attesa!\n\n"
                "• \"sì\" per inviare\n"
                "• \"no\" per annullare\n"
                "• \"modifica: [nuovo testo]\" per cambiare"
            )
            return
        
        # === SEND EMAIL IN NATURAL LANGUAGE ===
        
        # First check if there's a send intent
        send_keywords = ['manda', 'invia', 'scrivi', 'comunica', 'di a', 'dì a', 'chiedi', 'avvisa', 'contatta', 
                         'digli', 'dille', 'chiedigli', 'chiedile', 'avvisalo', 'avvisala', 'contattalo', 'contattala']
        has_send_intent = any(word in text_lower for word in send_keywords)
        
        if has_send_intent:
            # Try to find email address first
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text, re.IGNORECASE)
            
            if email_match:
                to_address = email_match.group(1)
                # Extract message (everything that's not the email and not the command words)
                message_content = re.sub(r'(?:manda|invia|scrivi|di|dì|chiedi|comunica|avvisa|contatta)(?:\s+(?:una?\s+)?(?:email|mail))?\s+a\s+', '', text, flags=re.IGNORECASE)
                message_content = re.sub(re.escape(to_address), '', message_content).strip()
                
                if message_content:
                    await self._send_natural_email(update, to_address, message_content)
                    return
            
            # No email found - try to resolve contact name
            # Pattern: "manda/scrivi a [NOME] [messaggio]" or "digli/dille che..."
            
            # First try "digli/dille" patterns (without "a")
            digli_match = re.search(r'(?:digli|dille|chiedigli|chiedile|avvisalo|avvisala)\s+(?:che\s+|se\s+|di\s+)?(.+)', text, re.IGNORECASE)
            if digli_match:
                # Need to find who - check if there's a name before
                name_match = re.search(r'(?:a\s+)?([a-zA-Z]+(?:\s+[a-zA-Z]+)?)\s+(?:digli|dille|chiedigli|chiedile)', text, re.IGNORECASE)
                if name_match:
                    contact_name = name_match.group(1).strip()
                    message_content = digli_match.group(1).strip()
                    resolved_email = self._resolve_contact(contact_name)
                    if resolved_email:
                        interpreted_message = self._interpret_message(message_content)
                        await self._send_natural_email(update, resolved_email, interpreted_message)
                        return
            
            contact_match = re.search(r'(?:manda|invia|scrivi|di|dì|chiedi|comunica|avvisa|contatta)(?:\s+(?:una?\s+)?(?:email|mail))?\s+a\s+([^,\.!?\n]+?)(?:\s+(?:che|dicendo|per|se)\s+|\s+)(.+)', text, re.IGNORECASE)
            
            if contact_match:
                contact_name = contact_match.group(1).strip()
                message_content = contact_match.group(2).strip()
                
                # Try to resolve contact
                resolved_email = self._resolve_contact(contact_name)
                
                if resolved_email:
                    interpreted_message = self._interpret_message(message_content)
                    await self._send_natural_email(update, resolved_email, interpreted_message)
                    return
                else:
                    await update.message.reply_text(
                        f"📇 Non conosco '{contact_name}'.\n\n"
                        f"Scrivi l'indirizzo email completo:\n"
                        f"`manda email a nome@esempio.it {message_content}`",
                        parse_mode='Markdown'
                    )
                    return
        
        # === LIST EMAILS ===
        if any(word in text_lower for word in ['email', 'mail', 'posta', 'messaggi', 'inbox']):
            if any(word in text_lower for word in ['ultime', 'recenti', 'nuove', 'arrivate', 'mostra', 'vedi', 'leggi']):
                numbers = re.findall(r'\d+', text_lower)
                if numbers:
                    context.args = [numbers[0]]
                else:
                    context.args = []
                await self.emails_command(update, context)
                return
            elif any(word in text_lower for word in ['cerca', 'trovare', 'cercare']):
                for keyword in ['cerca', 'trovare', 'cercare']:
                    if keyword in text_lower:
                        query = text_lower.split(keyword)[-1].strip()
                        if query:
                            context.args = [query]
                            await self.search_command(update, context)
                            return
        
        # === CALENDAR ===
        if any(word in text_lower for word in ['eventi', 'calendario', 'appuntamenti', 'riunioni']):
            if 'oggi' in text_lower:
                await self.today_events_command(update, context)
            else:
                await self.events_command(update, context)
            return
        
        # Default response
        await update.message.reply_text(
            "🤔 Non ho capito. Prova con:\n\n"
            "• \"Mostrami le ultime email\"\n"
            "• \"Cerca fattura nelle email\"\n"
            "• \"Manda email a mario@ex.it dicendo che...\"\n"
            "• \"Eventi di oggi\"\n\n"
            "Oppure usa i comandi: /emails, /cerca, /invia, /eventi"
        )
    
    async def _send_natural_email(self, update: Update, to_address: str, message_content: str) -> None:
        """Process and send email from natural language."""
        import re
        
        if not self.email_client:
            await update.message.reply_text("❌ Client email non configurato.")
            return
        
        # Check if signature is requested
        include_signature = any(word in message_content.lower() for word in ['firma', 'signature', 'firmato', 'in calce'])
        
        # Use AI to interpret the message if available
        if self.openai_client:
            await update.message.reply_text("🤖 Interpreto il messaggio...")
            interpreted = await self._ai_interpret_email(message_content, to_address)
            if interpreted:
                subject = interpreted.get('subject', 'Messaggio')
                body = interpreted.get('body', message_content)
            else:
                # Fallback to basic interpretation
                body = self._interpret_message(message_content)
                subject = self._generate_subject(body)
        else:
            # Basic interpretation
            body = self._interpret_message(message_content)
            subject = self._generate_subject(body)
        
        # Add signature if requested
        if include_signature:
            signature = get_signature()
            if signature:
                body += f"\n\n{signature}"
        
        # Show preview and ask confirmation
        preview = f"""📧 **Anteprima Email**

**A:** {to_address}
**Oggetto:** {subject}

**Messaggio:**
{body}

{'✍️ _Con firma_' if include_signature else ''}

❓ **Confermi l'invio?**
• Rispondi "sì" o "ok" per inviare
• Rispondi "no" o "annulla" per cancellare
• Rispondi "modifica: [nuovo testo]" per cambiare"""
        
        await update.message.reply_text(preview, parse_mode='Markdown')
        
        # Store pending email for confirmation
        user_id = update.effective_user.id
        self.pending_emails[user_id] = {
            'to': to_address,
            'subject': subject,
            'body': body
        }
        logger.info(f"Email in attesa di conferma per user {user_id}")
    
    async def _ai_interpret_email(self, user_message: str, recipient_email: str) -> Optional[dict]:
        """Use AI to interpret user message into a proper email."""
        if not self.llm_type:
            return None
        
        try:
            # Get recipient name from email
            recipient_name = recipient_email.split('@')[0].replace('.', ' ').title()
            
            prompt = f"""Sei un assistente che trasforma messaggi informali in email professionali ma amichevoli.

L'utente vuole mandare un'email a {recipient_name} ({recipient_email}).

Messaggio dell'utente: "{user_message}"

Trasforma questo in un'email appropriata. Interpreta il significato:
- "se sta bene" = chiedi come sta
- "se ci va di vederci" = proponi un incontro
- "digli di..." = comunica qualcosa
- Aggiungi un saluto iniziale appropriato (Ciao, Buongiorno, etc.)
- Mantieni un tono amichevole ma professionale

Rispondi SOLO con un JSON valido in questo formato:
{{"subject": "oggetto breve e descrittivo", "body": "corpo dell'email completo"}}

Non aggiungere altro testo, solo il JSON."""

            result_text = None
            
            if self.llm_type == 'ollama':
                # Use Ollama (free, local)
                response = ollama.chat(
                    model=self.ollama_model,
                    messages=[
                        {"role": "system", "content": "Sei un assistente che genera email. Rispondi solo con JSON valido."},
                        {"role": "user", "content": prompt}
                    ],
                    options={"temperature": 0.7}
                )
                result_text = response['message']['content'].strip()
                
            elif self.llm_type == 'openai':
                # Use OpenAI
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Sei un assistente che genera email. Rispondi solo con JSON valido."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                result_text = response.choices[0].message.content.strip()
            
            if not result_text:
                return None
            
            # Parse JSON response
            # Clean up potential markdown code blocks
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            result_text = result_text.strip()
            
            result = json.loads(result_text)
            logger.info(f"AI interpreted email ({self.llm_type}): {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in AI interpretation: {e}")
            return None
    
    def _interpret_message(self, raw_message: str) -> str:
        """Interpret shorthand message into proper email text."""
        import re
        msg = raw_message.strip()
        msg_lower = msg.lower()
        
        # Start with greeting if not present
        has_greeting = any(word in msg_lower for word in ['ciao', 'buongiorno', 'buonasera', 'salve', 'hey', 'hi'])
        
        result_parts = []
        
        if not has_greeting:
            result_parts.append("Ciao!")
        
        # Interpret common patterns
        # "se sta bene" -> "Come stai?"
        if 'se sta bene' in msg_lower or 'come sta' in msg_lower or 'sta bene' in msg_lower:
            result_parts.append("Come stai?")
            msg = re.sub(r'se\s+sta\s+bene|come\s+sta|sta\s+bene', '', msg, flags=re.IGNORECASE).strip()
        
        # "se ci va di vederci" -> "Ti va di vederci?"
        if 'se ci va di vederci' in msg_lower or 'vederci' in msg_lower:
            result_parts.append("Ti va di vederci?")
            msg = re.sub(r'se\s+ci\s+va\s+di\s+vederci|ci\s+va\s+di\s+vederci|vederci', '', msg, flags=re.IGNORECASE).strip()
        
        # "se può" -> "Potresti..."
        if 'se può' in msg_lower or 'se puoi' in msg_lower:
            msg = re.sub(r'se\s+può|se\s+puoi', 'Potresti', msg, flags=re.IGNORECASE)
        
        # "digli di" -> remove, it's a command
        msg = re.sub(r'^\s*(?:digli|dille|chiedigli|chiedile)\s+(?:che\s+|se\s+|di\s+)?', '', msg, flags=re.IGNORECASE).strip()
        
        # Clean up punctuation
        msg = re.sub(r'[,;]\s*[,;]', ',', msg)  # Remove duplicate punctuation
        msg = re.sub(r'\s+', ' ', msg).strip()  # Clean whitespace
        
        # Add remaining message if any
        if msg and not msg.isspace():
            # Capitalize first letter
            msg = msg[0].upper() + msg[1:] if len(msg) > 1 else msg.upper()
            # Add period if no punctuation at end
            if msg and msg[-1] not in '.!?':
                msg += '.'
            result_parts.append(msg)
        
        # Join all parts
        result = '\n\n'.join(result_parts) if result_parts else raw_message
        
        return result
    
    def _generate_subject(self, content: str) -> str:
        """Generate email subject from content."""
        content_lower = content.lower()
        
        # Common patterns
        if any(word in content_lower for word in ['riunione', 'meeting', 'incontro']):
            return "Riunione"
        if any(word in content_lower for word in ['fattura', 'pagamento', 'invoice']):
            return "Fattura"
        if any(word in content_lower for word in ['progetto', 'project']):
            return "Aggiornamento Progetto"
        if any(word in content_lower for word in ['attività', 'programma', 'agenda', 'oggi']):
            return "Attività in programma"
        if any(word in content_lower for word in ['conferma', 'confirm']):
            return "Conferma"
        if any(word in content_lower for word in ['preventivo', 'offerta', 'quotation']):
            return "Preventivo"
        if any(word in content_lower for word in ['domanda', 'question', 'chiedo']):
            return "Richiesta informazioni"
        if any(word in content_lower for word in ['grazie', 'ringrazi']):
            return "Ringraziamento"
        if any(word in content_lower for word in ['urgente', 'urgent']):
            return "URGENTE"
        
        # Extract first meaningful words
        words = content.split()[:5]
        if words:
            return ' '.join(words)[:50]
        
        return "Messaggio"
    
    async def _do_send_email(self, update: Update, to: str, subject: str, body: str) -> None:
        """Actually send the email."""
        try:
            self.email_client.connect()
            self.email_client.send_email(to=to, subject=subject, body=body)
            self.email_client.disconnect()
            
            await update.message.reply_text(
                f"✅ **Email inviata!**\n\n"
                f"📧 A: {to}\n"
                f"📋 Oggetto: {subject}",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            await update.message.reply_text(f"❌ Errore: {str(e)}")
    
    async def _set_bot_commands(self, application) -> None:
        """Set bot commands in Telegram menu."""
        commands = [
            BotCommand("emails", "📧 Ultime email"),
            BotCommand("cerca", "🔍 Cerca nelle email"),
            BotCommand("da", "👤 Email da un mittente"),
            BotCommand("leggi", "📖 Leggi email completa"),
            BotCommand("rispondi", "↩️ Rispondi a un'email"),
            BotCommand("invia", "✉️ Invia nuova email"),
            BotCommand("eventi", "📅 Prossimi eventi"),
            BotCommand("oggi", "🗓 Eventi di oggi"),
            BotCommand("status", "📊 Stato connessione"),
            BotCommand("help", "❓ Mostra aiuto"),
        ]
        await application.bot.set_my_commands(commands)
        logger.info("📋 Menu comandi registrato su Telegram")
    
    def run(self) -> None:
        """Start the Telegram bot."""
        if not self.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN non configurato!")
        
        # Create application
        application = Application.builder().token(self.telegram_token).post_init(self._set_bot_commands).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("emails", self.emails_command))
        application.add_handler(CommandHandler("leggi", self.read_email_command))
        application.add_handler(CommandHandler("cerca", self.search_command))
        application.add_handler(CommandHandler("da", self.from_sender_command))
        application.add_handler(CommandHandler("rispondi", self.reply_email_command))
        application.add_handler(CommandHandler("invia", self.send_email_command))
        application.add_handler(CommandHandler("eventi", self.events_command))
        application.add_handler(CommandHandler("oggi", self.today_events_command))
        
        # Natural language handler (for non-command messages)
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.natural_language_handler
        ))
        
        logger.info("🤖 Bot Telegram avviato!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Entry point per il bot Telegram."""
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not telegram_token:
        print("❌ Errore: TELEGRAM_BOT_TOKEN non trovato nel file .env")
        print("\nPer configurare il bot:")
        print("1. Vai su Telegram e cerca @BotFather")
        print("2. Crea un nuovo bot con /newbot")
        print("3. Copia il token e aggiungilo al file .env:")
        print("   TELEGRAM_BOT_TOKEN=your_token_here")
        return
    
    # Optional: list of authorized Telegram user IDs
    authorized_users_str = os.getenv('TELEGRAM_AUTHORIZED_USERS', '')
    authorized_users = []
    if authorized_users_str:
        authorized_users = [int(uid.strip()) for uid in authorized_users_str.split(',') if uid.strip()]
    
    bot = ArubaTelegramBot(
        telegram_token=telegram_token,
        authorized_users=authorized_users
    )
    
    print("🚀 Avvio bot Telegram per Aruba Email...")
    print("   Premi Ctrl+C per fermare")
    
    bot.run()


if __name__ == "__main__":
    main()
