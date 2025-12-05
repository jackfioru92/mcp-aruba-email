# Email Signature Examples

Esempi pratici di utilizzo del sistema di firme email.

## Quick Start

### Setup Firma Interattivo

```bash
python setup_signature.py
```

Segui le istruzioni interattive per configurare:
- Nome, ruolo, azienda, contatti
- Stile (professional, minimal, colorful)
- Colore principale (#1ca2c8)
- Foto profilo (percorso file o URL)

### Esempio di Setup Completo

```
Nome completo: Giacomo Fiorucci
Ruolo/Posizione: Software Developer
Azienda: Emotion Team
Email: giacomo.fiorucci@emotion-team.com
Telefono: +39 123 456 7890
Sito web: https://emotion-team.com

Stile: 1 (Professional)
Colore principale: #1ca2c8

Percorso foto: /Users/giacomo/Desktop/profile.jpg
```

## Uso Programmatico

### Creare una Firma via Codice

```python
from src.mcp_aruba.signature import create_default_signature, save_signature

# Firma con tutti i dettagli
signature = create_default_signature(
    name='Giacomo Fiorucci',
    email='giacomo.fiorucci@emotion-team.com',
    role='Software Developer',
    company='Emotion Team',
    phone='+39 123 456 7890',
    website='https://emotion-team.com',
    photo_input='/path/to/photo.jpg',  # o URL diretto
    style='professional',
    color='#1ca2c8'
)

# Salva come firma predefinita
save_signature(signature, 'default')
```

### Firma Minimal Senza Foto

```python
signature = create_default_signature(
    name='Mario Rossi',
    email='mario.rossi@example.com',
    role='CEO',
    company='Example Inc',
    style='minimal',
    color='#333333'
)

save_signature(signature, 'minimal-signature')
```

### Firma Colorful per Marketing

```python
signature = create_default_signature(
    name='Laura Bianchi',
    email='laura@marketing.com',
    role='Marketing Manager',
    company='Creative Agency',
    phone='+39 333 123 4567',
    website='https://creative-agency.com',
    photo_input='https://example.com/laura.jpg',
    style='colorful',
    color='#FF6B6B'
)

save_signature(signature, 'marketing')
```

## Gestione Firme Multiple

### Creare Firme per Diversi Contesti

```python
from src.mcp_aruba.signature import (
    create_default_signature, 
    save_signature,
    get_signature,
    list_signatures
)

# Firma formale per clienti
formal = create_default_signature(
    name='Dott. Giovanni Verdi',
    email='g.verdi@studio.com',
    role='Consulente Legale',
    company='Studio Legale Verdi',
    phone='+39 06 1234567',
    style='professional',
    color='#1a237e'
)
save_signature(formal, 'formal')

# Firma casual per colleghi
casual = create_default_signature(
    name='Giovanni',
    email='giovanni@studio.com',
    style='minimal',
    color='#0066cc'
)
save_signature(casual, 'casual')

# Lista tutte le firme disponibili
signatures = list_signatures()
print(f"Firme disponibili: {signatures}")

# Recupera una firma specifica
my_signature = get_signature('formal')
```

## Invio Email con Firma

### Usando il Client Email

```python
from src.mcp_aruba.email_client import ArubaEmailClient
import os

client = ArubaEmailClient(
    host='imaps.aruba.it',
    port=993,
    username=os.getenv('IMAP_USERNAME'),
    password=os.getenv('IMAP_PASSWORD'),
    smtp_host='smtps.aruba.it',
    smtp_port=465
)

# Invia con firma predefinita (automatica)
client.send_email(
    to='cliente@example.com',
    subject='Proposta Progetto',
    body='Buongiorno,\n\nAllego la proposta per il progetto discusso.',
    use_signature=True  # default
)

# Invia senza firma
client.send_email(
    to='interno@example.com',
    subject='Nota veloce',
    body='Quick note...',
    use_signature=False
)
```

### Via MCP Tool (Claude/AI)

```
# Claude comprende richieste in linguaggio naturale:

"Invia un'email a john@example.com con oggetto 'Meeting Follow-up' 
 e includi la mia firma professionale"

"Scrivi a maria@client.com ringraziando per la collaborazione, 
 usa la firma formale"
```

## Personalizzazione Avanzata

### Colori Brand Comuni

```python
# Tech / Modern
color='#0066cc'  # Blu Microsoft
color='#1DA1F2'  # Blu Twitter
color='#0077B5'  # Blu LinkedIn

# Business / Corporate
color='#1a237e'  # Blu scuro professionale
color='#333333'  # Grigio scuro
color='#2c3e50'  # Blu-grigio

# Creative / Marketing
color='#FF6B6B'  # Rosso corallo
color='#4ECDC4'  # Turchese
color='#F7B731'  # Giallo oro

# Custom Brand
color='#1ca2c8'  # Emotion Team azzurro
```

### Upload Foto Automatico

Quando fornisci un percorso file locale:

```python
# La foto viene automaticamente caricata su Imgur
signature = create_default_signature(
    name='Test User',
    email='test@example.com',
    photo_input='/Users/test/Desktop/photo.jpg',  # File locale
    # ...
)
# Il sistema:
# 1. Legge il file locale
# 2. Converte in base64
# 3. Upload su Imgur API
# 4. Usa URL pubblico nella firma
```

Formati supportati:
- `.jpg`, `.jpeg` - JPEG images
- `.png` - PNG images
- `.gif` - GIF images
- `.webp` - WebP images

### Stili Disponibili

**Professional** (Consigliato)
- Bordo colorato superiore
- Foto circolare con bordo
- Layout pulito a 2 colonne
- Nome in grassetto colorato

**Minimal**
- Design essenziale
- Meno elementi decorativi
- Focus su informazioni

**Colorful**
- Più uso del colore
- Elementi grafici vivaci
- Ideale per creative industries

## Storage e Privacy

### Dove Vengono Salvate le Firme

```bash
# macOS/Linux
~/.config/mcp_aruba/signature.json

# Windows
%USERPROFILE%\.config\mcp_aruba\signature.json
```

### Formato Storage

```json
{
  "default": "<div style=\"...\">...</div>",
  "formal": "<div style=\"...\">...</div>",
  "casual": "Plain text signature"
}
```

### Gestione File

```python
from src.mcp_aruba.signature import delete_signature

# Elimina una firma
delete_signature('old-signature')

# Elimina firma predefinita
delete_signature('default')
```

### Privacy e Sicurezza

- ✅ File salvato localmente (mai condiviso)
- ✅ `.gitignore` previene commit accidentali
- ✅ Foto caricate su Imgur (servizio pubblico affidabile)
- ⚠️ Imgur URL sono pubblici (accessibili a chiunque conosca l'URL)
- 💡 Per privacy assoluta, usa URL foto da server privato

## Troubleshooting

### Foto Non Caricata

```python
# Verifica percorso file
from pathlib import Path
photo_path = Path('/Users/giacomo/photo.jpg').expanduser()
print(f"File esiste: {photo_path.exists()}")
print(f"File size: {photo_path.stat().st_size} bytes")

# Testa upload manualmente
from src.mcp_aruba.signature import upload_image_to_imgur
url = upload_image_to_imgur(str(photo_path))
print(f"Imgur URL: {url}")
```

### Firma Non Appare nelle Email

```python
# Verifica firma salvata
from src.mcp_aruba.signature import get_signature, list_signatures

print("Firme disponibili:", list_signatures())
signature = get_signature('default')
print(f"Firma default: {signature[:100]}...")

# Test invio con debug
client.send_email(
    to='test@example.com',
    subject='Test',
    body='Test body',
    use_signature=True  # Assicurati sia True
)
```

### Reset Completo

```bash
# Elimina tutte le firme
rm ~/.config/mcp_aruba/signature.json

# Ricrea da zero
python setup_signature.py
```

## Best Practices

### ✅ DO
- Usa foto professionali e di qualità
- Mantieni le informazioni essenziali
- Scegli colori coerenti con il brand
- Testa l'invio prima di usare in produzione
- Usa firma "default" per email automatiche

### ❌ DON'T
- Non usare immagini troppo grandi (max 1-2 MB)
- Non includere troppe informazioni
- Non usare colori difficili da leggere
- Non dimenticare di testare su diversi client email
- Non condividere link Imgur di foto private/sensibili

## Esempi Completi

Vedi i file di test nella repository:
- `create_signature_test.py` - Esempio creazione firma con foto
- `test_send_with_signature.py` - Esempio invio email con firma
- `setup_signature.py` - Script interattivo per utenti finali
