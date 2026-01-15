#!/usr/bin/env python3
"""
Script per verificare che il progetto sia pronto per la pubblicazione su Smithery.
"""

import json
import sys
import re
from pathlib import Path


def load_pyproject():
    """Carica pyproject.toml (parsing semplice)"""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ File pyproject.toml non trovato!")
        return None
    
    with open(pyproject_path, "r") as f:
        content = f.read()
        
    # Estrai versione e nome con regex
    version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
    name_match = re.search(r'name\s*=\s*"([^"]+)"', content)
    
    if not version_match or not name_match:
        print("❌ Impossibile leggere versione o nome da pyproject.toml")
        return None
    
    return {
        "project": {
            "version": version_match.group(1),
            "name": name_match.group(1)
        }
    }


def load_server_json():
    """Carica server.json"""
    server_json_path = Path("server.json")
    if not server_json_path.exists():
        print("❌ File server.json non trovato!")
        return None
    
    with open(server_json_path, "r") as f:
        return json.load(f)


def check_versions(pyproject, server_json):
    """Verifica che le versioni corrispondano"""
    pyproject_version = pyproject["project"]["version"]
    server_version = server_json["version"]
    
    if pyproject_version != server_version:
        print(f"❌ Versioni non corrispondono:")
        print(f"   pyproject.toml: {pyproject_version}")
        print(f"   server.json: {server_version}")
        return False
    
    print(f"✅ Versioni corrispondono: {pyproject_version}")
    return True


def check_package_name(pyproject, server_json):
    """Verifica il nome del package"""
    pyproject_name = pyproject["project"]["name"]
    
    packages = server_json.get("packages", [])
    if not packages:
        print("❌ Nessun package definito in server.json")
        return False
    
    server_package = packages[0].get("identifier")
    
    if pyproject_name != server_package:
        print(f"❌ Nome package non corrisponde:")
        print(f"   pyproject.toml: {pyproject_name}")
        print(f"   server.json: {server_package}")
        return False
    
    print(f"✅ Nome package corretto: {pyproject_name}")
    return True


def check_schema(server_json):
    """Verifica lo schema MCP"""
    schema = server_json.get("$schema")
    expected_schema = "https://static.modelcontextprotocol.io/schemas/2025-10-17/server.schema.json"
    
    if schema != expected_schema:
        print(f"⚠️  Schema MCP potrebbe non essere aggiornato:")
        print(f"   Attuale: {schema}")
        print(f"   Consigliato: {expected_schema}")
        return False
    
    print(f"✅ Schema MCP corretto")
    return True


def check_repository(server_json):
    """Verifica configurazione repository"""
    repo = server_json.get("repository", {})
    
    if not repo.get("url"):
        print("❌ URL repository non specificato in server.json")
        return False
    
    if "github.com" not in repo["url"]:
        print("⚠️  Repository non è su GitHub")
        return False
    
    print(f"✅ Repository configurato: {repo['url']}")
    return True


def check_env_variables(server_json):
    """Verifica variabili d'ambiente"""
    packages = server_json.get("packages", [])
    if not packages:
        return False
    
    env_vars = packages[0].get("environmentVariables", [])
    
    required_vars = ["EMAIL_USER", "EMAIL_PASSWORD"]
    found_vars = [var["name"] for var in env_vars]
    
    missing = [var for var in required_vars if var not in found_vars]
    
    if missing:
        print(f"⚠️  Variabili d'ambiente mancanti: {', '.join(missing)}")
        return False
    
    # Verifica che le password siano marcate come secret
    for var in env_vars:
        if "PASSWORD" in var["name"] and not var.get("isSecret", False):
            print(f"⚠️  {var['name']} dovrebbe essere marcata come secret")
            return False
    
    print(f"✅ Variabili d'ambiente configurate correttamente ({len(env_vars)} totali)")
    return True


def check_readme():
    """Verifica che README esista"""
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("❌ README.md non trovato!")
        return False
    
    print("✅ README.md presente")
    return True


def check_license():
    """Verifica che LICENSE esista"""
    license_path = Path("LICENSE")
    if not license_path.exists():
        print("⚠️  LICENSE non trovato")
        return False
    
    print("✅ LICENSE presente")
    return True


def main():
    print("🔍 Verifica pre-pubblicazione Smithery\n")
    print("=" * 50)
    
    # Carica file
    print("\n📁 Caricamento file di configurazione...")
    pyproject = load_pyproject()
    server_json = load_server_json()
    
    if not pyproject or not server_json:
        print("\n❌ Impossibile procedere senza i file necessari")
        sys.exit(1)
    
    # Esegui tutti i controlli
    print("\n🔍 Verifica configurazione...\n")
    
    checks = [
        check_versions(pyproject, server_json),
        check_package_name(pyproject, server_json),
        check_schema(server_json),
        check_repository(server_json),
        check_env_variables(server_json),
        check_readme(),
        check_license(),
    ]
    
    # Riepilogo
    print("\n" + "=" * 50)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"\n✅ Tutti i controlli superati! ({passed}/{total})")
        print("\n🚀 Sei pronto per pubblicare su Smithery!")
        print("\nProssimi passi:")
        print("1. Vai su https://smithery.ai")
        print("2. Accedi con GitHub")
        print("3. Pubblica il server")
        sys.exit(0)
    else:
        print(f"\n⚠️  Alcuni controlli falliti: {passed}/{total}")
        print("\n📋 Rivedi gli errori sopra e riprova")
        sys.exit(1)


if __name__ == "__main__":
    main()
