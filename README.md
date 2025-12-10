# MCP Aruba Email & Calendar Server

<!-- mcp-name: io.github.jackfioru92/aruba-email -->

**Italiano** | [English](README_EN.md)

Server MCP (Model Context Protocol) per accedere a email e calendario Aruba tramite IMAP/SMTP/CalDAV. Integra facilmente email e calendario Aruba con assistenti AI come Claude!

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-1.2.0+-green.svg)](https://modelcontextprotocol.io/)

**Italiano** | [English](README.md)

## Funzionalità

### Email
- 📧 **Elenca email** - Naviga nella casella con filtri per mittente
- 🔍 **Cerca email** - Ricerca per oggetto/corpo con filtri data
- 📖 **Leggi email** - Ottieni il contenuto completo
- ✉️ **Invia email** - Invia email via SMTP con firma personalizzata
- ✍️ **Firma email** - Crea firme professionali con foto e colori brand

### Calendario
- 📅 **Crea eventi** - Crea eventi calendario con partecipanti
- 📋 **Elenca eventi** - Visualizza eventi futuri
- ✅ **Accetta inviti** - Accetta inviti calendario
- ❌ **Declina inviti** - Declina inviti calendario
- ❓ **Forse** - Rispondi "forse" agli inviti calendario
- 🗑️ **Elimina eventi** - Rimuovi eventi dal calendario

### Generale
- 🔒 **Sicuro** - Usa IMAP/SMTP/CalDAV su SSL/TLS
- ⚡ **Veloce** - Gestione efficiente delle connessioni con context manager
- 🤖 **Pronto per AI** - Funziona perfettamente con Claude Desktop e altri client MCP

## Installazione

```bash
# Clona il repository
git clone https://github.com/jackfioru92/mcp-aruba-email.git
cd mcp-aruba-email

# Crea ambiente virtuale
python -m venv .venv
source .venv/bin/activate  # Su Windows: .venv\Scripts\activate

# Installa dipendenze
pip install -e .
```

## Configurazione

1. Copia `.env.example` in `.env`:
```bash
cp .env.example .env
```

2. Modifica `.env` con le tue credenziali Aruba:
```env
# Configurazione Email
IMAP_HOST=imaps.aruba.it
IMAP_PORT=993
IMAP_USERNAME=tua_email@aruba.it
IMAP_PASSWORD=tua_password

SMTP_HOST=smtps.aruba.it
SMTP_PORT=465

# Configurazione Calendario
CALDAV_URL=https://syncdav.aruba.it/calendars/tua_email@aruba.it/
CALDAV_USERNAME=tua_email@aruba.it
CALDAV_PASSWORD=tua_password
```

3. **(Opzionale) Configura la tua firma email personalizzata:**

   **Metodo 1: Script Interattivo** (Consigliato)
   ```bash
   # Esegui lo script interattivo
   python setup_signature.py
   ```
   
   Lo script ti guiderà nella creazione di una firma professionale con:
   - 📝 Informazioni personali (nome, ruolo, azienda, contatti)
   - 🎨 Scelta dello stile (professional, minimal, colorful)
   - 🌈 Personalizzazione colori
   - 📸 Upload automatico foto su Imgur (opzionale)

   **Metodo 2: Tramite Claude** (Ancora più semplice!)
   ```
   Dopo aver configurato Claude Desktop, chiedi direttamente:
   
   "Crea una firma email per me con nome Mario Rossi, 
    ruolo Software Developer, azienda TechCorp e colore #0066cc"
   
   "Configura la mia firma con questa foto: /path/to/photo.jpg"
   
   "Imposta una firma minimal con solo nome e email"
   ```
   
   Claude userà automaticamente i tool MCP per creare la tua firma!

La firma verrà inclusa automaticamente in tutte le email inviate.

> **Nota**: Le credenziali sono memorizzate localmente e non lasciano mai il tuo computer. Il server MCP viene eseguito localmente e si connette direttamente ai server Aruba.

## Utilizzo

### Esegui il server direttamente

```bash
python -m mcp_aruba.server
```

### Configura con Claude Desktop

Vedi [CLAUDE_SETUP.md](CLAUDE_SETUP.md) per istruzioni dettagliate.

Configurazione rapida per `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aruba-email-calendar": {
      "command": "python",
      "args": ["-m", "mcp_aruba.server"],
      "env": {
        "IMAP_HOST": "imaps.aruba.it",
        "IMAP_PORT": "993",
        "IMAP_USERNAME": "tua_email@aruba.it",
        "IMAP_PASSWORD": "tua_password",
        "SMTP_HOST": "smtps.aruba.it",
        "SMTP_PORT": "465",
        "CALDAV_URL": "https://syncdav.aruba.it/calendars/tua_email@aruba.it/",
        "CALDAV_USERNAME": "tua_email@aruba.it",
        "CALDAV_PASSWORD": "tua_password"
      }
    }
  }
}
```

### Configura con VS Code Copilot

Vedi [VSCODE_SETUP.md](VSCODE_SETUP.md) per istruzioni dettagliate sull'uso di questo server con l'estensione Copilot MCP di VS Code.

### Usa la CLI rapida

```bash
# Attiva ambiente virtuale
source .venv/bin/activate

# Mostra ultime 5 email
python cli.py emails

# Mostra ultime 10 email
python cli.py emails 10

# Mostra eventi prossimi 7 giorni
python cli.py calendar

# Mostra eventi prossimi 14 giorni
python cli.py calendar 14
```

## Strumenti Disponibili

### Strumenti Email

#### `list_emails`
Elenca email recenti con filtri opzionali.

**Parametri:**
- `folder` (str, default: "INBOX") - Cartella email da leggere
- `sender_filter` (str, opzionale) - Filtra per email mittente
- `limit` (int, default: 10, max: 50) - Numero di email da restituire

**Esempi:**
```
Mostra le ultime 5 email da john@example.com
Elenca email recenti nella mia inbox
Dammi le 10 email più recenti dal mio capo
```

#### `read_email`
Leggi il contenuto completo di un'email specifica.

**Parametri:**
- `email_id` (str) - ID email da list_emails
- `folder` (str, default: "INBOX") - Cartella email

**Esempi:**
```
Leggi l'email 123
Mostrami il contenuto completo dell'email 456
```

#### `search_emails`
Cerca email per oggetto o contenuto corpo.

**Parametri:**
- `query` (str) - Query di ricerca
- `folder` (str, default: "INBOX") - Cartella dove cercare
- `from_date` (str, opzionale) - Solo email da questa data (formato: DD-MMM-YYYY)
- `limit` (int, default: 10, max: 50) - Numero massimo di risultati

**Esempi:**
```
Cerca email che parlano di "API" dalla settimana scorsa
Trova tutte le email su "fattura" da dicembre
```

#### `send_email`
Invia un'email via SMTP.

**Parametri:**
- `to` (str) - Indirizzo email destinatario
- `subject` (str) - Oggetto email
- `body` (str) - Corpo email (testo semplice)
- `from_name` (str, default: "Giacomo Fiorucci") - Nome visualizzato mittente
- `use_signature` (bool, default: True) - Include la firma email se configurata
- `verify_recipient` (bool, default: True) - Verifica che l'email destinatario esista

**Esempi:**
```
Invia un'email a colleague@example.com ringraziando per l'aggiornamento
Rispondi a john@example.com con lo stato del progetto
```

**Nota sulla firma**: Se hai configurato una firma usando `setup_signature.py`, verrà automaticamente inclusa nelle email. Puoi disabilitarla temporaneamente con `use_signature=False`.

#### `set_email_signature`
Configura una firma email personalizzata.

**Parametri:**
- `name` (str) - Nome completo
- `email` (str) - Indirizzo email
- `role` (str, opzionale) - Ruolo/posizione
- `company` (str, opzionale) - Nome azienda
- `phone` (str, opzionale) - Numero di telefono
- `website` (str, opzionale) - Sito web
- `photo_input` (str, opzionale) - Percorso file foto o URL (upload automatico su Imgur)
- `style` (str, default: "professional") - Stile: professional, minimal, colorful
- `color` (str, default: "#0066cc") - Colore principale (formato esadecimale)
- `signature_name` (str, default: "default") - Nome identificativo firma

**Esempi:**
```
Crea una firma con il mio nome, ruolo e foto del profilo
Configura una firma professionale con logo aziendale
```

#### `get_email_signature`
Ottieni la firma email corrente.

**Parametri:**
- `signature_name` (str, default: "default") - Nome firma da recuperare

#### `list_email_signatures`
Elenca tutte le firme email salvate.

### Strumenti Calendario

#### `create_calendar_event`
Crea un nuovo evento calendario.

**Parametri:**
- `summary` (str) - Titolo evento
- `start` (str) - Data/ora inizio in formato ISO (YYYY-MM-DDTHH:MM:SS)
- `end` (str) - Data/ora fine in formato ISO
- `description` (str, opzionale) - Descrizione evento
- `location` (str, opzionale) - Luogo evento
- `attendees` (str, opzionale) - Lista email partecipanti separati da virgola

**Esempi:**
```
Crea un meeting chiamato "Riunione Team" domani alle 15 per 1 ora
Programma un "Project Review" il 10 dicembre alle 14 con john@example.com
```

#### `list_calendar_events`
Elenca eventi calendario in un intervallo di date.

**Parametri:**
- `start_date` (str, opzionale) - Data inizio in formato ISO (default: oggi)
- `end_date` (str, opzionale) - Data fine in formato ISO (default: 30 giorni da ora)
- `limit` (int, default: 50) - Eventi massimi da restituire

**Esempi:**
```
Mostrami il mio calendario per questa settimana
Quali eventi ho a dicembre?
Elenca tutti i miei meeting per i prossimi 7 giorni
```

#### `accept_calendar_event`
Accetta un invito calendario.

**Parametri:**
- `event_uid` (str) - UID dell'evento
- `comment` (str, opzionale) - Commento opzionale

**Esempi:**
```
Accetta l'invito al meeting "Team Standup"
Accetta l'evento abc123@aruba.it con commento "Non vedo l'ora!"
```

#### `decline_calendar_event`
Declina un invito calendario.

**Parametri:**
- `event_uid` (str) - UID dell'evento
- `comment` (str, opzionale) - Commento opzionale

**Esempi:**
```
Declina l'evento abc123@aruba.it
Declina il meeting con commento "Mi dispiace, ho un conflitto"
```

#### `tentative_calendar_event`
Rispondi "forse" a un invito calendario.

**Parametri:**
- `event_uid` (str) - UID dell'evento
- `comment` (str, opzionale) - Commento opzionale

**Esempi:**
```
Rispondi forse all'evento abc123@aruba.it
Segna come "forse" il meeting di domani
Forse partecipo al meeting di domani
```

#### `delete_calendar_event`
Elimina un evento calendario.

**Parametri:**
- `event_uid` (str) - UID dell'evento da eliminare

**Esempi:**
```
Elimina l'evento abc123@aruba.it
Cancella il mio meeting delle 14
```

## Casi d'Uso

### 📬 Comunicazione Team
```
Mostrami le ultime email dai membri del mio team
Elenca email non lette da project@company.com
```

### 🔍 Tracking Progetti
```
Cerca email che menzionano "modifiche API" dall'ultima settimana
Trova tutte le email su "fattura" dal 1° dicembre
```

### 📊 Riepilogo Email Giornaliero
```
Riassumi tutte le email che ho ricevuto oggi
Mostrami le email importanti di stamattina
```

### ✉️ Risposte Rapide
```
Invia un'email a colleague@example.com ringraziandoli per l'aggiornamento
Rispondi a john@example.com con lo stato del progetto
```

### 📅 Gestione Calendario
```
Quali meeting ho questa settimana?
Crea una riunione team per domani alle 15
Accetta l'invito calendario per la review di venerdì
Declina il meeting di lunedì, sono in vacanza
Mostrami il mio programma per la prossima settimana
```

### 🤖 Gestione Email & Calendario con AI
Con Claude Desktop o VS Code Copilot, puoi:
- Chiedere a Claude di riassumere più email
- Creare risposte basate sul contenuto email
- Estrarre task da thread email
- Organizzare e categorizzare email automaticamente
- Programmare meeting basati su conversazioni email
- Gestire conflitti calendario e trovare fasce orarie disponibili

## Stack Tecnologico

- **Python 3.10+** - Python moderno
- **MCP SDK 1.2.0+** - Model Context Protocol per integrazione AI
- **imaplib** - Client IMAP libreria standard (supporto SSL/TLS)
- **smtplib** - Client SMTP libreria standard (supporto SSL/TLS)
- **email** - Parsing email e gestione MIME
- **caldav** - Protocollo CalDAV per accesso calendario
- **icalendar** - Parsing e generazione formato iCalendar
- **python-dotenv** - Gestione variabili ambiente

## Sicurezza & Privacy

- 🔒 **Esecuzione locale** - Il server gira sul tuo computer, le credenziali non lasciano mai la tua macchina
- 🛡️ **Crittografia SSL/TLS** - Tutte le connessioni usano protocolli sicuri (IMAPS porta 993, SMTPS porta 465, HTTPS per CalDAV)
- 🔐 **Variabili ambiente** - Credenziali salvate nel file `.env` (gitignored di default)
- 📝 **Troncamento corpo** - Corpo email limitato a 5000 caratteri per prevenire overflow del contesto
- ✅ **Nessun servizio esterno** - Connessione diretta solo ai server Aruba

### Best Practice Sicurezza

1. Non committare mai il file `.env` nel controllo versione
2. Usa password forti e uniche per il tuo account email
3. Considera l'abilitazione 2FA sul tuo account Aruba
4. Ruota regolarmente le tue credenziali
5. Rivedi i log del server MCP per attività sospette

## Performance

- ⚡ Connection pooling via context manager
- 📊 Limiti risultati configurabili per prevenire problemi di memoria
- 🚀 Connessioni on-demand (nessun processo in background)
- 💾 Footprint di memoria minimo

## Sviluppo

### Eseguire i Test

```bash
# Attiva ambiente virtuale
source .venv/bin/activate

# Esegui test connessione email
python test_connection.py

# Esegui test connessione calendario
python test_calendar.py

# Test creazione evento
python test_create_event.py

# Test invio invito calendario
python send_invite.py
```

### Qualità Codice

```bash
# Formatta codice
black src/

# Type checking
mypy src/

# Linting
pylint src/
```

## Abilitare Sincronizzazione CalDAV

Per usare le funzionalità calendario, devi abilitare la sincronizzazione CalDAV in Aruba Webmail:

1. Vai su https://webmail.aruba.it
2. Naviga alla sezione Calendario
3. Clicca su **"Sincronizza calendario"**
4. Scegli **"Calendari"** → **"Procedi"**
5. Seleziona **"Lettura e modifica"** (CalDAV) → **"Procedi"**
6. Seleziona i calendari da sincronizzare → **"Procedi"**

Una volta abilitato, potrai gestire completamente i tuoi calendari tramite il server MCP!

## Risoluzione Problemi

### Calendario non disponibile

Se vedi "No calendar available", devi abilitare la sincronizzazione CalDAV (vedi sezione sopra).

### Errori connessione

1. Verifica che le credenziali in `.env` siano corrette
2. Controlla che le porte 993 (IMAP), 465 (SMTP), 443 (CalDAV) non siano bloccate
3. Verifica le impostazioni firewall
4. Prova a eseguire gli script di test

### Email o eventi non visualizzati

1. Verifica di avere i permessi corretti sull'account
2. Controlla i filtri applicati (sender_filter, date filters)
3. Aumenta il limite di risultati

## FAQ

**Q: È sicuro memorizzare le mie credenziali nel file .env?**  
A: Sì, finché il file `.env` non viene committato nel controllo versione. È già incluso in `.gitignore`. Le credenziali rimangono sul tuo computer locale.

**Q: Posso usare questo con altri provider email?**  
A: Il server è ottimizzato per Aruba, ma puoi adattarlo per altri provider che supportano IMAP/SMTP/CalDAV modificando le configurazioni.

**Q: Quanto costano i server MCP?**  
A: I server MCP sono gratuiti! Questo è software open-source. Hai solo bisogno di un abbonamento Claude o GitHub Copilot per usarlo con quegli AI.

**Q: I miei dati vengono inviati a terze parti?**  
A: No! Il server gira localmente e si connette direttamente ai server Aruba. Nessun dato passa attraverso servizi terzi.

**Q: Posso contribuire al progetto?**  
A: Assolutamente! Vedi [CONTRIBUTING.md](CONTRIBUTING.md) per linee guida.

## Contribuire

I contributi sono benvenuti! Per favore:

1. Fai un fork del repository
2. Crea un feature branch (`git checkout -b feature/funzionalita-fantastica`)
3. Committa le modifiche (`git commit -m 'Aggiungi funzionalità fantastica'`)
4. Pusha al branch (`git push origin feature/funzionalita-fantastica`)
5. Apri una Pull Request

Vedi [CONTRIBUTING.md](CONTRIBUTING.md) per dettagli completi.

## Roadmap

- [ ] Supporto IMAP IDLE per notifiche real-time
- [ ] Gestione allegati email
- [ ] Composizione email HTML
- [ ] Suite test pytest
- [ ] Supporto account multipli
- [ ] Eventi calendario ricorrenti
- [ ] Notifiche calendario
- [ ] Integrazione con altri calendari (Google Calendar, Outlook)

## Documentazione

- [README.md](README.md) - Documentazione principale (Italiano)
- [README_EN.md](README_EN.md) - Documentation in English
- [EXAMPLES.md](EXAMPLES.md) - Esempi d'uso
- [CLAUDE_SETUP.md](CLAUDE_SETUP.md) - Setup Claude Desktop
- [VSCODE_SETUP.md](VSCODE_SETUP.md) - Setup VS Code Copilot MCP
- [docs/VSCODE_EXTENSION.md](docs/VSCODE_EXTENSION.md) - **Estensione VS Code Marketplace**
- [docs/MCP_REGISTRY.md](docs/MCP_REGISTRY.md) - **Pubblicazione MCP Registry**
- [SIGNATURE_EXAMPLES.md](SIGNATURE_EXAMPLES.md) - Esempi firme email
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guida contribuzioni
- [LICENSE](LICENSE) - Licenza MIT

## Installazione Rapida

### Da PyPI

```bash
pip install mcp-aruba
```

### Da VS Code Marketplace

Cerca "MCP Aruba Email" nel marketplace VS Code o installa direttamente:
```bash
code --install-extension jackfioru92.mcp-aruba-email
```

### Da MCP Registry

Il server è disponibile su [MCP Registry](https://mcpregistry.io/servers/io.github.jackfioru92/aruba-email)

## Supporto

Se incontri problemi:

1. Controlla la sezione [Risoluzione Problemi](#risoluzione-problemi)
2. Esegui gli script di test per verificare la connessione
3. Controlla i log per messaggi d'errore
4. Apri un issue su [GitHub](https://github.com/jackfioru92/mcp-aruba-email/issues)

## Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file [LICENSE](LICENSE) per dettagli.

## Autore

Giacomo Fiorucci - giacomo.fiorucci@emotion-team.com

## Ringraziamenti

- [Model Context Protocol](https://modelcontextprotocol.io/) per il framework MCP
- [Anthropic](https://www.anthropic.com/) per Claude Desktop
- [GitHub](https://github.com/) per Copilot
- Aruba per i servizi email e calendario affidabili

---

⭐ Se questo progetto ti è utile, considera di dargli una stella su GitHub!
