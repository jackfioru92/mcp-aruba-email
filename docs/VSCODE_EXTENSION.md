# Aruba Email MCP Server - VS Code Extension

Questa guida spiega come installare e configurare l'estensione VS Code per il server MCP Aruba Email.

## 📦 Installazione

### Da VS Code Marketplace (Consigliato)

1. Apri VS Code
2. Premi `⌘+Shift+X` (macOS) o `Ctrl+Shift+X` (Windows/Linux)
3. Cerca **"Aruba Email MCP Server"** o **"jackfioru92.mcp-aruba-email"**
4. Clicca **Install**

### Da Open VSX (VSCodium, Cursor, ecc.)

1. Apri il marketplace delle estensioni
2. Cerca **"Aruba Email MCP Server"**
3. Clicca **Install**

Link diretto: https://open-vsx.org/extension/jackfioru92/mcp-aruba-email

### Da VSIX (Installazione Manuale)

1. Scarica il file `.vsix` dalle [releases GitHub](https://github.com/jackfioru92/mcp-aruba-email/releases)
2. In VS Code: `⌘+Shift+P` → **"Extensions: Install from VSIX..."**
3. Seleziona il file `.vsix` scaricato

## ⚙️ Configurazione

### Configurazione Iniziale

1. Premi `⌘+Shift+P` (Command Palette)
2. Digita **"Aruba Email: Configure Credentials"**
3. Inserisci:
   - **Email Aruba**: la tua email (es. `nome@aruba.it`)
   - **Password**: la password dell'account email
   - **Imgur Client ID** (opzionale): per le foto nelle firme email

### Impostazioni Avanzate

L'estensione supporta le seguenti impostazioni in `settings.json`:

```json
{
  "mcpArubaEmail.emailAddress": "tua@email.aruba.it",
  "mcpArubaEmail.imapHost": "imaps.aruba.it",
  "mcpArubaEmail.imapPort": 993,
  "mcpArubaEmail.smtpHost": "smtps.aruba.it",
  "mcpArubaEmail.smtpPort": 465,
  "mcpArubaEmail.caldavUrl": "https://syncdav.aruba.it/calendars/tua@email.aruba.it/",
  "mcpArubaEmail.calendarEnabled": true
}
```

### Dove viene salvata la password?

La password viene salvata in modo sicuro usando il **keychain di sistema** (Keychain su macOS, Credential Manager su Windows, libsecret su Linux) tramite la libreria `keytar`.

## 🚀 Utilizzo con GitHub Copilot

Una volta configurata l'estensione, il server MCP sarà disponibile automaticamente in GitHub Copilot Chat.

### Aprire Copilot Chat

1. Clicca sull'icona 💬 nella sidebar sinistra
2. Oppure premi `⌘+Shift+I`

### Esempi di Comandi

Nella chat di Copilot, puoi chiedere:

#### Email
- *"Mostrami le ultime 10 email"*
- *"Cerca email da mario.rossi@example.com"*
- *"Leggi l'email con oggetto 'Riunione'"*
- *"Invia un'email a info@azienda.it con oggetto 'Preventivo'"*

#### Calendario
- *"Quali eventi ho oggi?"*
- *"Crea un evento 'Riunione Team' per domani alle 15:00"*
- *"Mostra gli eventi della prossima settimana"*
- *"Accetta l'invito alla riunione di venerdì"*

#### Firme
- *"Crea una firma email professionale"*
- *"Imposta la firma con nome 'Mario Rossi' e ruolo 'Sviluppatore'"*

## 🔧 Comandi Disponibili

| Comando | Descrizione |
|---------|-------------|
| `Aruba Email: Configure Credentials` | Configura email e password |
| `Aruba Email: Test Connection` | Verifica la connessione al server |

## 🐛 Risoluzione Problemi

### L'estensione non si attiva

1. Verifica che VS Code sia aggiornato (≥ 1.101.0)
2. Riavvia VS Code
3. Controlla la console sviluppatore: `Help → Toggle Developer Tools`

### Errore "uvx command not found"

L'estensione usa `uvx` per eseguire il server Python. Installa `uv`:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# oppure con Homebrew
brew install uv
```

### Errore di connessione IMAP

1. Verifica le credenziali: `⌘+Shift+P` → "Aruba Email: Configure Credentials"
2. Controlla che l'host IMAP sia corretto: `imaps.aruba.it`
3. Verifica che la porta sia `993`

### Il server MCP non appare in Copilot

1. Assicurati di aver configurato le credenziali
2. Riavvia VS Code dopo la configurazione
3. Verifica che GitHub Copilot sia attivo

## 📊 Architettura

```
┌─────────────────────────────────────────────────────────────┐
│                      VS Code                                 │
│  ┌─────────────┐    ┌──────────────────┐    ┌────────────┐ │
│  │  Copilot    │◄──►│  MCP Extension   │◄──►│   keytar   │ │
│  │   Chat      │    │  (TypeScript)    │    │ (password) │ │
│  └─────────────┘    └────────┬─────────┘    └────────────┘ │
│                              │                              │
└──────────────────────────────┼──────────────────────────────┘
                               │ stdio
                               ▼
                    ┌──────────────────┐
                    │   uvx mcp-aruba  │
                    │     (Python)     │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌─────────┐    ┌─────────┐    ┌─────────┐
        │  IMAP   │    │  SMTP   │    │ CalDAV  │
        │ Server  │    │ Server  │    │ Server  │
        └─────────┘    └─────────┘    └─────────┘
           Aruba          Aruba         Aruba
```

## 🔗 Link Utili

- **VS Code Marketplace**: https://marketplace.visualstudio.com/items?itemName=jackfioru92.mcp-aruba-email
- **Open VSX**: https://open-vsx.org/extension/jackfioru92/mcp-aruba-email
- **PyPI**: https://pypi.org/project/mcp-aruba/
- **GitHub**: https://github.com/jackfioru92/mcp-aruba-email
- **MCP Registry**: `io.github.jackfioru92/aruba-email`

## 📄 Licenza

MIT License - Vedi [LICENSE](../LICENSE)
