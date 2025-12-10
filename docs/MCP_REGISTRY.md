# MCP Registry - Pubblicazione e Utilizzo

## Cos'è MCP Registry

[MCP Registry](https://mcpregistry.io/) è un registro centralizzato per la pubblicazione e la scoperta di server MCP (Model Context Protocol). Permette agli sviluppatori di condividere i propri server MCP con la community.

## Server Pubblicato

Il nostro server è pubblicato su MCP Registry:

- **Nome**: `io.github.jackfioru92/aruba-email`
- **URL**: https://mcpregistry.io/servers/io.github.jackfioru92/aruba-email
- **Versione**: 0.2.1

## Come Usare il Server da MCP Registry

### 1. Installazione Diretta

Gli utenti possono installare il server direttamente da PyPI:

```bash
pip install mcp-aruba
```

### 2. Configurazione Claude Desktop

Aggiungi al file di configurazione Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json` su macOS):

```json
{
  "mcpServers": {
    "aruba-email": {
      "command": "mcp-aruba",
      "env": {
        "IMAP_HOST": "imaps.pec.aruba.it",
        "IMAP_USERNAME": "tua@pec.it",
        "IMAP_PASSWORD": "password",
        "SMTP_HOST": "smtps.pec.aruba.it",
        "SMTP_USERNAME": "tua@pec.it",
        "SMTP_PASSWORD": "password"
      }
    }
  }
}
```

### 3. Utilizzo con VS Code

Vedi la documentazione [VSCODE_EXTENSION.md](./VSCODE_EXTENSION.md) per l'integrazione con VS Code e GitHub Copilot.

## File server.json

Il file `server.json` nella root del progetto definisce la configurazione per MCP Registry:

```json
{
  "$schema": "https://mcpregistry.io/schemas/server.json",
  "name": "io.github.jackfioru92/aruba-email",
  "version": "0.2.1",
  "description": "MCP Server for Aruba Email (IMAP/SMTP) and Calendar (CalDAV)",
  "publisher": {
    "name": "Giacomo Fiorucci",
    "url": "https://github.com/jackfioru92"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/jackfioru92/mcp_aruba.git"
  },
  "license": "MIT",
  "runtime": {
    "type": "pypi",
    "package": "mcp-aruba"
  },
  "tools": [
    {
      "name": "list_mailboxes",
      "description": "List all mailboxes"
    },
    {
      "name": "list_emails",
      "description": "List emails from a mailbox"
    },
    {
      "name": "read_email",
      "description": "Read a specific email"
    },
    {
      "name": "send_email",
      "description": "Send an email via SMTP"
    },
    {
      "name": "list_calendars",
      "description": "List CalDAV calendars"
    },
    {
      "name": "list_events",
      "description": "List calendar events"
    },
    {
      "name": "create_event",
      "description": "Create a calendar event"
    }
  ],
  "configurationOptions": [
    {
      "name": "IMAP_HOST",
      "description": "IMAP server hostname",
      "required": true,
      "default": "imaps.pec.aruba.it"
    },
    {
      "name": "IMAP_USERNAME",
      "description": "IMAP username (email address)",
      "required": true
    },
    {
      "name": "IMAP_PASSWORD",
      "description": "IMAP password",
      "required": true,
      "secret": true
    },
    {
      "name": "SMTP_HOST",
      "description": "SMTP server hostname",
      "required": false,
      "default": "smtps.pec.aruba.it"
    },
    {
      "name": "SMTP_USERNAME",
      "description": "SMTP username (email address)",
      "required": false
    },
    {
      "name": "SMTP_PASSWORD",
      "description": "SMTP password",
      "required": false,
      "secret": true
    }
  ]
}
```

## Pubblicazione su MCP Registry

### Prerequisiti

1. Account GitHub
2. MCP CLI installato

### Procedura

1. **Installa MCP CLI**:
   ```bash
   npx @anthropic-ai/mcp-registry register
   ```

2. **Autenticazione GitHub**:
   Il comando aprirà il browser per l'autenticazione OAuth con GitHub.

3. **Verifica Proprietà**:
   Il registry verificherà che tu sia il proprietario del repository GitHub.

4. **Pubblicazione**:
   Segui le istruzioni a schermo per completare la pubblicazione.

### Tag di Verifica

Per verificare la proprietà del repository, aggiungi questo tag al README.md:

```markdown
[mcp-name:io.github.jackfioru92/aruba-email]
```

Questo tag (che può essere nascosto come commento HTML) permette al registry di verificare che tu controlli il repository.

## Aggiornamento del Server

Per pubblicare una nuova versione:

1. Aggiorna la versione in `pyproject.toml`
2. Pubblica su PyPI: `python -m build && twine upload dist/*`
3. Aggiorna `server.json` con la nuova versione
4. Ri-registra su MCP Registry

## Link Utili

- [MCP Registry](https://mcpregistry.io/)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [Anthropic MCP SDK](https://github.com/anthropics/anthropic-sdk-python)
- [Server su MCP Registry](https://mcpregistry.io/servers/io.github.jackfioru92/aruba-email)
