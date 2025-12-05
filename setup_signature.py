#!/usr/bin/env python3
"""
Script interattivo per creare la firma email personalizzata.
Usare questo script per configurare la propria firma con foto.
"""

from src.mcp_aruba.signature import create_default_signature, save_signature
import sys
from pathlib import Path

def main():
    print("=" * 70)
    print("📧 CONFIGURAZIONE FIRMA EMAIL - MCP Aruba")
    print("=" * 70)
    print()
    print("Questo script ti aiuterà a creare una firma email professionale")
    print("con la tua foto che verrà inclusa automaticamente in tutte le email.")
    print()
    
    # Raccolta informazioni
    print("👤 INFORMAZIONI PERSONALI")
    print("-" * 70)
    name = input("Nome completo: ").strip()
    if not name:
        print("❌ Il nome è obbligatorio!")
        sys.exit(1)
    
    role = input("Ruolo/Posizione (es. Software Developer): ").strip()
    company = input("Azienda: ").strip()
    email = input("Email: ").strip()
    
    if not email:
        print("❌ L'email è obbligatoria!")
        sys.exit(1)
    
    phone = input("Telefono (opzionale, premi INVIO per saltare): ").strip()
    website = input("Sito web (opzionale, premi INVIO per saltare): ").strip()
    
    print()
    print("🎨 PERSONALIZZAZIONE STILE")
    print("-" * 70)
    print("Scegli uno stile per la firma:")
    print("  1. Professional (consigliato) - Bordo colorato e layout classico")
    print("  2. Minimal - Design essenziale")
    print("  3. Colorful - Più colori e vivace")
    
    style_choice = input("Stile (1-3) [1]: ").strip() or "1"
    styles = {"1": "professional", "2": "minimal", "3": "colorful"}
    style = styles.get(style_choice, "professional")
    
    color = input("Colore principale (es. #1ca2c8) [#0066cc]: ").strip() or "#0066cc"
    
    print()
    print("📸 FOTO PROFILO")
    print("-" * 70)
    print("Puoi aggiungere una foto alla tua firma.")
    print("Fornisci il percorso a un file immagine locale (jpg, png) oppure un URL.")
    print("La foto verrà caricata automaticamente su Imgur.")
    print()
    
    photo_input = input("Percorso foto o URL (premi INVIO per saltare): ").strip()
    
    if photo_input:
        # Espandi ~ e verifica se è un file locale
        photo_path = Path(photo_input).expanduser()
        if photo_path.exists() and photo_path.is_file():
            print(f"✅ Foto trovata: {photo_path}")
        elif photo_input.startswith('http'):
            print(f"✅ URL foto: {photo_input}")
        else:
            print(f"⚠️  Attenzione: il file non esiste, verrà tentato comunque")
    
    print()
    print("⏳ Creazione firma in corso...")
    print()
    
    # Crea la firma
    try:
        signature = create_default_signature(
            name=name,
            email=email,
            role=role if role else None,
            company=company if company else None,
            phone=phone if phone else None,
            website=website if website else None,
            photo_input=photo_input if photo_input else None,
            style=style,
            color=color
        )
        
        if not signature:
            print("❌ Errore nella creazione della firma")
            sys.exit(1)
        
        # Salva la firma
        save_signature(signature, 'default')
        
        print("✅ Firma creata e salvata con successo!")
        print()
        print("=" * 70)
        print("🎉 CONFIGURAZIONE COMPLETATA!")
        print("=" * 70)
        print()
        print("La tua firma è stata salvata come firma predefinita.")
        print("Verrà inclusa automaticamente in tutte le email inviate tramite MCP.")
        print()
        
        if photo_input:
            print("📸 La foto è stata caricata su Imgur e sarà visibile nelle email.")
            print()
        
        print("💡 Puoi modificare o eliminare la firma in qualsiasi momento")
        print("   rieseguendo questo script oppure usando i tool MCP:")
        print("   - set_email_signature")
        print("   - get_email_signature")
        print("   - list_email_signatures")
        print()
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
