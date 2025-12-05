from src.mcp_aruba.signature import create_default_signature, save_signature
import sys
import re

print('📸 Creazione firma con foto e upload automatico...')
print()

photo_path = '/Users/giacomofiorucci/Desktop/IMG_3088 copia.jpg'

print('⏳ Upload foto su Imgur in corso...')

signature = create_default_signature(
    name='Giacomo Fiorucci',
    email='giacomo.fiorucci@emotion-team.com',
    role='Software Developer',
    company='Emotion Team',
    photo_input=photo_path,
    color='#1ca2c8',
    style='professional'
)

if signature and '<img' in signature:
    print('✅ Firma HTML creata con foto!')
    print()
    
    url_match = re.search(r'src="(https://[^"]+)"', signature)
    if url_match:
        print(f'🌐 Foto caricata su: {url_match.group(1)}')
        print()
    
    print(f'📝 Anteprima firma (primi 500 caratteri):')
    print('=' * 80)
    print(signature[:500] + '...')
    print('=' * 80)
    
    save_signature(signature, 'default')
    print()
    print('✅ Firma salvata come "default"')
    print('💡 Ora tutte le tue email avranno questa firma automaticamente!')
else:
    print('❌ Errore nella creazione della firma')
    sys.exit(1)
