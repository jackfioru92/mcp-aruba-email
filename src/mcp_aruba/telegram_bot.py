"""Telegram Bot for Aruba Email - Query your emails via Telegram chat."""

import os
import asyncio
import logging
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    ContextTypes,
    filters
)

from .email_client import ArubaEmailClient
from .calendar_client import ArubaCalendarClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
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
        
        self._setup_email_client()
        self._setup_calendar_client()
    
    def _setup_email_client(self) -> None:
        """Setup email client from environment variables."""
        try:
            self.email_client = ArubaEmailClient(
                host=os.getenv('IMAP_HOST', 'imaps.aruba.it'),
                port=int(os.getenv('IMAP_PORT', 993)),
                username=os.getenv('EMAIL_ADDRESS'),
                password=os.getenv('EMAIL_PASSWORD'),
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
                    username=os.getenv('EMAIL_ADDRESS'),
                    password=os.getenv('EMAIL_PASSWORD')
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
• /leggi [id] - Leggi email completa

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
            await update.message.reply_text("⚠️ Specifica l'ID email: `/leggi 123`", parse_mode='Markdown')
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
            
            response = f"📧 **Email {email_id}**\n\n"
            response += f"**Da:** {email_content.get('from', 'N/A')}\n"
            response += f"**A:** {email_content.get('to', 'N/A')}\n"
            response += f"**Oggetto:** {email_content.get('subject', 'N/A')}\n"
            response += f"**Data:** {email_content.get('date', 'N/A')}\n"
            response += f"\n{'─'*30}\n\n"
            
            body = email_content.get('body', '(Nessun contenuto)')
            # Limit body length for Telegram
            if len(body) > 3000:
                body = body[:3000] + "\n\n... (troncato)"
            response += body
            
            # Split if too long
            if len(response) > 4000:
                chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk, parse_mode='Markdown')
            else:
                await update.message.reply_text(response, parse_mode='Markdown')
                
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
    
    async def natural_language_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle natural language messages."""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Non autorizzato.")
            return
        
        text = update.message.text.lower()
        
        # Simple intent detection
        if any(word in text for word in ['email', 'mail', 'posta', 'messaggi', 'inbox']):
            if any(word in text for word in ['ultime', 'recenti', 'nuove', 'arrivate', 'mostra', 'vedi']):
                # Extract number if present
                import re
                numbers = re.findall(r'\d+', text)
                if numbers:
                    context.args = [numbers[0]]
                else:
                    context.args = []
                await self.emails_command(update, context)
                return
            elif any(word in text for word in ['cerca', 'trovare', 'cercare']):
                # Extract search query
                for keyword in ['cerca', 'trovare', 'cercare']:
                    if keyword in text:
                        query = text.split(keyword)[-1].strip()
                        if query:
                            context.args = [query]
                            await self.search_command(update, context)
                            return
        
        if any(word in text for word in ['eventi', 'calendario', 'appuntamenti', 'riunioni']):
            if 'oggi' in text:
                await self.today_events_command(update, context)
            else:
                await self.events_command(update, context)
            return
        
        # Default response
        await update.message.reply_text(
            "🤔 Non ho capito. Prova con:\n\n"
            "• \"Mostrami le ultime email\"\n"
            "• \"Cerca fattura nelle email\"\n"
            "• \"Eventi di oggi\"\n\n"
            "Oppure usa i comandi: /emails, /cerca, /eventi"
        )
    
    def run(self) -> None:
        """Start the Telegram bot."""
        if not self.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN non configurato!")
        
        # Create application
        application = Application.builder().token(self.telegram_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("emails", self.emails_command))
        application.add_handler(CommandHandler("leggi", self.read_email_command))
        application.add_handler(CommandHandler("cerca", self.search_command))
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
