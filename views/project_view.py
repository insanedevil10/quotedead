"""
Project View - Handles the project information tab UI
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt

class ProjectView(QWidget):
    """View for project information management"""
    
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
        
        # Form layout for project details
        form_layout = QFormLayout()
        
        # Project name
        self.project_name = QLineEdit()
        self.project_name.textChanged.connect(self.on_field_changed)
        form_layout.addRow("Project Name:", self.project_name)
        
        # Client name
        self.client_name = QLineEdit()
        self.client_name.textChanged.connect(self.on_field_changed)
        form_layout.addRow("Client Name:", self.client_name)
        
        # Site address
        self.site_address = QLineEdit()
        self.site_address.textChanged.connect(self.on_field_changed)
        form_layout.addRow("Site Address:", self.site_address)
        
        # Contact info
        self.contact_info = QLineEdit()
        self.contact_info.textChanged.connect(self.on_field_changed)
        form_layout.addRow("Contact Info:", self.contact_info)
        
        # Project type
        self.project_type = QComboBox()
        self.project_type.addItems(["Apartment", "Villa", "Farmhouse", "Independent House", "Office Space"])
        self.project_type.currentTextChanged.connect(self.on_field_changed)
        form_layout.addRow("Project Type:", self.project_type)
        
        # Add form to layout
        layout.addLayout(form_layout)
        
        # Add buttons for save/load project
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Project")
        save_btn.clicked.connect(self.save_project)
        buttons_layout.addWidget(save_btn)
        
        load_btn = QPushButton("Load Project")
        load_btn.clicked.connect(self.load_project)
        buttons_layout.addWidget(load_btn)
        
        new_btn = QPushButton("New Project")
        new_btn.clicked.connect(self.new_project)
        buttons_layout.addWidget(new_btn)
        
        layout.addLayout(buttons_layout)
        
        # Add stretch to push form to the top
        layout.addStretch()
        
        # Add description at the bottom
        description = QLabel("Input your project details and client information here.")
        description.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(description)
    
    def on_field_changed(self):
        """Update project data when fields change"""
        self.update_project_data()
    
    def update_project_data(self):
        """Update project data in the model via controller"""
        self.project_controller.set_project_info({
            "name": self.project_name.text(),
            "client_name": self.client_name.text(),
            "site_address": self.site_address.text(),
            "contact_info": self.contact_info.text(),
            "project_type": self.project_type.currentText()
        })
    
    def update_from_model(self):
        """Update UI from model data via controller"""
        # Temporarily block signals to prevent triggering on_field_changed
        self.project_name.blockSignals(True)
        self.client_name.blockSignals(True)
        self.site_address.blockSignals(True)
        self.contact_info.blockSignals(True)
        self.project_type.blockSignals(True)
        
        # Get project info from controller
        project_info = self.project_controller.get_project_info()
        
        # Update UI elements
        self.project_name.setText(project_info.get("name", ""))
        self.client_name.setText(project_info.get("client_name", ""))
        self.site_address.setText(project_info.get("site_address", ""))
        self.contact_info.setText(project_info.get("contact_info", ""))
        
        # Set project type if it exists
        project_type = project_info.get("project_type", "")
        if project_type:
            index = self.project_type.findText(project_type)
            if index >= 0:
                self.project_type.setCurrentIndex(index)
        
        # Restore signals
        self.project_name.blockSignals(False)
        self.client_name.blockSignals(False)
        self.site_address.blockSignals(False)
        self.contact_info.blockSignals(False)
        self.project_type.blockSignals(False)
    
    def save_project(self):
        """Save project data"""
        self.project_controller.save_project(parent_widget=self)
    
    def load_project(self):
        """Load project data"""
        self.project_controller.load_project(parent_widget=self)
    
    def new_project(self):
        """Create a new project"""
        self.project_controller.new_project(parent_widget=self)