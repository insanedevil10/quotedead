"""
Select From Rate Card Dialog - For selecting items from the rate card
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QFormLayout, QSplitter, QMessageBox, QTreeWidget,
                             QTreeWidgetItem, QCheckBox, QGroupBox, QHeaderView, QSpinBox,
                             QTabWidget, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QColor

from views.dialogs.item_options_dialog import ItemOptionsDialog

class SelectFromRateCardDialog(QDialog):
    """Enhanced dialog for selecting items from rate card"""
    
    def __init__(self, parent=None, rate_card_controller=None, calculation_controller=None):
        """Initialize dialog with controllers"""
        super().__init__(parent)
        self.setWindowTitle("Select from Rate Card")
        self.setMinimumSize(900, 600)
        
        self.rate_card_controller = rate_card_controller
        self.calculation_controller = calculation_controller
        self.selected_items = []
        
        self.init_ui()
        self.populate_tree()
        self.populate_table()
        self.update_category_filter()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tabbed interface for different views
        self.view_tabs = QTabWidget()
        
        # Items grid view (default)
        grid_view = QWidget()
        grid_layout = QVBoxLayout(grid_view)
        
        # Search and filter controls
        filter_group = QGroupBox("Search and Filter")
        filter_layout = QHBoxLayout(filter_group)
        
        # Category filter
        filter_layout.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.currentIndexChanged.connect(self.filter_items)
        filter_layout.addWidget(self.category_filter)
        
        # UOM filter
        filter_layout.addWidget(QLabel("UOM:"))
        self.uom_filter = QComboBox()
        self.uom_filter.addItem("All")
        self.uom_filter.addItems(["SFT", "RFT", "NOS"])
        self.uom_filter.currentIndexChanged.connect(self.filter_items)
        filter_layout.addWidget(self.uom_filter)
        
        # Price range filter
        filter_layout.addWidget(QLabel("Max Rate (₹):"))
        self.max_rate_filter = QSpinBox()
        self.max_rate_filter.setRange(0, 100000)
        self.max_rate_filter.setSingleStep(500)
        self.max_rate_filter.setValue(10000)  # Default max
        self.max_rate_filter.setSpecialValueText("Any")  # Show "Any" for 0
        self.max_rate_filter.valueChanged.connect(self.filter_items)
        filter_layout.addWidget(self.max_rate_filter)
        
        # Search input
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search items...")
        self.search_input.textChanged.connect(self.filter_items)
        filter_layout.addWidget(self.search_input)
        
        grid_layout.addWidget(filter_group)
        
        # Splitter for rate card table and selected items
        splitter = QSplitter(Qt.Vertical)
        
        # Rate card items table
        rate_card_group = QGroupBox("Available Items")
        rate_card_layout = QVBoxLayout(rate_card_group)
        
        self.rate_card_table = QTableWidget()
        self.rate_card_table.setColumnCount(7)
        self.rate_card_table.setHorizontalHeaderLabels([
            "Category", "Item", "UOM", "Base Rate (₹)", 
            "Material Options", "Add-ons", "Actions"
        ])
        self.rate_card_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.rate_card_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.rate_card_table.doubleClicked.connect(self.add_to_selection_with_options)
        rate_card_layout.addWidget(self.rate_card_table)
        
        splitter.addWidget(rate_card_group)
        
        # Selected items group
        selected_group = QGroupBox("Selected Items")
        selected_layout = QVBoxLayout(selected_group)
        
        self.selected_table = QTableWidget()
        self.selected_table.setColumnCount(8)
        self.selected_table.setHorizontalHeaderLabels([
            "Category", "Item", "UOM", "Length", "Height", 
            "Quantity", "Material", "Rate (₹)"
        ])
        self.selected_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        selected_layout.addWidget(self.selected_table)
        
        # Selected items controls
        selected_controls = QHBoxLayout()
        
        edit_btn = QPushButton("Edit Selected Item")
        edit_btn.clicked.connect(self.edit_selected_item)
        selected_controls.addWidget(edit_btn)
        
        duplicate_btn = QPushButton("Duplicate Item")
        duplicate_btn.clicked.connect(self.duplicate_selected_item)
        selected_controls.addWidget(duplicate_btn)
        
        remove_btn = QPushButton("Remove from Selection")
        remove_btn.clicked.connect(self.remove_from_selection)
        selected_controls.addWidget(remove_btn)
        
        clear_btn = QPushButton("Clear Selection")
        clear_btn.clicked.connect(self.clear_selection)
        selected_controls.addWidget(clear_btn)
        
        selected_layout.addLayout(selected_controls)
        
        splitter.addWidget(selected_group)
        
        # Set initial splitter sizes (70% for rate card, 30% for selection)
        splitter.setSizes([700, 300])
        
        grid_layout.addWidget(splitter)
        
        # Add the grid view tab
        self.view_tabs.addTab(grid_view, "Grid View")
        
        # Tree view tab
        tree_view = QWidget()
        tree_layout = QVBoxLayout(tree_view)
        
        # Create category tree for hierarchical browsing
        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderLabels(["Categories and Items"])
        self.category_tree.setColumnWidth(0, 300)
        self.category_tree.itemClicked.connect(self.on_tree_item_clicked)
        tree_layout.addWidget(self.category_tree)
        
        # Tree selection buttons
        tree_buttons = QHBoxLayout()
        
        add_from_tree_btn = QPushButton("Add Selected Item")
        add_from_tree_btn.clicked.connect(self.add_from_tree)
        tree_buttons.addWidget(add_from_tree_btn)
        
        add_all_from_category_btn = QPushButton("Add All from Category")
        add_all_from_category_btn.clicked.connect(self.add_all_from_category)
        tree_buttons.addWidget(add_all_from_category_btn)
        
        tree_layout.addLayout(tree_buttons)
        
        # Add the tree view tab
        self.view_tabs.addTab(tree_view, "Tree View")
        
        # Add tabs to main layout
        layout.addWidget(self.view_tabs)
        
        # Dialog buttons
        btn_layout = QHBoxLayout()
        
        stats_label = QLabel("Selected: 0 items, Total: ₹0.00")
        self.selection_stats = stats_label
        btn_layout.addWidget(stats_label)
        
        btn_layout.addStretch()
        
        add_selected_btn = QPushButton("Add Selected Items")
        add_selected_btn.clicked.connect(self.accept)
        btn_layout.addWidget(add_selected_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def populate_table(self):
        """Populate rate card table with all items"""
        self.filter_items()
    
    def populate_tree(self):
        """Populate category tree with hierarchical data"""
        if not self.rate_card_controller:
            return
            
        self.category_tree.clear()
        
        # Add root item for all categories
        all_categories = QTreeWidgetItem(self.category_tree, ["All Categories"])
        all_categories.setExpanded(True)
        
        # Group items by category
        categories = {}
        for item in self.rate_card_controller.get_items():
            category = item.get("category", "Uncategorized")
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Add categories and their items
        for category, items in categories.items():
            category_item = QTreeWidgetItem(all_categories, [category])
            
            # Add items to category
            for item in items:
                item_text = f"{item['item']} ({item['uom']} - ₹{item['rate']:.2f})"
                item_node = QTreeWidgetItem(category_item, [item_text])
                # Store item data for reference
                item_node.setData(0, Qt.UserRole, item)
            
            # Expand category by default
            category_item.setExpanded(True)
    
    def update_category_filter(self):
        """Update category filter dropdown with available categories"""
        # Save current selection
        current_text = self.category_filter.currentText()
        
        # Block signals to prevent filter triggering during update
        self.category_filter.blockSignals(True)
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        
        # Add available categories
        if self.rate_card_controller:
            categories = self.rate_card_controller.get_categories()
            self.category_filter.addItems(categories)
        
        # Restore selection if possible
        index = self.category_filter.findText(current_text)
        if index >= 0:
            self.category_filter.setCurrentIndex(index)
        
        self.category_filter.blockSignals(False)
    
    def filter_items(self):
        """Filter items in rate card table based on category and search"""
        if not self.rate_card_controller:
            return
            
        # Get filter criteria
        category = self.category_filter.currentText()
        uom_filter = self.uom_filter.currentText()
        max_rate = self.max_rate_filter.value()
        search_text = self.search_input.text().lower()
        
        # Clear table
        self.rate_card_table.setRowCount(0)
        
        # Get all items
        all_items = self.rate_card_controller.get_items()
        
        # Apply filters
        filtered_items = all_items
        
        # Category filter
        if category != "All Categories":
            filtered_items = [item for item in filtered_items if item.get("category") == category]
        
        # UOM filter
        if uom_filter != "All":
            filtered_items = [item for item in filtered_items if item.get("uom") == uom_filter]
        
        # Price filter
        if max_rate > 0:  # Only apply if not "Any"
            filtered_items = [item for item in filtered_items if float(item.get("rate", 0)) <= max_rate]
        
        # Search text filter
        if search_text:
            filtered_items = [
                item for item in filtered_items 
                if search_text in str(item.get("category", "")).lower() or 
                   search_text in str(item.get("item", "")).lower()
            ]
        
        # Update table
        for i, item in enumerate(filtered_items):
            self.rate_card_table.insertRow(i)
            
            self.rate_card_table.setItem(i, 0, QTableWidgetItem(item.get("category", "")))
            self.rate_card_table.setItem(i, 1, QTableWidgetItem(item.get("item", "")))
            self.rate_card_table.setItem(i, 2, QTableWidgetItem(item.get("uom", "")))
            self.rate_card_table.setItem(i, 3, QTableWidgetItem(str(item.get("rate", 0))))
            self.rate_card_table.setItem(i, 4, QTableWidgetItem(item.get("material_options", "")))
            self.rate_card_table.setItem(i, 5, QTableWidgetItem(item.get("add_ons", "")))
            
            # Add button for quick add
            add_btn = QPushButton("Add")
            add_btn.setStyleSheet("padding: 3px;")
            add_btn.clicked.connect(lambda _, row=i: self.quick_add_item(row))
            self.rate_card_table.setCellWidget(i, 6, add_btn)
    
    def quick_add_item(self, row):
        """Quickly add an item without showing options dialog"""
        if row < 0 or row >= self.rate_card_table.rowCount():
            return
            
        # Get item data from table
        category = self.rate_card_table.item(row, 0).text()
        item_name = self.rate_card_table.item(row, 1).text()
        uom = self.rate_card_table.item(row, 2).text()
        rate = float(self.rate_card_table.item(row, 3).text() or 0)
        
        # Find full item data in rate card
        all_items = self.rate_card_controller.get_items()
        found_item = None
        
        for item in all_items:
            if (item.get("category") == category and 
                item.get("item") == item_name and 
                item.get("uom") == uom and 
                float(item.get("rate", 0)) == rate):
                found_item = item
                break
        
        if not found_item:
            QMessageBox.warning(self, "Error", "Item not found in rate card")
            return
        
        # Create basic item structure with default values
        item_data = self.create_item_from_rate_card(found_item)
        
        # Add to selected items
        self.selected_items.append(item_data)
        self.update_selected_table()
        self.update_selection_stats()
    
    def create_item_from_rate_card(self, rate_card_item):
        """Create a line item from rate card item with default values"""
        item_data = {
            "category": rate_card_item.get("category", ""),
            "item": rate_card_item.get("item", ""),
            "uom": rate_card_item.get("uom", "NOS"),
            "length": 0 if rate_card_item.get("uom") in ["SFT", "RFT"] else "",
            "height": 0 if rate_card_item.get("uom") == "SFT" else "",
            "quantity": 1,
            "rate": float(rate_card_item.get("rate", 0))
        }
        
        # Process material options if available
        material_options_str = rate_card_item.get("material_options", "")
        if material_options_str and self.calculation_controller:
            material_data = self.calculation_controller.get_material_options_from_rate_card({
                "material_options": material_options_str,
                "material_prices": rate_card_item.get("material_prices", "")
            })
            
            if material_data["options"]:
                item_data["material"] = material_data
                if material_data["base_material"]:
                    item_data["material"]["selected"] = material_data["base_material"]
        
        # Process add-ons if available
        add_ons_str = rate_card_item.get("add_ons", "")
        addon_prices_str = rate_card_item.get("addon_prices", "")
        if add_ons_str and add_ons_str.lower() != "none" and self.calculation_controller:
            add_ons = self.calculation_controller.get_add_ons_from_rate_card({
                "add_ons": add_ons_str,
                "addon_prices": addon_prices_str
            })
            
            if add_ons:
                item_data["add_ons"] = add_ons
        
        # Calculate amount using calculator
        if self.calculation_controller:
            item_data["amount"] = self.calculation_controller.calculate_item_amount(item_data)
        else:
            # Simple calculation if calculator not available
            item_data["amount"] = float(item_data["rate"]) * float(item_data["quantity"])
        
        return item_data
    
    def add_to_selection_with_options(self):
        """Add selected item to selection with options dialog"""
        selected_rows = self.rate_card_table.selectedIndexes()
        if not selected_rows:
            return
            
        # Get row of first selected cell
        row = selected_rows[0].row()
        
        # Get item data from rate card
        category = self.rate_card_table.item(row, 0).text()
        item_name = self.rate_card_table.item(row, 1).text()
        uom = self.rate_card_table.item(row, 2).text()
        rate = float(self.rate_card_table.item(row, 3).text() or 0)
        
        # Find full item data in rate card
        all_items = self.rate_card_controller.get_items()
        found_item = None
        
        for item in all_items:
            if (item.get("category") == category and 
                item.get("item") == item_name and 
                item.get("uom") == uom and 
                float(item.get("rate", 0)) == rate):
                found_item = item
                break
        
        if not found_item:
            QMessageBox.warning(self, "Error", "Item not found in rate card")
            return
        
        # Create item with default values
        item_data = self.create_item_from_rate_card(found_item)
        
        # Show options dialog
        dialog = ItemOptionsDialog(self, item_data, self.calculation_controller)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get updated item data
            updated_item = dialog.get_item_data()
            
            # Calculate amount
            if self.calculation_controller:
                updated_item["amount"] = self.calculation_controller.calculate_item_amount(updated_item)
            
            # Add to selected items
            self.selected_items.append(updated_item)
            self.update_selected_table()
            self.update_selection_stats()
    
    def edit_selected_item(self):
        """Edit a selected item in the selection"""
        selected_rows = self.selected_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No item selected")
            return
            
        # Get row of first selected cell
        row = selected_rows[0].row()
        
        if 0 <= row < len(self.selected_items):
            # Get item data
            item_data = self.selected_items[row]
            
            # Show options dialog
            dialog = ItemOptionsDialog(self, item_data, self.calculation_controller)
            result = dialog.exec_()
            
            if result == QDialog.Accepted:
                # Get updated item data
                updated_item = dialog.get_item_data()
                
                # Calculate amount using calculator
                if self.calculation_controller:
                    updated_item["amount"] = self.calculation_controller.calculate_item_amount(updated_item)
                
                # Update in selected items
                self.selected_items[row] = updated_item
                self.update_selected_table()
                self.update_selection_stats()
    
    def duplicate_selected_item(self):
        """Duplicate the selected item"""
        selected_rows = self.selected_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No item selected")
            return
            
        # Get row of first selected cell
        row = selected_rows[0].row()
        
        if 0 <= row < len(self.selected_items):
            # Get item data
            original_item = self.selected_items[row]
            
            # Create a deep copy
            import copy
            new_item = copy.deepcopy(original_item)
            
            # Modify name to indicate it's a copy
            if "item" in new_item:
                new_item["item"] = f"{new_item['item']} (Copy)"
            
            # Add to selected items
            self.selected_items.append(new_item)
            self.update_selected_table()
            self.update_selection_stats()
    
    def remove_from_selection(self):
        """Remove item from selection"""
        selected_rows = self.selected_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No item selected")
            return
            
        # Get row of first selected cell
        row = selected_rows[0].row()
        
        # Remove from list
        if 0 <= row < len(self.selected_items):
            del self.selected_items[row]
            self.update_selected_table()
            self.update_selection_stats()
    
    def clear_selection(self):
        """Clear all selected items"""
        if not self.selected_items:
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Action",
            f"Are you sure you want to clear all {len(self.selected_items)} selected items?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.selected_items = []
            self.update_selected_table()
            self.update_selection_stats()
    
    def on_tree_item_clicked(self, item, column):
        """Handle tree item click - update selection info"""
        # Check if it's an item node (has data)
        item_data = item.data(0, Qt.UserRole)
        if item_data:
            # It's an item node, show details at bottom of dialog
            self.selection_stats.setText(f"Ready to add: {item_data.get('item')} - ₹{item_data.get('rate', 0):.2f} per {item_data.get('uom', 'NOS')}")
        else:
            # It's a category node
            child_count = item.childCount()
            self.selection_stats.setText(f"Category: {item.text(0)} - {child_count} items")
    
    def add_from_tree(self):
        """Add the selected item from tree view"""
        selected_items = self.category_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No item selected in tree")
            return
            
        item = selected_items[0]
        item_data = item.data(0, Qt.UserRole)
        
        # Check if it's an item node
        if not item_data:
            QMessageBox.information(self, "Info", "Please select an item, not a category")
            return
        
        # Create basic item structure
        line_item = self.create_item_from_rate_card(item_data)
        
        # Show options dialog
        dialog = ItemOptionsDialog(self, line_item, self.calculation_controller)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get updated item data
            updated_item = dialog.get_item_data()
            
            # Calculate amount
            if self.calculation_controller:
                updated_item["amount"] = self.calculation_controller.calculate_item_amount(updated_item)
            
            # Add to selected items
            self.selected_items.append(updated_item)
            self.update_selected_table()
            self.update_selection_stats()
    
    def add_all_from_category(self):
        """Add all items from the selected category"""
        selected_items = self.category_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No category selected in tree")
            return
            
        item = selected_items[0]
        
        # Get child count to check if it's a category
        child_count = item.childCount()
        if child_count == 0:
            # This is an item node, not a category
            QMessageBox.information(self, "Info", "Please select a category, not an individual item")
            return
        
        # Confirm adding multiple items
        reply = QMessageBox.question(
            self, "Confirm Action",
            f"Are you sure you want to add all {child_count} items from {item.text(0)}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Add all items from this category
        items_added = 0
        for i in range(child_count):
            child = item.child(i)
            item_data = child.data(0, Qt.UserRole)
            
            if item_data:
                # Create basic item structure
                line_item = self.create_item_from_rate_card(item_data)
                
                # Calculate amount
                if self.calculation_controller:
                    line_item["amount"] = self.calculation_controller.calculate_item_amount(line_item)
                
                # Add to selected items
                self.selected_items.append(line_item)
                items_added += 1
        
        # Update UI
        self.update_selected_table()
        self.update_selection_stats()
        
        QMessageBox.information(self, "Success", f"Added {items_added} items from {item.text(0)}")
    
    def update_selected_table(self):
        """Update the selected items table"""
        self.selected_table.setRowCount(0)
        
        for i, item in enumerate(self.selected_items):
            self.selected_table.insertRow(i)
            self.selected_table.setItem(i, 0, QTableWidgetItem(item.get("category", "")))
            self.selected_table.setItem(i, 1, QTableWidgetItem(item.get("item", "")))
            self.selected_table.setItem(i, 2, QTableWidgetItem(item.get("uom", "")))
            self.selected_table.setItem(i, 3, QTableWidgetItem(str(item.get("length", ""))))
            self.selected_table.setItem(i, 4, QTableWidgetItem(str(item.get("height", ""))))
            self.selected_table.setItem(i, 5, QTableWidgetItem(str(item.get("quantity", 1))))
            
            # Add material info if available
            material_text = ""
            if "material" in item and item["material"].get("selected"):
                material_text = item["material"]["selected"]
            self.selected_table.setItem(i, 6, QTableWidgetItem(material_text))
            
            # Add rate
            self.selected_table.setItem(i, 7, QTableWidgetItem(str(item.get("rate", 0))))
    
    def update_selection_stats(self):
        """Update selection statistics"""
        count = len(self.selected_items)
        total = sum(item.get("amount", 0) for item in self.selected_items)
        self.selection_stats.setText(f"Selected: {count} items, Total: ₹{total:.2f}")
    
    def get_selected_items(self):
        """Get the list of selected items"""
        return self.selected_items