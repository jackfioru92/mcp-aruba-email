"""Email signature management for Aruba email client."""

import os
import json
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Default signature storage path
SIGNATURE_FILE = Path.home() / ".config" / "mcp_aruba" / "signature.json"


def get_signature_file_path() -> Path:
    """Get the path to the signature configuration file."""
    # Ensure directory exists
    SIGNATURE_FILE.parent.mkdir(parents=True, exist_ok=True)
    return SIGNATURE_FILE


def save_signature(signature: str, name: str = "default") -> None:
    """Save an email signature.
    
    Args:
        signature: The signature text
        name: Name of the signature (default: "default")
    """
    signature_path = get_signature_file_path()
    
    # Load existing signatures
    signatures = {}
    if signature_path.exists():
        try:
            with open(signature_path, 'r', encoding='utf-8') as f:
                signatures = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load existing signatures: {e}")
    
    # Add/update signature
    signatures[name] = signature
    
    # Save
    with open(signature_path, 'w', encoding='utf-8') as f:
        json.dump(signatures, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved signature '{name}'")


def get_signature(name: str = "default") -> Optional[str]:
    """Get an email signature by name.
    
    Args:
        name: Name of the signature (default: "default")
        
    Returns:
        Signature text or None if not found
    """
    signature_path = get_signature_file_path()
    
    if not signature_path.exists():
        return None
    
    try:
        with open(signature_path, 'r', encoding='utf-8') as f:
            signatures = json.load(f)
            return signatures.get(name)
    except Exception as e:
        logger.error(f"Error loading signature: {e}")
        return None


def list_signatures() -> dict[str, str]:
    """List all saved signatures.
    
    Returns:
        Dictionary of signature names and their content
    """
    signature_path = get_signature_file_path()
    
    if not signature_path.exists():
        return {}
    
    try:
        with open(signature_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading signatures: {e}")
        return {}


def delete_signature(name: str = "default") -> bool:
    """Delete a signature.
    
    Args:
        name: Name of the signature to delete
        
    Returns:
        True if deleted, False if not found
    """
    signature_path = get_signature_file_path()
    
    if not signature_path.exists():
        return False
    
    try:
        with open(signature_path, 'r', encoding='utf-8') as f:
            signatures = json.load(f)
        
        if name in signatures:
            del signatures[name]
            
            with open(signature_path, 'w', encoding='utf-8') as f:
                json.dump(signatures, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Deleted signature '{name}'")
            return True
        else:
            return False
            
    except Exception as e:
        logger.error(f"Error deleting signature: {e}")
        return False


def create_default_signature(name: str, email: str, phone: Optional[str] = None, 
                             company: Optional[str] = None, role: Optional[str] = None) -> str:
    """Create a professional email signature.
    
    Args:
        name: Full name
        email: Email address
        phone: Phone number (optional)
        company: Company name (optional)
        role: Job role/title (optional)
        
    Returns:
        Formatted signature text
    """
    signature_parts = [
        "",
        "--",
        name
    ]
    
    if role:
        signature_parts.append(role)
    
    if company:
        signature_parts.append(company)
    
    signature_parts.append(f"📧 {email}")
    
    if phone:
        signature_parts.append(f"📞 {phone}")
    
    return "\n".join(signature_parts)
