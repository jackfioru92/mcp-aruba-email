#!/usr/bin/env python3
"""
Demo script: Come visualizzare le ultime email

Questo script dimostra come utilizzare il client email Aruba per 
visualizzare le ultime email ricevute.

NOTA: Per eseguire questo script con dati reali, devi configurare 
il file .env con le tue credenziali Aruba.
"""

import os
import sys
from dotenv import load_dotenv
from src.mcp_aruba.email_client import ArubaEmailClient

def print_email(email, index):
    """Stampa un'email in formato leggibile."""
    print(f"\n{'='*80}")
    print(f"📧 Email #{index}")
    print(f"{'='*80}")
    print(f"ID:      {email.get('id', 'N/A')}")
    print(f"Da:      {email.get('from', 'N/A')}")
    print(f"A:       {email.get('to', 'N/A')}")
    print(f"Oggetto: {email.get('subject', 'N/A')}")
    print(f"Data:    {email.get('date', 'N/A')}")
    print(f"\nAnteprima:")
    print(f"{'-'*80}")
    body_preview = email.get('body', '')[:200]
    print(f"{body_preview}{'...' if len(email.get('body', '')) > 200 else ''}")
    print(f"{'-'*80}")


def demo_list_latest_emails(limit=5):
    """
    Dimostra come ottenere le ultime email.
    
    Args:
        limit: Numero di email da visualizzare (default: 5)
    """
    print("\n🚀 Demo: Visualizzare le Ultime Email\n")
    print(f"Tento di recuperare le ultime {limit} email...\n")
    
    # Carica configurazione
    load_dotenv()
    
    # Verifica credenziali
    username = os.getenv('IMAP_USERNAME')
    password = os.getenv('IMAP_PASSWORD')
    
    if not username or not password or password == 'your_password_here':
        print("⚠️  CREDENZIALI NON CONFIGURATE")
        print("\nQuesto è uno script dimostrativo.")
        print("Per vedere le tue email reali, devi:")
        print("  1. Copiare .env.example in .env")
        print("  2. Modificare .env con le tue credenziali Aruba")
        print("  3. Rieseguire questo script")
        print("\n" + "="*80)
        print("📝 ESEMPIO DI OUTPUT ATTESO:")
        print("="*80)
        
        # Mostra un esempio di come apparirebbe l'output
        example_emails = [
            {
                'id': '12345',
                'from': 'mario.rossi@example.com',
                'to': 'tuo_email@aruba.it',
                'subject': 'Riunione di domani',
                'date': 'Thu, 5 Dec 2024 14:30:00 +0100',
                'body': 'Ciao,\n\nVolevo confermare la riunione di domani alle 10:00 in sala riunioni A. Porterò i documenti del progetto.\n\nA domani!\nMario'
            },
            {
                'id': '12344',
                'from': 'newsletter@example.com',
                'to': 'tuo_email@aruba.it',
                'subject': 'Newsletter Settimanale - Dicembre 2024',
                'date': 'Thu, 5 Dec 2024 09:00:00 +0100',
                'body': 'Benvenuto alla newsletter di questa settimana!\n\nIn questo numero:\n- Novità del settore\n- Eventi in programma\n- Offerte speciali\n\nBuona lettura!'
            },
            {
                'id': '12343',
                'from': 'support@service.com',
                'to': 'tuo_email@aruba.it',
                'subject': 'Il tuo ticket #5678 è stato risolto',
                'date': 'Wed, 4 Dec 2024 16:45:00 +0100',
                'body': 'Buongiorno,\n\nIl ticket #5678 che hai aperto è stato risolto con successo. Il problema è stato identificato e corretto.\n\nSe hai altre domande, non esitare a contattarci.\n\nCordiali saluti,\nIl Team Support'
            }
        ]
        
        for i, email in enumerate(example_emails[:limit], 1):
            print_email(email, i)
        
        print(f"\n{'='*80}")
        print("✨ FINE ESEMPIO")
        print("="*80)
        print(f"\nCon credenziali reali, vedrai le tue {limit} email più recenti dalla casella Aruba.")
        return
    
    # Esegui con credenziali reali
    try:
        print(f"📡 Connessione a {os.getenv('IMAP_HOST')}...")
        print(f"👤 Utente: {username}\n")
        
        with ArubaEmailClient(
            host=os.getenv('IMAP_HOST', 'imaps.aruba.it'),
            port=int(os.getenv('IMAP_PORT', '993')),
            username=username,
            password=password
        ) as client:
            print("✅ Connesso!\n")
            print(f"📥 Recupero ultime {limit} email...\n")
            
            # Ottieni le email
            emails = client.list_emails(limit=limit)
            
            if not emails:
                print("📭 Nessuna email trovata nella casella INBOX.")
                return
            
            print(f"✅ Trovate {len(emails)} email!\n")
            
            # Stampa le email
            for i, email in enumerate(emails, 1):
                print_email(email, i)
            
            print(f"\n{'='*80}")
            print(f"✅ Recuperate con successo {len(emails)} email")
            print("="*80)
            
    except ValueError as e:
        print(f"\n❌ Errore di configurazione: {e}")
        print("\nVerifica che il file .env sia configurato correttamente.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        print("\nVerifica:")
        print("  - Credenziali corrette in .env")
        print("  - Connessione internet attiva")
        print("  - Firewall non blocca la porta 993")
        sys.exit(1)


def demo_filter_by_sender(sender_email, limit=5):
    """
    Dimostra come filtrare le email per mittente.
    
    Args:
        sender_email: Email del mittente da filtrare
        limit: Numero massimo di email da visualizzare
    """
    print(f"\n🔍 Demo: Filtrare Email per Mittente\n")
    print(f"Cerco email da: {sender_email}\n")
    
    load_dotenv()
    
    try:
        with ArubaEmailClient(
            host=os.getenv('IMAP_HOST', 'imaps.aruba.it'),
            port=int(os.getenv('IMAP_PORT', '993')),
            username=os.getenv('IMAP_USERNAME'),
            password=os.getenv('IMAP_PASSWORD')
        ) as client:
            
            emails = client.list_emails(
                sender_filter=sender_email,
                limit=limit
            )
            
            if not emails:
                print(f"📭 Nessuna email trovata da {sender_email}")
                return
            
            print(f"✅ Trovate {len(emails)} email da {sender_email}!\n")
            
            for i, email in enumerate(emails, 1):
                print_email(email, i)
                
    except Exception as e:
        print(f"❌ Errore: {e}")


def main():
    """Main demo function."""
    print("\n" + "="*80)
    print(" "*20 + "📧 DEMO: VISUALIZZARE LE ULTIME EMAIL")
    print("="*80)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'help' or command == '--help' or command == '-h':
            print("\nUtilizzo:")
            print("  python demo_list_emails.py [limit]")
            print("  python demo_list_emails.py filter <email> [limit]")
            print("\nEsempi:")
            print("  python demo_list_emails.py           # Mostra ultime 5 email")
            print("  python demo_list_emails.py 10        # Mostra ultime 10 email")
            print("  python demo_list_emails.py filter mario@example.com 5")
            return
        
        elif command == 'filter':
            if len(sys.argv) < 3:
                print("❌ Specifica l'email del mittente")
                print("   Esempio: python demo_list_emails.py filter mario@example.com")
                return
            sender = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
            demo_filter_by_sender(sender, limit)
            return
        
        else:
            try:
                limit = int(sys.argv[1])
                demo_list_latest_emails(limit)
            except ValueError:
                print(f"❌ Parametro non valido: {sys.argv[1]}")
                print("   Usa un numero o 'help' per vedere le opzioni")
                return
    else:
        demo_list_latest_emails(limit=5)
    
    print("\n" + "="*80)
    print("💡 SUGGERIMENTI:")
    print("="*80)
    print("• Usa la CLI per accesso rapido: python cli.py emails 10")
    print("• Configura Claude Desktop per interagire con linguaggio naturale")
    print("• Vedi GUIDA_UTILIZZO_EMAIL.md per esempi avanzati")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
