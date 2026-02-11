# 🤖 Telegram Bot per Aruba Email

Gestisci le tue email Aruba direttamente da Telegram!

## 🚀 Setup Veloce

### 1. Crea il Bot Telegram

1. Apri Telegram e cerca **@BotFather**
2. Invia `/newbot`
3. Scegli un nome (es: "Le Mie Email Aruba")
4. Scegli un username (es: `mia_email_aruba_bot`)
5. Copia il **token** che ricevi

### 2. Configura il file .env

Aggiungi al tuo file `.env`:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ

# (Opzionale) Limita l'accesso solo a specifici utenti
# Per trovare il tuo user_id, usa @userinfobot su Telegram
TELEGRAM_AUTHORIZED_USERS=123456789,987654321

# Email Aruba (probabilmente già configurati)
EMAIL_ADDRESS=tua@email.it
EMAIL_PASSWORD=tua_password
IMAP_HOST=imaps.aruba.it
IMAP_PORT=993
SMTP_HOST=smtps.aruba.it
SMTP_PORT=465

# Calendario (opzionale)
CALDAV_URL=https://caldav.aruba.it/...
```

### 3. Installa le dipendenze

```bash
pip install python-telegram-bot python-dotenv
```

### 4. Avvia il bot

```bash
python -m mcp_aruba.telegram_bot
```

## 📱 Comandi Disponibili

| Comando | Descrizione |
|---------|-------------|
| `/start` | Messaggio di benvenuto |
| `/help` | Mostra aiuto |
| `/status` | Stato connessione |
| `/emails` | Ultime 10 email |
| `/emails 5` | Ultime 5 email |
| `/leggi 123` | Leggi email con ID 123 |
| `/cerca fattura` | Cerca "fattura" nelle email |
| `/eventi` | Prossimi eventi calendario |
| `/oggi` | Eventi di oggi |

## 💬 Linguaggio Naturale

Puoi anche scrivere in modo naturale:

- "Mostrami le ultime email"
- "Fammi vedere le ultime 5 mail"
- "Cerca fattura nelle email"
- "Quali sono gli eventi di oggi?"

## 🔒 Sicurezza

### Limitare l'accesso

Per evitare che chiunque possa leggere le tue email, imposta `TELEGRAM_AUTHORIZED_USERS` nel `.env`:

1. Cerca `@userinfobot` su Telegram
2. Invia `/start` per ottenere il tuo user ID
3. Aggiungi al `.env`:
   ```
   TELEGRAM_AUTHORIZED_USERS=123456789
   ```

Se non impostato, chiunque con il link al bot può usarlo!

### Best Practices

- ✅ Usa sempre `TELEGRAM_AUTHORIZED_USERS` in produzione
- ✅ Non condividere il token del bot
- ✅ Usa password app-specific per l'email se disponibile

## 🏃 Esecuzione come Servizio

### macOS (launchd)

Crea `~/Library/LaunchAgents/com.aruba.telegrambot.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aruba.telegrambot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/python</string>
        <string>-m</string>
        <string>mcp_aruba.telegram_bot</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/mcp_aruba</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Poi:
```bash
launchctl load ~/Library/LaunchAgents/com.aruba.telegrambot.plist
```

### Linux (systemd)

Crea `/etc/systemd/system/aruba-telegram-bot.service`:

```ini
[Unit]
Description=Aruba Email Telegram Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/mcp_aruba
ExecStart=/path/to/python -m mcp_aruba.telegram_bot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Poi:
```bash
sudo systemctl enable aruba-telegram-bot
sudo systemctl start aruba-telegram-bot
```

## 🐳 Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .
RUN pip install -e . python-telegram-bot python-dotenv

CMD ["python", "-m", "mcp_aruba.telegram_bot"]
```

```bash
docker build -t aruba-telegram-bot .
docker run -d --env-file .env aruba-telegram-bot
```

## 🔧 Troubleshooting

### "TELEGRAM_BOT_TOKEN non trovato"
- Verifica che il file `.env` sia nella directory corretta
- Verifica che la variabile sia scritta correttamente

### "Non autorizzato"
- Il tuo user_id non è in `TELEGRAM_AUTHORIZED_USERS`
- Usa `@userinfobot` per trovare il tuo ID

### "Client email non configurato"
- Verifica `EMAIL_ADDRESS` e `EMAIL_PASSWORD` nel `.env`
- Verifica che i server IMAP siano raggiungibili

## 📝 Esempio di Conversazione

```
Tu: /start
Bot: 👋 Ciao! Sono il tuo assistente per le email Aruba...

Tu: mostrami le ultime email
Bot: 📬 Recupero ultime 10 email...
     📧 Ultime 10 email:
     1. `42` 
        📩 mario.rossi@esempio.it
        📝 Preventivo progetto XYZ
        🕐 23/01 10:30
     ...

Tu: /leggi 42
Bot: 📧 Email 42
     Da: mario.rossi@esempio.it
     Oggetto: Preventivo progetto XYZ
     ...

Tu: cerca fattura
Bot: 🔍 Risultati per 'fattura':
     1. `38` - Fattura Gennaio 2026
     ...
```

## 🤝 Contributi

Sei il benvenuto per contribuire! Vedi [CONTRIBUTING.md](../CONTRIBUTING.md).
