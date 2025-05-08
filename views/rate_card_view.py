"""
Rate Card View - Handles the rate card tab UI
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QDialog, QFormLayout, QLineEdit, 
                             QDoubleSpinBox, QGroupBox, QSplitter, QHeaderView)
from PyQt5.QtCore import Qt

from views.dialogs.add_edit_item_dialog import AddEditItemDialog

class RateCardView(QWidget):
    """View for rate card management"""
    
    def __init__(self, rate_card_controller):
        """Initialize with Rate Card controller"""
        super().__init__()
        
        self.rate_card_controller = rate_card_controller
        
        self.init_ui()
        
        # Register for updates from the model (via controller)
        self.rate_card_controller.register_view(self)
        
        # Load initial data
        self.update_from_model()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Create a splitter for category list and items
        splitter = QSplitter(Qt.Horizontal)
        
        # Category panel (left side)
        category_widget = QWidget()
        category_layout = QVBoxLayout(category_widget)
        
        # Category title
        category_layout.addWidget(QLabel("Categories"))
        
        # Category table
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(1)
        self.category_table.setHorizontalHeaderLabels(["Category"])
        self.category_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.category_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.category_table.clicked.connect(self.filter_by_category)
        category_layout.addWidget(self.category_table)
        
        # Category controls
        cat_controls = QHBoxLayout()
        
        self.add_category_btn = QPushButton("Add Category")
        self.add_category_btn.clicked.connect(self.add_category)
        cat_controls.addWidget(self.add_category_btn)
        
        self.del_category_btn = QPushButton("Delete Category")
        self.del_category_btn.clicked.connect(self.delete_category)
        cat_controls.addWidget(self.del_category_btn)
        
        category_layout.addLayout(cat_controls)
        
        # Items panel (right side)
        items_widget = QWidget()
        items_layout = QVBoxLayout(items_widget)
        
        # Rate card title and search
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Rate Card Items"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search items...")
        self.search_input.textChanged.connect(self.filter_rate_card)
        header_layout.addWidget(self.search_input)
        
        items_layout.addLayout(header_layout)
        
        # Rate card table
        self.rate_card_table = QTableWidget()
        self.rate_card_table.setColumnCount(7)
        self.rate_card_table.setHorizontalHeaderLabels([
            "Category", "Item", "UOM", "Base Rate (₹)", 
            "Material Options", "Add-ons", "Actions"
        ])
        self.rate_card_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        items_layout.addWidget(self.rate_card_table)
        
        # Item controls
        item_controls = QHBoxLayout()
        
        self.add_item_btn = QPushButton("Add Item")
        self.add_item_btn.clicked.connect(self.add_item)
        item_controls.addWidget(self.add_item_btn)
        
        self.edit_item_btn = QPushButton("Edit Item")
        self.edit_item_btn.clicked.connect(self.edit_item)
        item_controls.addWidget(self.edit_item_btn)
        
        self.del_item_btn = QPushButton("Delete Item")
        self.del_item_btn.clicked.connect(self.delete_item)
        item_controls.addWidget(self.del_item_btn)
        
        items_layout.addLayout(item_controls)
        
        # Add widgets to splitter
        splitter.addWidget(category_widget)
        splitter.addWidget(items_widget)
        
        # Set initial splitter sizes (30% for categories, 70% for items)
        splitter.setSizes([300, 700])
        
        # Add splitter to main layout
        layout.addWidget(splitter)
        
        # Import/Export controls
        io_controls = QHBoxLayout()
        
        self.import_btn = QPushButton("Import Rate Card")
        self.import_btn.clicked.connect(self.import_rate_card)
        io_controls.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("Export Rate Card")
        self.export_btn.clicked.connect(self.export_rate_card)
        io_controls.addWidget(self.export_btn)
        
        self.protect_btn = QPushButton("Password Protect")
        self.protect_btn.clicked.connect(self.password_protect_rate_card)
        io_controls.addWidget(self.protect_btn)
        
        layout.addLayout(io_controls)
        
        # Add description at the bottom
        description = QLabel("Manage your rate card with standard items, materials, and prices.")
        description.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(description)
    
    def get_selected_category(self):
        """Get the currently selected category in the category table"""
        selected_items = self.category_table.selectedItems()
        if selected_items:
            return selected_items[0].text()
        return None
    
    def update_from_model(self):
        """Update UI from model data via controller"""
        self.update_rate_card_table()
        self.update_category_table()
    
    def update_rate_card_table(self):
        """Update the rate card table with current data"""
        self.rate_card_table.setRowCount(0)
        
        # Get items
        items = self.rate_card_controller.get_items()
        
        # Apply filters
        selected_category = self.get_selected_category()
        search_text = self.search_input.text().lower()
        
        # Filter items
        filtered_items = items
        
        # Filter by category if selected
        if selected_category and selected_category != "All Categories":
            filtered_items = [item for item in filtered_items if item.get("category") == selected_category]
        
        # Filter by search text
        if search_text:
            filtered_items = [
                item for item in filtered_items 
                if search_text in str(item.get("category", "")).lower() or 
                   search_text in str(item.get("item", "")).lower()
            ]
        
        # Add rows
        for i, item in enumerate(filtered_items):
            self.rate_card_table.insertRow(i)
            
            self.rate_card_table.setItem(i, 0, QTableWidgetItem(item.get("category", "")))
            self.rate_card_table.setItem(i, 1, QTableWidgetItem(item.get("item", "")))
            self.rate_card_table.setItem(i, 2, QTableWidgetItem(item.get("uom", "")))
            self.rate_card_table.setItem(i, 3, QTableWidgetItem(str(item.get("rate", 0))))
            self.rate_card_table.setItem(i, 4, QTableWidgetItem(item.get("material_options", "")))
            self.rate_card_table.setItem(i, 5, QTableWidgetItem(item.get("add_ons", "")))
            
            # Add edit button
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("padding: 3px;")
            edit_btn.clicked.connect(lambda _, row=i: self.edit_item_at_row(row))
            self.rate_card_table.setCellWidget(i, 6, edit_btn)
    
    def update_category_table(self):
        """Update the category table"""
        self.category_table.setRowCount(0)
        
        # Add "All Categories" option
        self.category_table.insertRow(0)
        self.category_table.setItem(0, 0, QTableWidgetItem("All Categories"))
        
        # Add categories
        categories = self.rate_card_controller.get_categories()
        for i, category in enumerate(categories):
            row = i + 1  # +1 for "All Categories"
            self.category_table.insertRow(row)
            self.category_table.setItem(row, 0, QTableWidgetItem(category))
    
    def filter_by_category(self):
        """Filter rate card items by selected category"""
        self.update_rate_card_table()
    
    def filter_rate_card(self):
        """Filter rate card by search text"""
        self.update_rate_card_table()
    
    def add_category(self):
        """Add a new category"""
        category_name, ok = QInputDialog.getText(
            self, "Add Category", "Enter category name:"
        )
        
        if ok and category_name:
            # Check if category already exists
            existing_categories = self.rate_card_controller.get_categories()
            if category_name in existing_categories:
                QMessageBox.warning(self, "Warning", f"Category '{category_name}' already exists")
                return
            
            # Create a sample item in the category
            new_item = {
                "category": category_name,
                "item": "Sample Item",
                "uom": "SFT",
                "rate": 0,
                "material_options": "",
                "add_ons": ""
            }
            
            # Add to rate card controller
            self.rate_card_controller.add_item(new_item)
            
            # Update UI
            self.update_category_table()
            
            # Select the new category
            for row in range(self.category_table.rowCount()):
                if self.category_table.item(row, 0).text() == category_name:
                    self.category_table.selectRow(row)
                    break
    
    def delete_category(self):
        """Delete the selected category and all its items"""
        selected_items = self.category_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No category selected")
            return
        
        category = selected_items[0].text()
        
        # Skip if "All Categories" is selected
        if category == "All Categories":
            QMessageBox.warning(self, "Warning", "Cannot delete 'All Categories'")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Delete category '{category}' and all its items?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Get all items in this category
        items = self.rate_card_controller.get_items()
        items_to_delete = []
        
        for i, item in enumerate(items):
            if item.get("category") == category:
                items_to_delete.append(i)
        
        # Delete items in reverse order to avoid index issues
        for index in sorted(items_to_delete, reverse=True):
            self.rate_card_controller.delete_item(index)
        
        # Update UI
        self.update_from_model()
        
        # Select "All Categories"
        self.category_table.selectRow(0)
    
    def add_item(self):
        """Add a new item to the rate card"""
        # Get current selected category
        category = self.get_selected_category() or "General"
        if category == "All Categories":
            category = "General"
        
        # Show dialog
        categories = self.rate_card_controller.get_categories()
        dialog = AddEditItemDialog(self, None, categories)
        dialog.category_combo.setCurrentText(category)
        
        if dialog.exec_() == QDialog.Accepted:
            # Get item data
            item_data = dialog.get_item_data()
            
            # Add to rate card controller
            self.rate_card_controller.add_item(item_data)
            
            # Update UI
            self.update_from_model()
    
    def edit_item(self):
        """Edit the selected item in the rate card"""
        selected_items = self.rate_card_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No item selected")
            return
        
        row = selected_items[0].row()
        self.edit_item_at_row(row)
    
    def edit_item_at_row(self, row):
        """Edit the item at the specified row"""
        # Get the filtered items based on current category and search
        selected_category = self.get_selected_category()
        search_text = self.search_input.text().lower()
        
        all_items = self.rate_card_controller.get_items()
        filtered_items = all_items
        
        # Apply category filter
        if selected_category and selected_category != "All Categories":
            filtered_items = [item for item in filtered_items if item.get("category") == selected_category]
        
        # Apply search filter
        if search_text:
            filtered_items = [
                item for item in filtered_items 
                if search_text in str(item.get("category", "")).lower() or 
                   search_text in str(item.get("item", "")).lower()
            ]
        
        if row < 0 or row >= len(filtered_items):
            return
            
        # Find the actual index in the full list
        target_item = filtered_items[row]
        actual_index = all_items.index(target_item)
        
        # Show edit dialog
        categories = self.rate_card_controller.get_categories()
        dialog = AddEditItemDialog(self, target_item, categories)
        
        if dialog.exec_() == QDialog.Accepted:
            # Get updated item data
            item_data = dialog.get_item_data()
            
            # Update in rate card controller
            self.rate_card_controller.update_item(actual_index, item_data)
            
            # Update UI
            self.update_from_model()
    
    def delete_item(self):
        """Delete the selected item from the rate card"""
        selected_items = self.rate_card_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No item selected")
            return
        
        row = selected_items[0].row()
        
        # Get the filtered items based on current category and search
        selected_category = self.get_selected_category()
        search_text = self.search_input.text().lower()
        
        all_items = self.rate_card_controller.get_items()
        filtered_items = all_items
        
        # Apply category filter
        if selected_category and selected_category != "All Categories":
            filtered_items = [item for item in filtered_items if item.get("category") == selected_category]
        
        # Apply search filter
        if search_text:
            filtered_items = [
                item for item in filtered_items 
                if search_text in str(item.get("category", "")).lower() or 
                   search_text in str(item.get("item", "")).lower()
            ]
        
        if row < 0 or row >= len(filtered_items):
            return
            
        target_item = filtered_items[row]
        item_name = target_item.get("item", "")
        actual_index = all_items.index(target_item)
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Delete item '{item_name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete from rate card controller
            self.rate_card_controller.delete_item(actual_index)
            
            # Update UI
            self.update_from_model()
    
    def import_rate_card(self):
        """Import rate card from file"""
        if self.rate_card_controller.load_rate_card(parent_widget=self):
            self.update_from_model()
    
    def export_rate_card(self):
        """Export rate card to file"""
        self.rate_card_controller.save_rate_card(parent_widget=self)
    
    def password_protect_rate_card(self):
        """Set password protection for rate card"""
        self.rate_card_controller.set_password_protection(parent_widget=self)