from src.mcp_aruba.email_client import ArubaEmailClient
from dotenv import load_dotenv
import os

# Carica variabili d'ambiente dal file .env
load_dotenv()

print('📧 Test invio email con firma personalizzata...')
print()

# Leggi credenziali da environment variables
email = os.getenv('ARUBA_EMAIL') or os.getenv('IMAP_USERNAME') or 'giacomo.fiorucci@emotion-team.com'
password = os.getenv('ARUBA_PASSWORD') or os.getenv('IMAP_PASSWORD')

if not password:
    print('⚠️  Credenziali non trovate nel file .env')
    print('Aggiungi ARUBA_EMAIL e ARUBA_PASSWORD al file .env oppure:')
    email = input('📧 Email Aruba: ')
    password = input('🔑 Password: ')
    print()

client = ArubaEmailClient(
    host='imaps.aruba.it',
    port=993,
    username=email,
    password=password,
    smtp_host='smtps.aruba.it',
    smtp_port=465
)

print('📤 Invio email di test...')
result = client.send_email(
    to='giacomo.fiorucci@emotion-team.com',
    subject='Test Firma Personalizzata - Emotion Team',
    body='Ciao!\n\nQuesta è una email di test per verificare la nuova firma con il colore aziendale #1ca2c8.\n\nLa firma dovrebbe apparire automaticamente in fondo a questa email con la mia foto e lo stile professionale.\n\nBuona giornata!',
    use_signature=True,
    verify_recipient=False
)

if result:
    print('✅ Email inviata con successo!')
    print('📬 Controlla la tua casella per vedere la firma in azione')
else:
    print('❌ Errore nell\'invio')
