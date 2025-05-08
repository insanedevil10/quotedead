"""
Rate Card Model - Manages the rate card data and operations
"""
import json
import hashlib
import os
import pandas as pd
from pathlib import Path

class RateCard:
    """Model for rate card data and operations"""
    
    def __init__(self):
        """Initialize with default rate card data"""
        self.items = []
        self.file_path = ""
        self.password_hash = ""
        self.is_password_protected = False
        
        # Add some default items
        self.populate_default_items()
        
        # Observable pattern - listeners for data changes
        self._listeners = []
    
    def add_listener(self, listener):
        """Add a listener to be notified when rate card data changes"""
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def remove_listener(self, listener):
        """Remove a listener"""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def notify_listeners(self):
        """Notify all listeners about data changes"""
        for listener in self._listeners:
            listener(self)
    
    def populate_default_items(self):
        """Add default items to the rate card"""
        self.items = [
            {"category": "Wall Work", "item": "POP Wall", "uom": "SFT", "rate": 150, "material_options": "Standard, Premium", "add_ons": "None"},
            {"category": "Wall Work", "item": "Wall Painting", "uom": "SFT", "rate": 80, "material_options": "Regular, Texture", "add_ons": "None"},
            {"category": "Furniture", "item": "TV Unit", "uom": "SFT", "rate": 1200, "material_options": "Laminate, Veneer, PU", "add_ons": "Lights, Profile Door"},
            {"category": "Furniture", "item": "Wardrobe", "uom": "SFT", "rate": 1500, "material_options": "Laminate, Veneer, PU", "add_ons": "Lights, Profile Door"},
            {"category": "Furniture", "item": "Kitchen", "uom": "SFT", "rate": 2200, "material_options": "Laminate, Acrylic, PU", "add_ons": "Lights, Profile Door"},
            {"category": "Decorative", "item": "False Ceiling", "uom": "SFT", "rate": 220, "material_options": "Regular, Cove", "add_ons": "Lights"},
            {"category": "Decorative", "item": "Curtains", "uom": "SFT", "rate": 180, "material_options": "Regular, Blackout", "add_ons": "None"},
        ]
    
    def get_items(self):
        """Get all rate card items"""
        return self.items.copy()
    
    def get_item(self, index):
        """Get item at the specified index"""
        if 0 <= index < len(self.items):
            return self.items[index].copy()
        return None
    
    def add_item(self, item):
        """Add a new item to the rate card"""
        self.items.append(item)
        self.notify_listeners()
        return len(self.items) - 1
    
    def update_item(self, index, item):
        """Update an existing item"""
        if 0 <= index < len(self.items):
            self.items[index] = item
            self.notify_listeners()
            return True
        return False
    
    def delete_item(self, index):
        """Delete an item from the rate card"""
        if 0 <= index < len(self.items):
            del self.items[index]
            self.notify_listeners()
            return True
        return False
    
    def get_items_by_category(self, category):
        """Get all items in a specific category"""
        return [item.copy() for item in self.items if item.get("category") == category]
    
    def get_categories(self):
        """Get list of all unique categories"""
        return sorted(list(set(item.get("category", "") for item in self.items)))
    
    def save_to_file(self, file_path):
        """Save rate card to a file"""
        try:
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data for saving
            export_data = {
                'version': '1.0',
                'is_password_protected': self.is_password_protected,
                'password_hash': self.password_hash if self.is_password_protected else '',
                'items': self.items
            }
            
            # Determine format based on extension
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.json':
                # Save as JSON
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=4)
            elif ext == '.xlsx':
                # Save as Excel
                self._export_to_excel(file_path)
            else:
                # Default to JSON
                with open(file_path + '.json', 'w') as f:
                    json.dump(export_data, f, indent=4)
                file_path += '.json'
            
            self.file_path = file_path
            return True
        except Exception as e:
            print(f"Error saving rate card: {str(e)}")
            return False
    
    def _export_to_excel(self, file_path):
        """Export rate card to Excel file"""
        # Create DataFrame from items
        df = pd.DataFrame(self.items)
        
        # Rename columns for better readability
        column_map = {
            'category': 'Category',
            'item': 'Item',
            'uom': 'UOM',
            'rate': 'Base Rate (₹)',
            'material_options': 'Material Options',
            'add_ons': 'Add-ons',
            'material_prices': 'Material Prices',
            'addon_prices': 'Add-on Prices'
        }
        df.rename(columns=column_map, inplace=True)
        
        # Export to Excel
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Rate Card', index=False)
        
        # Format the Excel sheet
        workbook = writer.book
        worksheet = writer.sheets['Rate Card']
        
        # Add header format
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#C62828',
            'font_color': 'white'
        })
        
        # Apply header format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Auto-adjust column widths
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).apply(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)
        
        writer.close()
    
    def load_from_file(self, file_path):
        """Load rate card from a file"""
        try:
            # Determine format based on extension
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.json':
                # Load from JSON
                with open(file_path, 'r') as f:
                    loaded_data = json.load(f)
                
                # Check for versioned format
                if isinstance(loaded_data, dict) and 'items' in loaded_data:
                    self.items = loaded_data['items']
                    if 'is_password_protected' in loaded_data:
                        self.is_password_protected = loaded_data['is_password_protected']
                        self.password_hash = loaded_data.get('password_hash', '')
                else:
                    # Assume direct items list
                    self.items = loaded_data
            
            elif ext in ['.xlsx', '.xls']:
                # Load from Excel
                self._import_from_excel(file_path)
            
            else:
                # Unsupported format
                print(f"Unsupported file format: {ext}")
                return False
            
            self.file_path = file_path
            self.notify_listeners()
            return True
        except Exception as e:
            print(f"Error loading rate card: {str(e)}")
            return False
    
    def _import_from_excel(self, file_path):
        """Import rate card from Excel file"""
        df = pd.read_excel(file_path)
        
        # Map columns to our data structure
        self.items = []
        for _, row in df.iterrows():
            item = {
                "category": str(row.get('Category', '')),
                "item": str(row.get('Item', '')),
                "uom": str(row.get('UOM', 'SFT')),
                "rate": float(row.get('Base Rate (₹)', 0)),
                "material_options": str(row.get('Material Options', '')),
                "add_ons": str(row.get('Add-ons', 'None'))
            }
            
            # Add additional fields if they exist
            if 'Material Prices' in row:
                item["material_prices"] = str(row.get('Material Prices', ''))
            
            if 'Add-on Prices' in row:
                item["addon_prices"] = str(row.get('Add-on Prices', ''))
            
            self.items.append(item)
    
    def set_password_protection(self, password=None):
        """Set or remove password protection"""
        if password is None:
            # Remove password protection
            self.is_password_protected = False
            self.password_hash = ""
        else:
            # Set password protection
            self.is_password_protected = True
            self.password_hash = self._hash_password(password)
        
        self.notify_listeners()
        return True
    
    def verify_password(self, password):
        """Verify the provided password"""
        if not self.is_password_protected:
            return True
        
        return self._hash_password(password) == self.password_hash
    
    def _hash_password(self, password):
        """Create a SHA-256 hash of the password"""
        return hashlib.sha256(password.encode()).hexdigest()