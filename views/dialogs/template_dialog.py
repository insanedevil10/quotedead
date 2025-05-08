"""
Template Dialog - For creating and editing export templates
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QCheckBox, QGroupBox, 
                             QFormLayout, QComboBox, QTextEdit, QTabWidget, 
                             QColorDialog, QFontDialog, QDialogButtonBox,
                             QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from models.company import Company

class TemplateDialog(QDialog):
    """Dialog for creating or editing export templates"""
    
    def __init__(self, parent=None, template=None):
        """Initialize dialog with optional template data"""
        super().__init__(parent)
        self.setWindowTitle("Export Template")
        self.setMinimumWidth(600)
        
        self.template = template or {}
        self.init_ui()
        
        # Fill fields with template data if provided
        if template:
            self.populate_fields()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tabs for different aspects of the template
        tabs = QTabWidget()
        
        # General tab
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        # Template name
        self.template_name = QLineEdit()
        general_layout.addRow("Template Name:", self.template_name)
        
        # Header text
        self.header_text = QLineEdit()
        general_layout.addRow("Header Text:", self.header_text)
        
        # Footer text
        self.footer_text = QLineEdit()
        general_layout.addRow("Footer Text:", self.footer_text)
        
        # Include options
        self.include_logo = QCheckBox("Include Logo")
        general_layout.addRow(self.include_logo)
        
        self.include_company_details = QCheckBox("Include Company Details")
        general_layout.addRow(self.include_company_details)
        
        self.include_images = QCheckBox("Include Item Images")
        general_layout.addRow(self.include_images)
        
        self.include_terms = QCheckBox("Include Terms and Conditions")
        self.include_terms.stateChanged.connect(self.toggle_terms_edit)
        general_layout.addRow(self.include_terms)
        
        # Terms and conditions
        self.terms_text = QTextEdit()
        general_layout.addRow("Terms and Conditions:", self.terms_text)
        
        tabs.addTab(general_tab, "General")
        
        # Style tab
        style_tab = QWidget()
        style_layout = QFormLayout(style_tab)
        
        # Primary color
        color_layout = QHBoxLayout()
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(20, 20)
        self.color_preview.setStyleSheet(f"background-color: {Company.PRIMARY_COLOR}; border: 1px solid #888;")
        color_layout.addWidget(self.color_preview)
        
        self.color_button = QPushButton("Select Color")
        self.color_button.clicked.connect(self.select_color)
        color_layout.addWidget(self.color_button)
        
        self.primary_color = Company.PRIMARY_COLOR  # Hidden field to store color
        style_layout.addRow("Primary Color:", color_layout)
        
        # Font
        font_layout = QHBoxLayout()
        self.font_preview = QLabel("Sample Text")
        self.font_preview.setFont(QFont("Arial", 10))
        font_layout.addWidget(self.font_preview)
        
        self.font_button = QPushButton("Select Font")
        self.font_button.clicked.connect(self.select_font)
        font_layout.addWidget(self.font_button)
        
        self.font_family = "Arial"  # Hidden field to store font family
        self.font_size = 10         # Hidden field to store font size
        style_layout.addRow("Font:", font_layout)
        
        tabs.addTab(style_tab, "Style")
        
        # Layout tab (simplified for now)
        layout_tab = QWidget()
        layout_layout = QFormLayout(layout_tab)
        
        self.layout_type_group = QButtonGroup(self)
        
        self.compact_layout = QRadioButton("Compact (minimalist design)")
        self.layout_type_group.addButton(self.compact_layout, 1)
        layout_layout.addRow(self.compact_layout)
        
        self.detailed_layout = QRadioButton("Detailed (show all fields)")
        self.layout_type_group.addButton(self.detailed_layout, 2)
        layout_layout.addRow(self.detailed_layout)
        
        self.visual_layout = QRadioButton("Visual (includes graphics and charts)")
        self.layout_type_group.addButton(self.visual_layout, 3)
        layout_layout.addRow(self.visual_layout)
        
        # Set default option
        self.detailed_layout.setChecked(True)
        
        tabs.addTab(layout_tab, "Layout")
        
        layout.addWidget(tabs)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def toggle_terms_edit(self, state):
        """Enable/disable terms edit based on checkbox"""
        self.terms_text.setEnabled(state == Qt.Checked)
    
    def select_color(self):
        """Open color dialog to select primary color"""
        color = QColorDialog.getColor(QColor(self.primary_color), self, "Select Primary Color")
        if color.isValid():
            self.primary_color = color.name()
            self.color_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #888;")
    
    def select_font(self):
        """Open font dialog to select font"""
        current_font = QFont(self.font_family, self.font_size)
        font, ok = QFontDialog.getFont(current_font, self, "Select Font")
        if ok:
            self.font_family = font.family()
            self.font_size = font.pointSize()
            self.font_preview.setFont(font)
            self.font_preview.setText(f"Sample Text ({self.font_family}, {self.font_size}pt)")
    
    def populate_fields(self):
        """Fill form with template data"""
        if not self.template:
            return
        
        # General tab
        self.template_name.setText(self.template.get("name", ""))
        self.header_text.setText(self.template.get("header_text", ""))
        self.footer_text.setText(self.template.get("footer_text", ""))
        
        self.include_logo.setChecked(self.template.get("include_logo", True))
        self.include_company_details.setChecked(self.template.get("include_company_details", True))
        self.include_images.setChecked(self.template.get("include_images", False))
        self.include_terms.setChecked(self.template.get("include_terms", True))
        
        self.terms_text.setText(self.template.get("terms_text", ""))
        self.terms_text.setEnabled(self.include_terms.isChecked())
        
        # Style tab
        self.primary_color = self.template.get("primary_color", Company.PRIMARY_COLOR)
        self.color_preview.setStyleSheet(f"background-color: {self.primary_color}; border: 1px solid #888;")
        
        self.font_family = self.template.get("font_family", "Arial")
        self.font_size = self.template.get("font_size", 10)
        self.font_preview.setFont(QFont(self.font_family, self.font_size))
        self.font_preview.setText(f"Sample Text ({self.font_family}, {self.font_size}pt)")
        
        # Layout tab
        layout_type = self.template.get("layout_type", 2)  # Default to detailed
        if layout_type == 1:
            self.compact_layout.setChecked(True)
        elif layout_type == 2:
            self.detailed_layout.setChecked(True)
        elif layout_type == 3:
            self.visual_layout.setChecked(True)
    
    def get_template_data(self):
        """Get template data from form"""
        template = {
            "name": self.template_name.text(),
            "header_text": self.header_text.text(),
            "footer_text": self.footer_text.text(),
            "include_logo": self.include_logo.isChecked(),
            "include_company_details": self.include_company_details.isChecked(),
            "include_images": self.include_images.isChecked(),
            "include_terms": self.include_terms.isChecked(),
            "terms_text": self.terms_text.toPlainText(),
            "primary_color": self.primary_color,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "layout_type": self.layout_type_group.checkedId()
        }
        return template