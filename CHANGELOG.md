# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.2] - 2026-02-16

### Added
- Conversione HTML-to-text per email più leggibili usando `html2text`
- Dipendenza `html2text>=2024.2.26`

### Changed
- `_parse_email()` ora preferisce conversione HTML rispetto a text/plain auto-generato
- Email newsletter e transazionali ora mostrano testo pulito senza artefatti tabelle

### Fixed
- Risolto problema email HTML illeggibili con tag raw e layout tabelle

## [0.2.1] - 2025-01-15

### Added
- Estensione VS Code pubblicata su Marketplace
- Supporto completo per GitHub Copilot
- Configurazione credenziali tramite keychain sistema
- Comandi VS Code per gestione credenziali
- Documentazione estensione VS Code
- File `server.json` per registro MCP
- `.well-known/mcp/server-card.json` per Smithery

### Changed
- Migliorata documentazione installazione
- Aggiornato README con sezioni installazione multiple

### Fixed
- Gestione errori connessione IMAP migliorata

## [0.2.0] - 2025-01-10

### Added
- Sistema completo di firme email
- Upload automatico foto su Imgur
- Firme HTML con stili personalizzabili
- Script interattivo per setup firma (`setup_signature.py`)
- Supporto colori brand nelle firme
- Funzioni calendario: accetta/declina/tentative inviti
- Gestione completa eventi CalDAV
- Documentazione esempi firme (`SIGNATURE_EXAMPLES.md`)

### Changed
- Refactoring `signature.py` per migliore organizzazione
- Migliorata gestione errori CalDAV

### Fixed
- Bug parsing date eventi calendario
- Gestione timeout connessione IMAP

## [0.1.5] - 2024-12-20

### Added
- Supporto CalDAV per gestione calendario
- Funzioni lista eventi calendario
- Funzioni creazione eventi
- Eliminazione eventi calendario
- Documentazione calendario

### Changed
- Ristrutturato modulo email_client per migliore manutenibilità

## [0.1.0] - 2024-12-01

### Added
- Server MCP base con supporto IMAP/SMTP
- Funzioni lista email
- Funzioni lettura email
- Funzioni ricerca email
- Funzioni invio email
- Supporto variabili d'ambiente
- Documentazione base
- Esempi utilizzo
- File LICENSE (MIT)
- README in italiano e inglese

### Security
- Gestione sicura credenziali tramite .env

## [0.0.1] - 2024-11-15

### Added
- Setup iniziale progetto
- Struttura base directory
- pyproject.toml
- Primo commit

---

## Types of Changes

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for soon-to-be removed features.
- `Removed` for now removed features.
- `Fixed` for any bug fixes.
- `Security` in case of vulnerabilities.

[Unreleased]: https://github.com/jackfioru92/mcp-aruba-email/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/jackfioru92/mcp-aruba-email/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/jackfioru92/mcp-aruba-email/compare/v0.1.5...v0.2.0
[0.1.5]: https://github.com/jackfioru92/mcp-aruba-email/compare/v0.1.0...v0.1.5
[0.1.0]: https://github.com/jackfioru92/mcp-aruba-email/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/jackfioru92/mcp-aruba-email/releases/tag/v0.0.1
