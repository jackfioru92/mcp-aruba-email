"""Email signature management for Aruba email client."""

import os
import json
import base64
import requests
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


def upload_image_to_imgur(image_path: str, client_id: str = "546c25a59c58ad7") -> Optional[str]:
    """Upload an image to Imgur and return the public URL.
    
    Uses Imgur's anonymous upload API (no account required).
    
    Args:
        image_path: Path to the local image file
        client_id: Imgur API client ID (default is a public demo key)
        
    Returns:
        Public URL of uploaded image, or None if upload failed
    """
    try:
        # Read image file
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Convert to base64
        b64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Upload to Imgur
        headers = {'Authorization': f'Client-ID {client_id}'}
        data = {'image': b64_image, 'type': 'base64'}
        
        response = requests.post(
            'https://api.imgur.com/3/image',
            headers=headers,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            url = result['data']['link']
            logger.info(f"Image uploaded successfully: {url}")
            return url
        else:
            logger.error(f"Imgur upload failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        return None


def process_photo(photo_input: str) -> Optional[str]:
    """Process photo input - either use URL directly or upload local file.
    
    Args:
        photo_input: Either a URL (starts with http) or a local file path
        
    Returns:
        Public URL of the photo, or None if processing failed
    """
    # If it's already a URL, return it
    if photo_input.startswith('http://') or photo_input.startswith('https://'):
        return photo_input
    
    # If it's a local file, upload to Imgur
    photo_path = Path(photo_input).expanduser()
    
    if not photo_path.exists():
        logger.error(f"Photo file not found: {photo_input}")
        return None
    
    if not photo_path.is_file():
        logger.error(f"Photo path is not a file: {photo_input}")
        return None
    
    # Check file extension
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    if photo_path.suffix.lower() not in valid_extensions:
        logger.error(f"Unsupported image format: {photo_path.suffix}")
        return None
    
    logger.info(f"Uploading local photo to Imgur: {photo_input}")
    return upload_image_to_imgur(str(photo_path))


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
                             photo_input: Optional[str] = None, color: Optional[str] = None,
                             style: str = "professional") -> str:
    """Create a professional email signature.
    
    Args:
        name: Full name
        email: Email address
        phone: Phone number (optional)
        company: Company name (optional)
        role: Job role/title (optional)
        photo_input: URL or local file path to profile photo (optional, auto-uploads if local)
        color: Hex color code for accents (optional, e.g., "#0066cc")
        style: Signature style - "professional", "minimal", "colorful" (default: "professional")
        
    Returns:
        Formatted signature text (HTML if photo/color provided, plain text otherwise)
    """
    # Process photo if provided (upload to Imgur if it's a local file)
    photo_url = None
    if photo_input:
        photo_url = process_photo(photo_input)
        if not photo_url:
            logger.warning("Photo processing failed, creating signature without photo")
    
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
        html_parts.append(f'<img src="{photo_url}" alt="{name}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; object-position: center 30%; border: 3px solid {color};">')
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
