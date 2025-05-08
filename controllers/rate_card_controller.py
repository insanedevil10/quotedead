"""
Rate Card Controller - Handles interactions between Rate Card model and UI
"""
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog, QLineEdit

class RateCardController:
    """Controller for managing rate card data and UI interactions"""
    
    def __init__(self, rate_card_model):
        """Initialize with Rate Card model"""
        self.rate_card_model = rate_card_model
    
    def get_items(self):
        """Get all rate card items"""
        return self.rate_card_model.get_items()
    
    def get_item(self, index):
        """Get a specific item by index"""
        return self.rate_card_model.get_item(index)
    
    def add_item(self, item_data):
        """Add a new item to the rate card"""
        return self.rate_card_model.add_item(item_data)
    
    def update_item(self, index, item_data):
        """Update an item in the rate card"""
        return self.rate_card_model.update_item(index, item_data)
    
    def delete_item(self, index):
        """Delete an item from the rate card"""
        return self.rate_card_model.delete_item(index)
    
    def get_categories(self):
        """Get list of all categories in the rate card"""
        return self.rate_card_model.get_categories()
    
    def get_items_by_category(self, category):
        """Get all items in a specific category"""
        return self.rate_card_model.get_items_by_category(category)
    
    def save_rate_card(self, parent_widget=None):
        """Save rate card to file with file dialog"""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            parent_widget, "Save Rate Card", "", 
            "JSON Files (*.json);;Excel Files (*.xlsx)"
        )
        
        if not file_path:
            return False
            
        # Add default extension based on selected filter if needed
        if not file_path.lower().endswith(('.json', '.xlsx')):
            if "JSON" in selected_filter:
                file_path += ".json"
            else:
                file_path += ".xlsx"
        
        success = self.rate_card_model.save_to_file(file_path)
        
        if success and parent_widget:
            QMessageBox.information(parent_widget, "Success", "Rate card saved successfully")
        elif not success and parent_widget:
            QMessageBox.critical(parent_widget, "Error", "Failed to save rate card")
        
        return success
    
    def load_rate_card(self, parent_widget=None):
        """Load rate card from file with file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget, "Load Rate Card", "", 
            "Rate Card Files (*.json *.xlsx)"
        )
        
        if not file_path:
            return False
        
        # Check if password required
        if self.rate_card_model.is_password_protected:
            password = self._prompt_for_password(parent_widget)
            if not password or not self.rate_card_model.verify_password(password):
                if parent_widget:
                    QMessageBox.warning(parent_widget, "Access Denied", "Incorrect password")
                return False
        
        success = self.rate_card_model.load_from_file(file_path)
        
        if success and parent_widget:
            QMessageBox.information(parent_widget, "Success", "Rate card loaded successfully")
        elif not success and parent_widget:
            QMessageBox.critical(parent_widget, "Error", "Failed to load rate card")
        
        return success
    
    def set_password_protection(self, parent_widget=None):
        """Set or change password protection for rate card"""
        # Check if already password protected
        if self.rate_card_model.is_password_protected:
            # Verify current password first
            current_password = self._prompt_for_password(parent_widget)
            if not current_password or not self.rate_card_model.verify_password(current_password):
                if parent_widget:
                    QMessageBox.warning(parent_widget, "Access Denied", "Incorrect password")
                return False
            
            # Ask if user wants to change or remove password
            if parent_widget:
                items = ["Change Password", "Remove Password"]
                action, ok = QInputDialog.getItem(
                    parent_widget, "Password Protection",
                    "Do you want to change or remove the password?",
                    items, 0, False
                )
                
                if not ok:
                    return False
                
                if action == "Remove Password":
                    self.rate_card_model.set_password_protection(None)
                    QMessageBox.information(parent_widget, "Success", "Password protection removed")
                    return True
            
        # Set new password
        if parent_widget:
            password, ok = QInputDialog.getText(
                parent_widget, "Set Password",
                "Enter password for rate card:",
                QLineEdit.Password
            )
            
            if not ok or not password:
                return False
            
            # Confirm password
            confirm, ok = QInputDialog.getText(
                parent_widget, "Confirm Password",
                "Confirm password:",
                QLineEdit.Password
            )
            
            if not ok or password != confirm:
                QMessageBox.warning(parent_widget, "Error", "Passwords do not match")
                return False
            
            # Set password
            self.rate_card_model.set_password_protection(password)
            QMessageBox.information(parent_widget, "Success", "Password protection set successfully")
            return True
        
        return False
    
    def _prompt_for_password(self, parent_widget):
        """Prompt user for password"""
        if not parent_widget:
            return None
        
        password, ok = QInputDialog.getText(
            parent_widget, "Password Required",
            "Enter password for rate card:",
            QLineEdit.Password
        )
        
        if not ok:
            return None
        
        return password
    
    def register_view(self, view):
        """Register a view to be updated when rate card data changes"""
        self.rate_card_model.add_listener(lambda model: view.update_from_model())