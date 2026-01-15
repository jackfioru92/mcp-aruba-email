# Checklist per Pubblicazione su Smithery

## ✅ Prerequisiti (Da Verificare)

- [x] Package pubblicato su PyPI come `mcp-aruba`
- [x] Repository pubblico su GitHub
- [x] File `server.json` nella root del progetto
- [x] Estensione VS Code pubblicata
- [x] Loggato su Smithery ✅ **FATTO**
- [ ] Server registrato su Smithery 🔄 **IN CORSO**

## 🎯 Passi per Pubblicare su Smithery

### 1. Verifica File server.json

- [ ] Schema corretto: `https://static.modelcontextprotocol.io/schemas/2025-10-17/server.schema.json`
- [ ] Nome univoco: `io.github.jackfioru92/aruba-email`
- [ ] Versione corretta: `0.2.1` (deve corrispondere a PyPI)
- [ ] URL repository corretto
- [ ] Variabili d'ambiente definite correttamente

### 2. Accedi a Smithery

1. Vai su https://smithery.ai
2. Clicca "Sign in with GitHub"
3. Autorizza l'accesso al repository `mcp-aruba-email`

### 3. Pubblica il Server

**Via Web UI (Più Semplice)**:
1. Clicca "Publish Server" su Smithery
2. Inserisci URL: `https://github.com/jackfioru92/mcp-aruba-email`
3. Smithery leggerà automaticamente `server.json`
4. Conferma la pubblicazione

**Oppure via CLI**:
```bash
npm install -g @smithery/cli
smithery login
smithery publish
```

### 4. Verifica Pubblicazione

- [ ] Server visibile su: https://smithery.ai/server/io.github.jackfioru92/aruba-email
- [ ] Server trovabile cercando "aruba" su Smithery
- [ ] Documentazione visibile correttamente
- [ ] Link a PyPI funzionante

### 5. Testa in VS Code

- [ ] Apri GitHub Copilot Chat
- [ ] Digita `@mcp aruba`
- [ ] Il server appare nei suggerimenti
- [ ] L'installazione funziona correttamente

### 6. Aggiorna Documentazione

- [ ] Aggiungi badge Smithery al README:
  ```markdown
  [![Smithery](https://smithery.ai/badge/io.github.jackfioru92/aruba-email)](https://smithery.ai/server/io.github.jackfioru92/aruba-email)
  ```
- [ ] Aggiorna sezione "Installazione" nel README
- [ ] Rimuovi nota "Coming Soon" dal README
- [ ] Aggiorna `docs/VSCODE_EXTENSION.md` con istruzioni @mcp

### 7. Annuncia la Pubblicazione

- [ ] Post su GitHub Discussions
- [ ] Aggiorna GitHub Release notes
- [ ] Menziona nei social/community MCP

## 🔄 Per Aggiornamenti Futuri

Quando rilasci una nuova versione:

1. Aggiorna versione in `pyproject.toml`
2. Aggiorna versione in `server.json`
3. Pubblica su PyPI:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```
4. Crea tag Git:
   ```bash
   git tag v0.2.2
   git push origin v0.2.2
   ```
5. Smithery aggiornerà automaticamente! 🎉

## ⚠️ Note Importanti

- **Versione**: La versione in `server.json` DEVE corrispondere a quella su PyPI
- **Nome Package**: Deve essere esattamente `mcp-aruba` (come su PyPI)
- **Repository**: Deve essere pubblico e accessibile
- **Schema**: Usa sempre l'ultimo schema MCP disponibile

## 📚 Risorse

- Smithery: https://smithery.ai
- Documentazione MCP: https://modelcontextprotocol.io
- Guida dettagliata: [docs/MCP_SMITHERY_PUBLISH.md](docs/MCP_SMITHERY_PUBLISH.md)

## 🆘 Troubleshooting

### Problema: "Server not found"
**Soluzione**: Verifica che `server.json` sia nella root e che il repository sia pubblico

### Problema: "Version mismatch"
**Soluzione**: Sincronizza versioni in `pyproject.toml`, `server.json` e PyPI

### Problema: "@mcp aruba non funziona"
**Soluzione**: Serve tempo per l'indicizzazione. Aspetta 10-15 minuti dopo la pubblicazione.

---

**Prossimo Passo**: Vai su https://smithery.ai e pubblica il server! 🚀
