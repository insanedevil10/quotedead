"""
Add/Edit Item Dialog - For creating and editing rate card items
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QLineEdit, QFormLayout,
                             QDoubleSpinBox, QDialogButtonBox)
from PyQt5.QtCore import Qt

class AddEditItemDialog(QDialog):
    """Dialog for adding or editing rate card items"""
    
    def __init__(self, parent=None, item=None, categories=None):
        """Initialize dialog with optional item data and categories"""
        super().__init__(parent)
        self.setWindowTitle("Item Details")
        self.setMinimumWidth(500)
        
        self.item = item or {}
        self.categories = categories or []
        
        self.init_ui()
        
        # Fill fields if editing existing item
        if item:
            self.populate_fields()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QFormLayout(self)
        
        # Category field - combobox with editable option
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        if self.categories:
            self.category_combo.addItems(self.categories)
        layout.addRow("Category:", self.category_combo)
        
        # Item name
        self.item_name = QLineEdit()
        layout.addRow("Item Name:", self.item_name)
        
        # UOM
        self.uom_combo = QComboBox()
        self.uom_combo.addItems(["SFT", "RFT", "NOS"])
        layout.addRow("Unit of Measurement:", self.uom_combo)
        
        # Rate
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setRange(0, 100000)
        self.rate_spin.setDecimals(2)
        self.rate_spin.setSingleStep(10)
        layout.addRow("Base Rate (₹):", self.rate_spin)
        
        # Material options
        self.material_options = QLineEdit()
        self.material_options.setPlaceholderText("e.g. Laminate, Veneer, PU")
        layout.addRow("Material Options:", self.material_options)
        
        # Material prices
        self.material_prices = QLineEdit()
        self.material_prices.setPlaceholderText("e.g. Laminate:0,Veneer:500,PU:800")
        layout.addRow("Material Prices (₹):", self.material_prices)
        
        # Add-ons
        self.add_ons = QLineEdit()
        self.add_ons.setPlaceholderText("e.g. Lights, Profile Door")
        layout.addRow("Add-ons:", self.add_ons)
        
        # Add-on prices
        self.addon_prices = QLineEdit()
        self.addon_prices.setPlaceholderText("e.g. Lights:250,Profile Door:150")
        layout.addRow("Add-on Prices (₹):", self.addon_prices)
        
        # Description for the material prices and add-on prices format
        description = QLabel("Use Name:Price format for multiple material and add-on prices, separated by commas")
        description.setStyleSheet("color: #888; font-style: italic;")
        layout.addRow("", description)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow("", button_box)
    
    def populate_fields(self):
        """Fill form with existing item data"""
        if not self.item:
            return
            
        # Set category
        category = self.item.get("category", "")
        if category:
            index = self.category_combo.findText(category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            else:
                self.category_combo.setEditText(category)
        
        # Set other fields
        self.item_name.setText(self.item.get("item", ""))
        
        # Set UOM
        uom = self.item.get("uom", "SFT")
        uom_index = self.uom_combo.findText(uom)
        if uom_index >= 0:
            self.uom_combo.setCurrentIndex(uom_index)
            
        self.rate_spin.setValue(float(self.item.get("rate", 0)))
        self.material_options.setText(self.item.get("material_options", ""))
        self.material_prices.setText(self.item.get("material_prices", ""))
        self.add_ons.setText(self.item.get("add_ons", ""))
        self.addon_prices.setText(self.item.get("addon_prices", ""))
    
    def get_item_data(self):
        """Get item data from form"""
        return {
            "category": self.category_combo.currentText(),
            "item": self.item_name.text(),
            "uom": self.uom_combo.currentText(),
            "rate": self.rate_spin.value(),
            "material_options": self.material_options.text(),
            "material_prices": self.material_prices.text(),
            "add_ons": self.add_ons.text(),
            "addon_prices": self.addon_prices.text()
        }