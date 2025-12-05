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
                             company: Optional[str] = None, role: Optional[str] = None,
                             photo_url: Optional[str] = None, color: Optional[str] = None,
                             style: str = "professional") -> str:
    """Create a professional email signature.
    
    Args:
        name: Full name
        email: Email address
        phone: Phone number (optional)
        company: Company name (optional)
        role: Job role/title (optional)
        photo_url: URL to profile photo (optional)
        color: Hex color code for accents (optional, e.g., "#0066cc")
        style: Signature style - "professional", "minimal", "colorful" (default: "professional")
        
    Returns:
        Formatted signature text (HTML if photo/color provided, plain text otherwise)
    """
    # If photo or color provided, create HTML signature
    if photo_url or color:
        return _create_html_signature(name, email, phone, company, role, photo_url, color, style)
    
    # Plain text signature
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


def _create_html_signature(name: str, email: str, phone: Optional[str] = None,
                           company: Optional[str] = None, role: Optional[str] = None,
                           photo_url: Optional[str] = None, color: Optional[str] = None,
                           style: str = "professional") -> str:
    """Create an HTML email signature with photo and colors.
    
    Args:
        name: Full name
        email: Email address
        phone: Phone number (optional)
        company: Company name (optional)
        role: Job role/title (optional)
        photo_url: URL to profile photo (optional)
        color: Hex color code for accents (default: "#0066cc")
        style: Signature style
        
    Returns:
        HTML formatted signature
    """
    # Default color if not provided
    if not color:
        color = "#0066cc" if style == "professional" else "#4CAF50" if style == "colorful" else "#333333"
    
    # Build signature HTML
    html_parts = ['<div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6;">']
    
    # Add separator
    html_parts.append('<div style="border-top: 2px solid ' + color + '; margin: 20px 0 10px 0;"></div>')
    
    # Container with photo and info
    html_parts.append('<table cellpadding="0" cellspacing="0" border="0">')
    html_parts.append('<tr>')
    
    # Photo column
    if photo_url:
        html_parts.append('<td style="padding-right: 15px; vertical-align: top;">')
        html_parts.append(f'<img src="{photo_url}" alt="{name}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 3px solid {color};">')
        html_parts.append('</td>')
    
    # Info column
    html_parts.append('<td style="vertical-align: top;">')
    
    # Name (bold and colored)
    html_parts.append(f'<div style="font-size: 16px; font-weight: bold; color: {color}; margin-bottom: 5px;">{name}</div>')
    
    # Role
    if role:
        html_parts.append(f'<div style="font-size: 13px; color: #666; font-style: italic; margin-bottom: 3px;">{role}</div>')
    
    # Company
    if company:
        html_parts.append(f'<div style="font-size: 13px; color: #333; font-weight: 600; margin-bottom: 8px;">{company}</div>')
    
    # Email
    html_parts.append(f'<div style="font-size: 13px; margin-bottom: 3px;">📧 <a href="mailto:{email}" style="color: {color}; text-decoration: none;">{email}</a></div>')
    
    # Phone
    if phone:
        html_parts.append(f'<div style="font-size: 13px;">📞 <span style="color: #333;">{phone}</span></div>')
    
    html_parts.append('</td>')
    html_parts.append('</tr>')
    html_parts.append('</table>')
    
    html_parts.append('</div>')
    
    return ''.join(html_parts)
