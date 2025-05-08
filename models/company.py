"""
Company Model - Handles company configuration and branding
"""
import os
from pathlib import Path

class Company:
    """Model for company configuration and branding"""
    
    # Default company information
    COMPANY_NAME = "Kart Designs & HomeProject LLP"
    COMPANY_ADDRESS = "Home Project, patancheruvu, ORR exit 3"
    COMPANY_PHONE = "+91 9009 81008"
    COMPANY_EMAIL = "info@homeproject.in"
    COMPANY_WEBSITE = "homeproject.in"
    
    # Company colors
    PRIMARY_COLOR = "#C62828"  # Dark red for accents and selected items
    HEADER_BG_COLOR = "#FFFFFF"  # White background for header
    HEADER_TEXT_COLOR = "#333333"  # Dark gray for text on white background
    
    # Logo file names - these files should be placed in the 'assets' folder
    LOGO_FULL_FILE = "home_project_logo_full.png"
    LOGO_COMPACT_FILE = "home_project_logo_compact.png"
    
    @classmethod
    def get_company_details(cls):
        """Get formatted company details"""
        return {
            "name": cls.COMPANY_NAME,
            "address": cls.COMPANY_ADDRESS,
            "phone": cls.COMPANY_PHONE,
            "email": cls.COMPANY_EMAIL,
            "website": cls.COMPANY_WEBSITE,
            "contact": f"{cls.COMPANY_PHONE} | {cls.COMPANY_EMAIL} | {cls.COMPANY_WEBSITE}"
        }
    
    @classmethod
    def get_logo_path(cls, compact=False):
        """Get path to logo file"""
        # Determine which logo to use
        logo_file = cls.LOGO_COMPACT_FILE if compact else cls.LOGO_FULL_FILE
        
        # Create assets directory path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level (to get out of models folder)
        parent_dir = os.path.dirname(base_dir)
        assets_dir = os.path.join(parent_dir, "assets")
        
        # Ensure assets directory exists
        os.makedirs(assets_dir, exist_ok=True)
        
        # Return full path to logo file
        return os.path.join(assets_dir, logo_file)
    
    @classmethod
    def check_logo_files(cls):
        """Check if logo files exist and return result"""
        full_logo_path = cls.get_logo_path(compact=False)
        compact_logo_path = cls.get_logo_path(compact=True)
        
        return {
            "full_logo_exists": os.path.exists(full_logo_path),
            "compact_logo_exists": os.path.exists(compact_logo_path),
            "full_logo_path": full_logo_path,
            "compact_logo_path": compact_logo_path
        }
    
    @classmethod
    def install_logo_files(cls, full_logo_path, compact_logo_path):
        """Install logo files to assets directory"""
        import shutil
        
        # Ensure assets directory exists
        base_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(base_dir)
        assets_dir = os.path.join(parent_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        
        # Copy full logo
        if full_logo_path and os.path.exists(full_logo_path):
            dest_path = os.path.join(assets_dir, cls.LOGO_FULL_FILE)
            shutil.copy2(full_logo_path, dest_path)
        
        # Copy compact logo
        if compact_logo_path and os.path.exists(compact_logo_path):
            dest_path = os.path.join(assets_dir, cls.LOGO_COMPACT_FILE)
            shutil.copy2(compact_logo_path, dest_path)
            
        return cls.check_logo_files()