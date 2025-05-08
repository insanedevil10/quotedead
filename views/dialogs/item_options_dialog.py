"""
Item Options Dialog - For editing item properties with materials and add-ons
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QGroupBox, QCheckBox,
                             QFormLayout, QDoubleSpinBox, QSpinBox, QLineEdit,
                             QMessageBox, QTabWidget, QGridLayout, QScrollArea,
                             QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class ItemOptionsDialog(QDialog):
    """
    Dialog for selecting materials and add-ons for an item.
    This is displayed when adding an item or editing its properties.
    """
    def __init__(self, parent=None, item_data=None, calculation_controller=None):
        """Initialize with item data and calculation controller"""
        super().__init__(parent)
        self.setWindowTitle("Item Options")
        self.setMinimumSize(600, 400)
        
        self.item_data = item_data or {}
        self.calculation_controller = calculation_controller
        
        self.init_ui()
        self.populate_data()
        self.update_preview()
        
        # Connect signals
        self.connect_signals()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Basic info tab
        basic_tab = QWidget()
        basic_layout = QFormLayout(basic_tab)
        
        # Item name
        self.item_name = QLineEdit()
        self.item_name.textChanged.connect(self.update_preview)
        basic_layout.addRow("Item:", self.item_name)
        
        # UOM (Unit of Measurement)
        self.uom_combo = QComboBox()
        self.uom_combo.addItems(["SFT", "RFT", "NOS"])
        self.uom_combo.currentIndexChanged.connect(self.on_uom_changed)
        basic_layout.addRow("Unit of Measurement:", self.uom_combo)
        
        # Rate
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setRange(0, 100000)
        self.rate_spin.setDecimals(2)
        self.rate_spin.setSingleStep(10)
        self.rate_spin.valueChanged.connect(self.update_preview)
        basic_layout.addRow("Base Rate (₹):", self.rate_spin)
        
        # Dimensions group
        dimensions_group = QGroupBox("Dimensions")
        dimensions_layout = QFormLayout(dimensions_group)
        
        # Length
        self.length_spin = QDoubleSpinBox()
        self.length_spin.setRange(0, 1000)
        self.length_spin.setDecimals(2)
        self.length_spin.setSingleStep(0.1)
        self.length_spin.valueChanged.connect(self.update_preview)
        dimensions_layout.addRow("Length:", self.length_spin)
        
        # Height (only for SFT)
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0, 1000)
        self.height_spin.setDecimals(2)
        self.height_spin.setSingleStep(0.1)
        self.height_spin.valueChanged.connect(self.update_preview)
        dimensions_layout.addRow("Height:", self.height_spin)
        
        # Quantity
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0, 1000)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setSingleStep(1)
        self.quantity_spin.setValue(1)  # Default to 1
        self.quantity_spin.valueChanged.connect(self.update_preview)
        dimensions_layout.addRow("Quantity:", self.quantity_spin)
        
        basic_layout.addRow(dimensions_group)
        
        # Add basic tab
        self.tabs.addTab(basic_tab, "Basic Info")
        
        # Materials tab
        materials_tab = QWidget()
        materials_layout = QVBoxLayout(materials_tab)
        
        # Material selection
        self.material_group = QGroupBox("Material Options")
        self.material_layout = QVBoxLayout(self.material_group)
        
        self.material_combo = QComboBox()
        self.material_combo.currentIndexChanged.connect(self.update_preview)
        self.material_layout.addWidget(self.material_combo)
        
        # Material description
        self.material_description = QLabel()
        self.material_description.setStyleSheet("font-style: italic; color: #888;")
        self.material_layout.addWidget(self.material_description)
        
        # Material price addition
        self.material_price_addition = QLabel()
        self.material_layout.addWidget(self.material_price_addition)
        
        materials_layout.addWidget(self.material_group)
        
        # Add materials tab
        self.tabs.addTab(materials_tab, "Materials")
        
        # Add-ons tab
        addons_tab = QScrollArea()
        addons_tab.setWidgetResizable(True)
        addons_content = QWidget()
        addons_layout = QVBoxLayout(addons_content)
        
        # Add-ons group
        self.addons_group = QGroupBox("Add-on Options")
        self.addons_layout = QVBoxLayout(self.addons_group)
        
        # Placeholder for dynamically generated add-on checkboxes
        self.addon_checkboxes = {}
        
        addons_layout.addWidget(self.addons_group)
        addons_tab.setWidget(addons_content)
        
        # Add add-ons tab
        self.tabs.addTab(addons_tab, "Add-ons")
        
        # Add tabs to main layout
        layout.addWidget(self.tabs)
        
        # Preview group
        preview_group = QGroupBox("Price Preview")
        preview_layout = QFormLayout(preview_group)
        
        # Base price
        self.base_price_label = QLabel()
        preview_layout.addRow("Base Price:", self.base_price_label)
        
        # Material addition
        self.material_addition_label = QLabel()
        preview_layout.addRow("Material Addition:", self.material_addition_label)
        
        # Add-ons price
        self.addons_price_label = QLabel()
        preview_layout.addRow("Add-ons:", self.addons_price_label)
        
        # Total price
        self.total_price_label = QLabel()
        self.total_price_label.setStyleSheet("font-weight: bold; color: #C62828;")
        preview_layout.addRow("Total Price:", self.total_price_label)
        
        layout.addWidget(preview_group)
        
        # Dialog buttons
        buttons_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
    
    def connect_signals(self):
        """Connect signal handlers"""
        # When material selection changes, update the price addition display
        self.material_combo.currentIndexChanged.connect(self.update_material_info)
    
    def on_uom_changed(self):
        """Handle UOM change - show/hide height field"""
        # Get selected UOM
        uom = self.uom_combo.currentText()
        
        # Toggle height visibility based on UOM
        if uom == "SFT":
            self.height_spin.setVisible(True)
            self.height_spin.setValue(self.height_spin.value() or 1)  # Default to 1 if was 0
        else:
            self.height_spin.setVisible(False)
            self.height_spin.setValue(0)  # Reset height to 0 when not SFT
        
        # Update field labels
        if uom == "SFT":
            self.length_spin.setPrefix("")
            self.height_spin.setPrefix("")
        elif uom == "RFT":
            self.length_spin.setPrefix("")
            self.height_spin.setPrefix("")
        else:  # NOS
            self.length_spin.setPrefix("")
            self.height_spin.setPrefix("")
        
        # Update the preview when UOM changes
        self.update_preview()
    
    def populate_data(self):
        """Populate the dialog with item data"""
        if not self.item_data:
            return
        
        # Set basic info
        self.item_name.setText(self.item_data.get("item", ""))
        
        # Set UOM
        uom = self.item_data.get("uom", "SFT")
        index = self.uom_combo.findText(uom)
        if index >= 0:
            self.uom_combo.setCurrentIndex(index)
        
        # Set base rate
        self.rate_spin.setValue(float(self.item_data.get("rate", 0)))
        
        # Set dimensions
        self.length_spin.setValue(float(self.item_data.get("length", 0) or 0))
        self.height_spin.setValue(float(self.item_data.get("height", 0) or 0))
        self.quantity_spin.setValue(float(self.item_data.get("quantity", 1) or 1))
        
        # Hide height for non-SFT items
        if uom != "SFT":
            self.height_spin.setVisible(False)
        
        # Populate material options
        self.populate_materials()
        
        # Populate add-ons
        self.populate_addons()
    
    def populate_materials(self):
        """Populate material options"""
        if "material" not in self.item_data:
            self.material_group.setVisible(False)
            return
        
        material = self.item_data["material"]
        options = material.get("options", [])
        selected = material.get("selected", "")
        
        if not options:
            self.material_group.setVisible(False)
            return
        
        # Add options to combo box
        self.material_combo.clear()
        self.material_combo.addItems(options)
        
        # Set selected material if available
        if selected:
            index = self.material_combo.findText(selected)
            if index >= 0:
                self.material_combo.setCurrentIndex(index)
        
        # Update material info display
        self.update_material_info()
    
    def update_material_info(self):
        """Update material information display based on selection"""
        if "material" not in self.item_data:
            return
        
        material = self.item_data["material"]
        price_additions = material.get("price_additions", {})
        
        # Get selected material
        selected = self.material_combo.currentText()
        
        # Update description (placeholder for now)
        self.material_description.setText(f"Selected: {selected}")
        
        # Update price addition
        price_addition = price_additions.get(selected, 0)
        
        # Calculate total additional cost based on UOM and dimensions
        uom = self.uom_combo.currentText()
        length = self.length_spin.value()
        height = self.height_spin.value()
        quantity = self.quantity_spin.value()
        
        total_addition = 0
        if uom == "SFT":
            total_addition = price_addition * length * height * quantity
        elif uom == "RFT":
            total_addition = price_addition * length * quantity
        else:  # NOS
            total_addition = price_addition * quantity
        
        # Show per-unit and total addition
        if price_addition > 0:
            self.material_price_addition.setText(
                f"Additional Cost: ₹{price_addition:.2f} per {uom} (Total: ₹{total_addition:.2f})"
            )
            self.material_price_addition.setStyleSheet("color: #C62828; font-weight: bold;")
        else:
            self.material_price_addition.setText("No additional cost")
            self.material_price_addition.setStyleSheet("")
    
    def populate_addons(self):
        """Populate add-on options"""
        if "add_ons" not in self.item_data or not self.item_data["add_ons"]:
            self.addons_group.setVisible(False)
            return
        
        add_ons = self.item_data["add_ons"]
        
        # Clear existing checkboxes
        for widget in self.addon_checkboxes.values():
            widget["checkbox"].setParent(None)
            widget["description"].setParent(None)
        self.addon_checkboxes = {}
        
        # Get UOM for rate display
        uom = self.uom_combo.currentText()
        
        # Create layout for add-ons
        for addon_name, addon_info in add_ons.items():
            rate = addon_info.get("rate_per_unit", 0)
            
            # Create checkbox with name and rate
            checkbox = QCheckBox(f"{addon_name} (₹{rate:.2f} per {uom})")
            checkbox.setChecked(addon_info.get("selected", False))
            checkbox.stateChanged.connect(self.update_preview)
            
            # Create description label
            description = QLabel(addon_info.get("description", ""))
            description.setStyleSheet("font-style: italic; color: #888;")
            description.setWordWrap(True)
            
            # Add to layout
            addon_layout = QVBoxLayout()
            addon_layout.addWidget(checkbox)
            addon_layout.addWidget(description)
            
            self.addons_layout.addLayout(addon_layout)
            
            # Store widget references
            self.addon_checkboxes[addon_name] = {
                "checkbox": checkbox,
                "description": description
            }
    
    def update_preview(self):
        """Update price preview based on current selections"""
        if not self.calculation_controller:
            return
        
        # Create a copy of the item data to modify
        preview_item = self.item_data.copy()
        
        # Update basic properties from UI
        preview_item["item"] = self.item_name.text()
        preview_item["uom"] = self.uom_combo.currentText()
        preview_item["rate"] = self.rate_spin.value()
        preview_item["length"] = self.length_spin.value()
        preview_item["height"] = self.height_spin.value()
        preview_item["quantity"] = self.quantity_spin.value()
        
        # Update material selection if available
        if "material" in preview_item:
            preview_item["material"]["selected"] = self.material_combo.currentText()
        
        # Update add-on selections if available
        if "add_ons" in preview_item:
            for addon_name, widgets in self.addon_checkboxes.items():
                if addon_name in preview_item["add_ons"]:
                    preview_item["add_ons"][addon_name]["selected"] = widgets["checkbox"].isChecked()
        
        # Calculate base amount without material adjustment or add-ons
        base_item = preview_item.copy()
        
        # Remove material and add-ons to calculate base price
        if "material" in base_item:
            # Temporarily set to base material for base price calculation
            base_material = base_item["material"].get("base_material", "")
            if base_material:
                base_item["material"]["selected"] = base_material
        
        if "add_ons" in base_item:
            # Remove add-ons for base calculation
            for addon_name in base_item["add_ons"]:
                base_item["add_ons"][addon_name]["selected"] = False
        
        # Calculate base amount
        base_amount = self.calculation_controller.calculate_item_amount(base_item)
        
        # Calculate material addition
        material_addition = 0
        if "material" in preview_item:
            # Create item with only material, no add-ons
            material_item = preview_item.copy()
            
            # Disable all add-ons
            if "add_ons" in material_item:
                for addon_name in material_item["add_ons"]:
                    material_item["add_ons"][addon_name]["selected"] = False
            
            # Calculate with material only
            material_amount = self.calculation_controller.calculate_item_amount(material_item)
            material_addition = material_amount - base_amount
        
        # Calculate add-ons cost
        addon_amount = 0
        if "add_ons" in preview_item:
            # Calculate with full item
            total_amount = self.calculation_controller.calculate_item_amount(preview_item)
            addon_amount = total_amount - base_amount - material_addition
        
        # Update preview labels
        self.base_price_label.setText(f"₹{base_amount:.2f}")
        
        if material_addition > 0:
            self.material_addition_label.setText(f"₹{material_addition:.2f}")
        else:
            self.material_addition_label.setText("₹0.00")
        
        if addon_amount > 0:
            self.addons_price_label.setText(f"₹{addon_amount:.2f}")
        else:
            self.addons_price_label.setText("₹0.00")
        
        # Total is sum of all components
        total_amount = base_amount + material_addition + addon_amount
        self.total_price_label.setText(f"₹{total_amount:.2f}")
        
        # Store the calculated amount
        preview_item["amount"] = total_amount
        self.item_data = preview_item
    
    def get_item_data(self):
        """Get the updated item data"""
        return self.item_data