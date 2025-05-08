"""
Project Controller - Handles interactions between Project model and UI
"""
from PyQt5.QtWidgets import QFileDialog, QMessageBox

class ProjectController:
    """Controller for managing project data and UI interactions"""
    
    def __init__(self, project_model):
        """Initialize with Project model"""
        self.project_model = project_model
    
    def set_project_info(self, info):
        """Update project information"""
        self.project_model.set_project_info(info)
    
    def get_project_info(self):
        """Get project information"""
        return self.project_model.get_project_info()
    
    def add_room(self, room_data):
        """Add a new room to the project"""
        return self.project_model.add_room(room_data)
    
    def get_rooms(self):
        """Get all rooms in the project"""
        return self.project_model.get_rooms()
    
    def delete_room(self, index):
        """Delete a room from the project"""
        return self.project_model.delete_room(index)
    
    def add_line_item(self, item_data):
        """Add a new line item to the project"""
        return self.project_model.add_line_item(item_data)
    
    def get_line_items(self, room=None):
        """Get line items, optionally filtered by room"""
        return self.project_model.get_line_items(room)
    
    def update_line_item(self, index, item_data):
        """Update a line item in the project"""
        return self.project_model.update_line_item(index, item_data)
    
    def delete_line_item(self, index):
        """Delete a line item from the project"""
        return self.project_model.delete_line_item(index)
    
    def update_settings(self, settings):
        """Update project settings"""
        self.project_model.update_settings(settings)
    
    def get_settings(self):
        """Get project settings"""
        return self.project_model.get_settings()
    
    def save_project(self, parent_widget=None):
        """Save project to file with file dialog"""
        file_path, _ = QFileDialog.getSaveFileName(
            parent_widget, "Save Project", "", "JSON Files (*.json)"
        )
        
        if not file_path:
            return False
        
        # Add .json extension if not present
        if not file_path.lower().endswith('.json'):
            file_path += '.json'
        
        success = self.project_model.save_to_file(file_path)
        
        if success and parent_widget:
            QMessageBox.information(parent_widget, "Success", "Project saved successfully")
        elif not success and parent_widget:
            QMessageBox.critical(parent_widget, "Error", "Failed to save project")
        
        return success
    
    def load_project(self, parent_widget=None):
        """Load project from file with file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget, "Load Project", "", "JSON Files (*.json)"
        )
        
        if not file_path:
            return False
        
        success = self.project_model.load_from_file(file_path)
        
        if success and parent_widget:
            QMessageBox.information(parent_widget, "Success", "Project loaded successfully")
        elif not success and parent_widget:
            QMessageBox.critical(parent_widget, "Error", "Failed to load project")
        
        return success
    
    def new_project(self, parent_widget=None):
        """Create a new project"""
        # If parent widget is provided, confirm with user
        if parent_widget:
            reply = QMessageBox.question(
                parent_widget, "New Project", 
                "Are you sure you want to create a new project? Unsaved changes will be lost.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return False
        
        self.project_model.create_new()
        
        if parent_widget:
            QMessageBox.information(parent_widget, "Success", "New project created")
        
        return True
    
    def register_view(self, view):
        """Register a view to be updated when project data changes"""
        self.project_model.add_listener(lambda model: view.update_from_model())