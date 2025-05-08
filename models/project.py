"""
Project Model - Contains data structures and logic for project data
"""
import json
import datetime
from pathlib import Path

class Project:
    """Model for project data"""
    
    def __init__(self):
        """Initialize with default project data"""
        self.project_info = {
            "name": "",
            "client_name": "",
            "site_address": "",
            "contact_info": "",
            "project_type": ""
        }
        self.rooms = []
        self.line_items = []
        self.settings = {
            "gst": 18,
            "discount": 0
        }
        
        # Observable pattern - listeners for data changes
        self._listeners = []
    
    def add_listener(self, listener):
        """Add a listener to be notified when project data changes"""
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
    
    # Project Info Methods
    def get_project_info(self):
        """Get project information"""
        return self.project_info.copy()
    
    def set_project_info(self, info):
        """Update project information"""
        self.project_info.update(info)
        self.notify_listeners()
    
    # Room Methods
    def get_rooms(self):
        """Get all rooms"""
        return self.rooms.copy()
    
    def add_room(self, room):
        """Add a new room"""
        self.rooms.append(room)
        self.notify_listeners()
        return len(self.rooms) - 1  # Return index of new room
    
    def update_room(self, index, room):
        """Update a room at the specified index"""
        if 0 <= index < len(self.rooms):
            self.rooms[index] = room
            self.notify_listeners()
            return True
        return False
    
    def delete_room(self, index):
        """Delete a room and its associated items"""
        if 0 <= index < len(self.rooms):
            room_name = self.rooms[index]["name"]
            del self.rooms[index]
            
            # Remove associated line items
            self.line_items = [
                item for item in self.line_items
                if item["room"] != room_name
            ]
            
            self.notify_listeners()
            return True
        return False
    
    # Line Item Methods
    def get_line_items(self, room=None):
        """Get all line items, optionally filtered by room"""
        if room:
            return [item.copy() for item in self.line_items if item["room"] == room]
        return [item.copy() for item in self.line_items]
    
    def add_line_item(self, item):
        """Add a new line item"""
        self.line_items.append(item)
        self.notify_listeners()
        return len(self.line_items) - 1  # Return index of new item
    
    def update_line_item(self, index, item):
        """Update a line item at the specified index"""
        if 0 <= index < len(self.line_items):
            self.line_items[index] = item
            self.notify_listeners()
            return True
        return False
    
    def delete_line_item(self, index):
        """Delete a line item"""
        if 0 <= index < len(self.line_items):
            del self.line_items[index]
            self.notify_listeners()
            return True
        return False
    
    # Settings Methods
    def get_settings(self):
        """Get project settings"""
        return self.settings.copy()
    
    def update_settings(self, settings):
        """Update project settings"""
        self.settings.update(settings)
        self.notify_listeners()
    
    # File Operations
    def save_to_file(self, file_path):
        """Save project to a file"""
        try:
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Add version and timestamp for future compatibility
            data = {
                "version": "1.0",
                "timestamp": datetime.datetime.now().isoformat(),
                "data": {
                    "project_info": self.project_info,
                    "rooms": self.rooms,
                    "line_items": self.line_items,
                    "settings": self.settings
                }
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            
            return True
        except Exception as e:
            print(f"Error saving project: {str(e)}")
            return False
    
    def load_from_file(self, file_path):
        """Load project from a file"""
        try:
            with open(file_path, 'r') as f:
                loaded_data = json.load(f)
            
            # Check for versioned format
            if isinstance(loaded_data, dict) and "data" in loaded_data:
                data = loaded_data["data"]
            else:
                # Legacy format (no version)
                data = loaded_data
            
            # Update project data
            if "project_info" in data:
                self.project_info = data["project_info"]
            
            if "rooms" in data:
                self.rooms = data["rooms"]
            
            if "line_items" in data:
                self.line_items = data["line_items"]
            
            if "settings" in data:
                self.settings = data["settings"]
            
            self.notify_listeners()
            return True
        except Exception as e:
            print(f"Error loading project: {str(e)}")
            return False
    
    def create_new(self):
        """Create a new empty project"""
        self.project_info = {
            "name": "",
            "client_name": "",
            "site_address": "",
            "contact_info": "",
            "project_type": ""
        }
        self.rooms = []
        self.line_items = []
        self.settings = {
            "gst": 18,
            "discount": 0
        }
        self.notify_listeners()