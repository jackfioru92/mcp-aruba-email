# Guida: Come Vedere le Ultime Email

Questa guida spiega come utilizzare il server MCP Aruba per visualizzare le ultime email ricevute.

## 🚀 Metodi Disponibili

### 1. Utilizzo con Claude Desktop (Consigliato)

Una volta configurato il server MCP con Claude Desktop (vedi [CLAUDE_SETUP.md](CLAUDE_SETUP.md)), puoi semplicemente chiedere:

```
Mostrami le ultime 5 email
Dammi le email più recenti
Elenca le ultime 10 email dalla mia inbox
Quali sono le mie email recenti?
```

Claude utilizzerà automaticamente il tool `list_emails` per mostrarti le email.

**Esempio di conversazione:**
```
Tu: Mostrami le ultime 5 email

Claude: Ecco le tue ultime 5 email:

1. Da: mario.rossi@example.com
   Oggetto: Riunione di domani
   Data: 5 Dic 2024, 14:30
   Anteprima: Ciao, volevo confermare la riunione di domani alle...

2. Da: info@newsletter.com
   Oggetto: Newsletter Settimanale
   Data: 5 Dic 2024, 09:00
   Anteprima: Ecco le novità della settimana...

[...]
```

### 2. Utilizzo con VS Code Copilot

Con l'estensione Copilot MCP (vedi [VSCODE_SETUP.md](VSCODE_SETUP.md)), puoi chiedere:

```
@workspace mostrami le ultime email
@workspace dammi le 10 email più recenti
```

### 3. Utilizzo della CLI

Il modo più veloce per vedere le email direttamente da terminale:

```bash
# Attiva l'ambiente virtuale
source .venv/bin/activate  # Su Windows: .venv\Scripts\activate

# Mostra le ultime 5 email (default)
python cli.py emails

# Mostra le ultime 10 email
python cli.py emails 10

# Mostra le ultime 20 email
python cli.py emails 20
```

**Output della CLI:**
```
📧 Ultime 5 email:

================================================================================

1. ID: 12345
   Da: mario.rossi@example.com
   Oggetto: Riunione di domani
   Data: Thu, 5 Dec 2024 14:30:00 +0100
   Anteprima: Ciao, volevo confermare la riunione di domani alle 10:00. Ci vediamo in sala riunioni A...
--------------------------------------------------------------------------------

2. ID: 12344
   Da: laura.bianchi@example.com
   Oggetto: Report mensile
   Data: Thu, 5 Dec 2024 12:15:00 +0100
   Anteprima: Allego il report mensile delle attività. Come puoi vedere, abbiamo raggiunto tutti gli...
--------------------------------------------------------------------------------

[...]
```

### 4. Utilizzo Programmatico (Python)

Puoi utilizzare direttamente il client email nel tuo codice Python:

```python
from src.mcp_aruba.email_client import ArubaEmailClient
from dotenv import load_dotenv
import os

load_dotenv()

# Crea il client
with ArubaEmailClient(
    host=os.getenv('IMAP_HOST'),
    port=int(os.getenv('IMAP_PORT')),
    username=os.getenv('IMAP_USERNAME'),
    password=os.getenv('IMAP_PASSWORD')
) as client:
    # Ottieni le ultime 5 email
    emails = client.list_emails(limit=5)
    
    # Stampa le email
    for email in emails:
        print(f"Da: {email['from']}")
        print(f"Oggetto: {email['subject']}")
        print(f"Data: {email['date']}")
        print(f"Anteprima: {email['body'][:100]}...")
        print("-" * 50)
```

## 🎯 Casi d'Uso Avanzati

### Filtrare per Mittente

**Con Claude/Copilot:**
```
Mostrami le ultime email da mario.rossi@example.com
Dammi tutte le email recenti da denisa@c-tic.it
```

**In Python:**
```python
emails = client.list_emails(
    sender_filter="mario.rossi@example.com",
    limit=10
)
```

### Cercare Email per Contenuto

**Con Claude/Copilot:**
```
Cerca email che parlano di "fattura"
Trova email con "API" nell'oggetto o nel corpo
Cerca email su "progetto X" dalla settimana scorsa
```

**In Python:**
```python
emails = client.search_emails(
    query="fattura",
    from_date="01-Dec-2024",
    limit=10
)
```

### Leggere il Contenuto Completo

Dopo aver ottenuto la lista delle email, puoi leggere il contenuto completo:

**Con Claude/Copilot:**
```
Leggi l'email con ID 12345
Mostrami il contenuto completo dell'ultima email
```

**In Python:**
```python
email_content = client.read_email(email_id="12345")
print(email_content['body'])
```

## ⚙️ Configurazione

Prima di utilizzare qualsiasi metodo, assicurati di aver configurato le credenziali:

1. Copia `.env.example` in `.env`
2. Modifica `.env` con le tue credenziali Aruba:

```env
IMAP_HOST=imaps.aruba.it
IMAP_PORT=993
IMAP_USERNAME=tuo_email@aruba.it
IMAP_PASSWORD=tua_password
```

## 🔍 Tool MCP Disponibili

Il server MCP espone questi strumenti per gestire le email:

### `list_emails`
Elenca le email più recenti dalla casella di posta.

**Parametri:**
- `folder` (str, default: "INBOX") - Cartella da cui leggere
- `sender_filter` (str, opzionale) - Filtra per mittente
- `limit` (int, default: 10, max: 50) - Numero massimo di email

### `read_email`
Legge il contenuto completo di un'email specifica.

**Parametri:**
- `email_id` (str) - ID dell'email da leggere
- `folder` (str, default: "INBOX") - Cartella

### `search_emails`
Cerca email per oggetto o contenuto.

**Parametri:**
- `query` (str) - Testo da cercare
- `folder` (str, default: "INBOX") - Cartella
- `from_date` (str, opzionale) - Data di inizio (formato: DD-MMM-YYYY)
- `limit` (int, default: 10, max: 50) - Numero massimo di risultati

## 🐛 Risoluzione Problemi

### "Credenziali non configurate"
Assicurati di aver creato il file `.env` con le tue credenziali Aruba.

### "Connessione fallita"
- Verifica che le credenziali siano corrette
- Controlla che le porte 993 (IMAP) non siano bloccate dal firewall
- Prova a eseguire `python test_connection.py` per diagnosticare il problema

### "Nessuna email trovata"
- Verifica di avere email nella cartella INBOX
- Controlla che i filtri applicati (sender_filter, date filter) non siano troppo restrittivi
- Aumenta il limite: `limit=50`

## 📚 Risorse Aggiuntive

- [README.md](README.md) - Documentazione completa del progetto
- [EXAMPLES.md](EXAMPLES.md) - Altri esempi d'uso
- [CLAUDE_SETUP.md](CLAUDE_SETUP.md) - Configurazione con Claude Desktop
- [VSCODE_SETUP.md](VSCODE_SETUP.md) - Configurazione con VS Code Copilot

## 💡 Suggerimenti

1. **Usa la CLI per test rapidi**: È il modo più veloce per verificare la connessione e vedere le email
2. **Sfrutta Claude/Copilot per elaborazioni complesse**: Puoi chiedere riassunti, traduzioni, o estrazioni di informazioni dalle email
3. **Limita i risultati**: Usa `limit` appropriato per evitare di scaricare troppe email in una volta
4. **Salva l'ID**: Ogni email ha un ID univoco che puoi usare per leggerla successivamente

---

**Nota**: Tutte le operazioni sono sicure e avvengono localmente. Le credenziali non lasciano mai il tuo computer e la connessione ai server Aruba avviene tramite SSL/TLS.
