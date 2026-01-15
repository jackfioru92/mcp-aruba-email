# Pubblicazione su Smithery (Registro MCP)

## Cos'è Smithery?

**Smithery** (https://smithery.ai) è il registro ufficiale per server MCP. Una volta pubblicato su Smithery, il tuo server diventerà scopribile con `@mcp aruba` in VS Code, Claude Desktop e altri client MCP.

## Differenza tra Estensione VS Code e Server MCP

| Componente | Cosa fa | Come si usa |
|------------|---------|-------------|
| **Estensione VS Code** | Integra il server MCP con VS Code e GitHub Copilot | Installa da VS Code Marketplace |
| **Server MCP su Smithery** | Rende il server scopribile e installabile ovunque | Usa `@mcp aruba` o installa da Smithery |

**Attualmente**: Avete solo l'estensione VS Code ✅  
**Manca**: Pubblicazione su Smithery ❌

## Come Pubblicare su Smithery

### 1. Prerequisiti

- Account GitHub
- Package pubblicato su PyPI (✅ già fatto: `mcp-aruba`)
- Repository pubblico (✅ già fatto)

### 2. Prepara il file server.json

Il file `server.json` nella root del progetto definisce la configurazione per Smithery. Verifica che sia corretto:

```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-10-17/server.schema.json",
  "name": "io.github.jackfioru92/aruba-email",
  "title": "Aruba Email & Calendar",
  "description": "MCP server for Aruba email and calendar via IMAP/SMTP/CalDAV",
  "repository": {
    "url": "https://github.com/jackfioru92/mcp-aruba-email",
    "source": "github"
  },
  "version": "0.2.1",
  "packages": [
    {
      "registryType": "pypi",
      "identifier": "mcp-aruba",
      "version": "0.2.1",
      "transport": {
        "type": "stdio"
      },
      "environmentVariables": [
        {
          "name": "EMAIL_USER",
          "description": "Your Aruba email address",
          "isRequired": true,
          "format": "string",
          "isSecret": false
        },
        {
          "name": "EMAIL_PASSWORD",
          "description": "Your Aruba email password",
          "isRequired": true,
          "format": "string",
          "isSecret": true
        }
      ]
    }
  ]
}
```

### 3. Pubblica su Smithery

#### Opzione A: Tramite GitHub (Consigliato)

1. Vai su https://smithery.ai
2. Clicca **"Sign in with GitHub"**
3. Autorizza Smithery ad accedere al tuo repository
4. Clicca **"Publish Server"**
5. Inserisci l'URL del repository: `https://github.com/jackfioru92/mcp-aruba-email`
6. Smithery leggerà automaticamente il `server.json` e pubblicherà il server

#### Opzione B: Tramite CLI Smithery

```bash
# Installa la CLI di Smithery
npm install -g @smithery/cli

# Accedi
smithery login

# Pubblica il server
smithery publish

# Verifica la pubblicazione
smithery info io.github.jackfioru92/aruba-email
```

### 4. Verifica la Pubblicazione

Dopo la pubblicazione, il tuo server sarà visibile su:
- https://smithery.ai/server/io.github.jackfioru92/aruba-email

## Utilizzo Post-Pubblicazione

### Da VS Code con @mcp

1. Apri GitHub Copilot Chat in VS Code
2. Digita: `@mcp aruba`
3. Il server apparirà nei suggerimenti!
4. Installalo seguendo le istruzioni

### Da Claude Desktop

Aggiungi al file di configurazione (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "aruba-email": {
      "command": "mcp-aruba",
      "env": {
        "EMAIL_USER": "tua@email.aruba.it",
        "EMAIL_PASSWORD": "password"
      }
    }
  }
}
```

### Installazione Diretta

Gli utenti possono installare direttamente:

```bash
# Via pip
pip install mcp-aruba

# Via smithery CLI
smithery install io.github.jackfioru92/aruba-email
```

## Aggiornamento Versioni

Quando rilasci una nuova versione:

1. Aggiorna la versione in `pyproject.toml`
2. Aggiorna la versione in `server.json`
3. Pubblica su PyPI:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```
4. Crea un nuovo tag Git:
   ```bash
   git tag v0.2.2
   git push origin v0.2.2
   ```
5. Smithery rileverà automaticamente la nuova versione dal repository

## Badge per README

Dopo la pubblicazione, aggiungi questi badge al README:

```markdown
[![Smithery](https://smithery.ai/badge/io.github.jackfioru92/aruba-email)](https://smithery.ai/server/io.github.jackfioru92/aruba-email)
[![Install with Smithery](https://smithery.ai/badge/@smithery/install?server=io.github.jackfioru92/aruba-email)](https://smithery.ai/server/io.github.jackfioru92/aruba-email)
```

## Troubleshooting

### "Server not found in Smithery"

- Verifica che il `server.json` sia nella root del repository
- Controlla che il repository sia pubblico
- Assicurati che lo schema JSON sia valido

### "Version mismatch"

- La versione in `server.json` deve corrispondere a quella su PyPI
- Aggiorna entrambi i file e republica

### "Package not found on PyPI"

- Verifica che il package `mcp-aruba` sia pubblicato su PyPI
- Controlla che il nome nel `server.json` corrisponda

## Risorse

- Smithery: https://smithery.ai
- MCP Documentation: https://modelcontextprotocol.io
- MCP Schema: https://github.com/modelcontextprotocol/specification/tree/main/schema
