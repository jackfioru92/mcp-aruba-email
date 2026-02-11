# Troubleshooting - MCP Aruba Email

## Problema: "command 'mcp-aruba-email.configure' not found"

### Sintomo
Quando provi a eseguire il comando **"Aruba Email: Configure Credentials"** dalla Command Palette, ricevi l'errore:
```
command 'mcp-aruba-email.configure' not found
```

### Cause possibili
1. L'estensione non è installata correttamente
2. Stai usando una versione vecchia dell'estensione
3. VS Code non ha caricato l'estensione correttamente

### Soluzione 1: Reinstalla l'estensione (CONSIGLIATO)

1. **Disinstalla la versione attuale**
   - Apri VS Code
   - Vai nelle Extensions (Cmd+Shift+X / Ctrl+Shift+X)
   - Cerca "Aruba Email MCP Server"
   - Clicca con il tasto destro → Uninstall

2. **Installa l'ultima versione**
   - Scarica il file `mcp-aruba-email-0.2.3.vsix` dalla cartella `vscode-extension/`
   - In VS Code, apri Command Palette (Cmd+Shift+P / Ctrl+Shift+P)
   - Digita: `Extensions: Install from VSIX...`
   - Seleziona il file `mcp-aruba-email-0.2.3.vsix`
   - Riavvia VS Code

3. **Verifica l'installazione**
   - Apri Command Palette (Cmd+Shift+P / Ctrl+Shift+P)
   - Cerca: `Aruba Email: Configure Credentials`
   - Il comando dovrebbe apparire

### Soluzione 2: Ricarica VS Code

Se l'estensione è già installata, prova a ricaricare la finestra:
- Apri Command Palette (Cmd+Shift+P / Ctrl+Shift+P)
- Digita: `Developer: Reload Window`
- Premi Invio

### Soluzione 3: Controlla i log

Se il problema persiste, controlla i log:
1. Apri Output Panel: `View → Output`
2. Seleziona "Extension Host" dal dropdown
3. Cerca messaggi di errore relativi a `mcp-aruba-email`

### Dopo la configurazione

Una volta che il comando funziona correttamente:

1. **Configura le credenziali**
   - Command Palette → `Aruba Email: Configure Credentials`
   - Inserisci email Aruba: `tuo@email.it`
   - Inserisci password
   - (Opzionale) Inserisci Imgur Client ID per le foto nelle firme

2. **Testa la connessione**
   - Command Palette → `Aruba Email: Test Connection`

3. **Usa in GitHub Copilot Chat**
   - Apri GitHub Copilot Chat
   - L'MCP Server "Aruba Email" sarà disponibile automaticamente
   - Puoi chiedere: "List my emails" o "Send an email to..."

## Altri problemi comuni

### Il server MCP non appare in GitHub Copilot Chat

**Verifica:**
1. Le credenziali sono configurate correttamente
2. GitHub Copilot Chat è abilitato
3. Hai riavviato VS Code dopo l'installazione

**Soluzione:**
- Ricarica la finestra: `Developer: Reload Window`
- Controlla le impostazioni: `Preferences → Settings → mcp aruba`

### Errore di autenticazione con Aruba

**Verifica:**
1. Email e password sono corretti
2. Hai abilitato l'accesso IMAP/SMTP nel tuo account Aruba
3. Non hai 2FA abilitato (o usa una password per app)

**Soluzione:**
- Riconfigura: `Aruba Email: Configure Credentials`
- Controlla su webmail.aruba.it le impostazioni account

### L'estensione non si attiva

**Verifica:**
1. Versione VS Code >= 1.101.0
2. L'estensione è abilitata nelle Extensions
3. Non ci sono conflitti con altre estensioni MCP

**Soluzione:**
- Aggiorna VS Code all'ultima versione
- Disabilita temporaneamente altre estensioni MCP
- Controlla: `Help → Toggle Developer Tools → Console`

## Supporto

Se hai ancora problemi:
1. Crea un issue su GitHub: https://github.com/jackfioru92/mcp-aruba-email/issues
2. Includi:
   - Versione VS Code
   - Versione estensione (0.2.3)
   - Sistema operativo
   - Log di errore completo

## File utili

- Extension: `vscode-extension/mcp-aruba-email-0.2.3.vsix`
- README: `vscode-extension/README.md`
- Setup Guide: `VSCODE_SETUP.md`
