"""
Rooms View - Handles the room management tab UI
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox)
from PyQt5.QtCore import Qt

class RoomsView(QWidget):
    """View for room management"""
    
    # Default room types for the application
    DEFAULT_ROOM_TYPES = [
        "Bedroom", "Kitchen", "Living Room", "Bathroom", 
        "Dining Room", "Study", "Balcony", "Foyer", "Puja Room"
    ]
    
    def __init__(self, project_controller):
        """Initialize with Project controller"""
        super().__init__()
        
        self.project_controller = project_controller
        self.init_ui()
        
        # Register for updates from the model (via controller)
        self.project_controller.register_view(self)
        
        # Load initial data
        self.update_from_model()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Room management controls
        controls_layout = QHBoxLayout()
        
        # Room type selection
        self.room_type = QComboBox()
        self.room_type.addItems(self.DEFAULT_ROOM_TYPES)
        controls_layout.addWidget(QLabel("Room Type:"))
        controls_layout.addWidget(self.room_type)
        
        # Add room button
        add_room_btn = QPushButton("Add Room")
        add_room_btn.clicked.connect(self.add_room)
        controls_layout.addWidget(add_room_btn)
        
        # Delete room button
        delete_room_btn = QPushButton("Delete Room")
        delete_room_btn.clicked.connect(self.delete_room)
        controls_layout.addWidget(delete_room_btn)
        
        # Room template button (placeholder for future feature)
        save_template_btn = QPushButton("Save as Template")
        save_template_btn.clicked.connect(self.save_room_template)
        controls_layout.addWidget(save_template_btn)
        
        layout.addLayout(controls_layout)
        
        # Table for rooms
        self.rooms_table = QTableWidget()
        self.rooms_table.setColumnCount(2)
        self.rooms_table.setHorizontalHeaderLabels(["Room Type", "Room Name"])
        self.rooms_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.rooms_table)
        
        # Add description at the bottom
        description = QLabel("Add rooms to your project here. Each room can later be filled with items.")
        description.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(description)
    
    def add_room(self):
        """Add a new room to the project"""
        room_type = self.room_type.currentText()
        
        # Get existing rooms to generate a unique name
        rooms = self.project_controller.get_rooms()
        # Count existing rooms of this type
        count = sum(1 for room in rooms if room["type"] == room_type)
        # Generate room name with incrementing number
        room_name = f"{room_type} {count + 1}"
        
        # Create room data object
        room_data = {
            "type": room_type,
            "name": room_name
        }
        
        # Add to project via controller
        self.project_controller.add_room(room_data)
    
    def delete_room(self):
        """Delete the selected room from the project"""
        # Get selected row
        selected_rows = self.rooms_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No room selected")
            return
        
        row = selected_rows[0].row()
        rooms = self.project_controller.get_rooms()
        
        if row >= len(rooms):
            return
        
        room_name = rooms[row]["name"]
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete '{room_name}'? All items in this room will also be deleted.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove room via controller
            self.project_controller.delete_room(row)
    
    def save_room_template(self):
        """Placeholder for future room template functionality"""
        QMessageBox.information(self, "Info", "Room template feature will be added in future version")
    
    def update_from_model(self):
        """Update UI from model data via controller"""
        # Clear table
        self.rooms_table.setRowCount(0)
        
        # Get rooms from controller
        rooms = self.project_controller.get_rooms()
        
        # Add rows to table
        for i, room in enumerate(rooms):
            self.rooms_table.insertRow(i)
            self.rooms_table.setItem(i, 0, QTableWidgetItem(room.get("type", "")))
            self.rooms_table.setItem(i, 1, QTableWidgetItem(room.get("name", "")))