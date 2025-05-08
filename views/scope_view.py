"""
Scope View - Handles the scope of work tab UI
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QMenu, QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from views.dialogs.item_options_dialog import ItemOptionsDialog
from views.dialogs.select_from_rate_card_dialog import SelectFromRateCardDialog
from views.dialogs.bulk_material_options_dialog import BulkMaterialOptionsDialog

class ScopeView(QWidget):
    """View for scope of work management"""
    
    def __init__(self, project_controller, calculation_controller, rate_card_controller):
        """Initialize with controllers"""
        super().__init__()
        
        self.project_controller = project_controller
        self.calculation_controller = calculation_controller
        self.rate_card_controller = rate_card_controller
        
        self.init_ui()
        
        # Register for updates from the model (via controller)
        self.project_controller.register_view(self)
        
        # Load initial data
        self.update_from_model()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Create toolbar for common actions
        toolbar_layout = QHBoxLayout()
        
        # Add item button
        add_item_btn = QPushButton("Add Item")
        add_item_btn.clicked.connect(self.add_line_item)
        toolbar_layout.addWidget(add_item_btn)
        
        # Add from rate card button
        rate_card_btn = QPushButton("From Rate Card")
        rate_card_btn.clicked.connect(self.add_from_rate_card)
        toolbar_layout.addWidget(rate_card_btn)
        
        # Delete item button
        delete_item_btn = QPushButton("Delete Item")
        delete_item_btn.clicked.connect(self.delete_line_item)
        toolbar_layout.addWidget(delete_item_btn)
        
        # Edit options button
        edit_options_btn = QPushButton("Edit Options")
        edit_options_btn.clicked.connect(self.edit_item_with_options)
        toolbar_layout.addWidget(edit_options_btn)
        
        # Bulk edit button
        bulk_edit_btn = QPushButton("Bulk Edit")
        bulk_edit_btn.clicked.connect(self.bulk_edit_items)
        toolbar_layout.addWidget(bulk_edit_btn)
        
        # Add toolbar to layout
        layout.addLayout(toolbar_layout)
        
        # Room selection for scope
        room_layout = QHBoxLayout()
        room_layout.addWidget(QLabel("Select Room:"))
        
        self.scope_room_selector = QComboBox()
        self.scope_room_selector.currentIndexChanged.connect(self.on_room_selection_changed)
        room_layout.addWidget(self.scope_room_selector)
        
        layout.addLayout(room_layout)
        
        # Table for line items
        self.line_items_table = QTableWidget()
        self.line_items_table.setColumnCount(8)  # Added columns for material and add-ons summary
        self.line_items_table.setHorizontalHeaderLabels([
            "Item", "UOM", "Length", "Height", "Quantity", 
            "Material", "Rate (₹)", "Amount (₹)"
        ])
        self.line_items_table.horizontalHeader().setStretchLastSection(True)
        
        # Connect cell editing to update calculations
        self.line_items_table.cellChanged.connect(self.on_line_item_cell_changed)
        self.line_items_table.doubleClicked.connect(self.edit_item_with_options)
        
        # Enable context menu
        self.line_items_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.line_items_table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.line_items_table)
        
        # Add description at the bottom
        description = QLabel("Select a room and add items to it. Double-click an item to edit its properties.")
        description.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(description)
    
    def show_context_menu(self, position):
        """Show context menu for line items table"""
        # Get the row under the cursor
        row = self.line_items_table.rowAt(position.y())
        if row < 0:
            return
        
        # Create context menu
        menu = QMenu(self)
        
        edit_action = menu.addAction("Edit Options")
        edit_action.triggered.connect(lambda: self.edit_item_with_options(self.line_items_table.indexAt(position)))
        
        duplicate_action = menu.addAction("Duplicate Item")
        duplicate_action.triggered.connect(lambda: self.duplicate_line_item(row))
        
        delete_action = menu.addAction("Delete Item")
        delete_action.triggered.connect(lambda: self.delete_line_item(row))
        
        # Show menu at cursor position
        menu.exec_(QCursor.pos())
    
    def on_room_selection_changed(self):
        """Handle room selection change"""
        self.update_line_items_table()
    
    def on_line_item_cell_changed(self, row, column):
        """Handle cell value changes in the table"""
        # Ignore if table is being programmatically updated
        if self.line_items_table.signalsBlocked():
            return
            
        # Get selected room
        room_name = self.scope_room_selector.currentText()
        if not room_name:
            return
            
        # Get line items for current room
        room_items = self.project_controller.get_line_items(room_name)
        
        if row >= len(room_items):
            return
            
        # Get the actual item index in the full list
        all_items = self.project_controller.get_line_items()
        item_index = -1
        
        for i, item in enumerate(all_items):
            if item["room"] == room_name and item == room_items[row]:
                item_index = i
                break
                
        if item_index == -1:
            return
            
        # Update item based on column
        item = all_items[item_index].copy()  # Make a copy to modify
        
        try:
            if column == 0:  # Item name
                item["item"] = self.line_items_table.item(row, column).text()
            elif column == 1:  # UOM
                item["uom"] = self.line_items_table.item(row, column).text()
            elif column == 2:  # Length
                length_text = self.line_items_table.item(row, column).text()
                item["length"] = float(length_text) if length_text else 0
            elif column == 3:  # Height
                height_text = self.line_items_table.item(row, column).text()
                item["height"] = float(height_text) if height_text else 0
            elif column == 4:  # Quantity
                quantity_text = self.line_items_table.item(row, column).text()
                item["quantity"] = float(quantity_text) if quantity_text else 0
            elif column == 5:  # Material - readonly in direct edit
                pass
            elif column == 6:  # Rate
                rate_text = self.line_items_table.item(row, column).text()
                item["rate"] = float(rate_text) if rate_text else 0
                
            # Recalculate amount using calculator controller
            item["amount"] = self.calculation_controller.calculate_item_amount(item)
            
            # Update in project controller
            self.project_controller.update_line_item(item_index, item)
            
            # Update amount cell
            self.line_items_table.blockSignals(True)
            self.line_items_table.setItem(row, 7, QTableWidgetItem(f"{item['amount']:.2f}"))
            self.line_items_table.blockSignals(False)
            
        except ValueError:
            # Reset to previous value if invalid input
            self.update_line_items_table()
            QMessageBox.warning(self, "Warning", "Please enter valid numeric values")
    
    def add_line_item(self):
        """Add a new line item to the current room"""
        # Check if any rooms exist
        if len(self.project_controller.get_rooms()) == 0:
            QMessageBox.warning(self, "Warning", "Add at least one room first")
            return
        
        # Get selected room
        room_name = self.scope_room_selector.currentText()
        if not room_name:
            return
        
        # Create basic line item
        new_item = {
            "room": room_name,
            "item": "New Item",
            "uom": "SFT",
            "length": 0,
            "height": 0,
            "quantity": 1,
            "rate": 0,
            "amount": 0
        }
        
        # Show options dialog to configure the item
        dialog = ItemOptionsDialog(self, new_item, self.calculation_controller)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get updated item data
            updated_item = dialog.get_item_data()
            
            # Calculate amount
            updated_item["amount"] = self.calculation_controller.calculate_item_amount(updated_item)
            
            # Add to project via controller
            self.project_controller.add_line_item(updated_item)
    
    def duplicate_line_item(self, selected_row=None):
        """Duplicate the selected line item"""
        # Get selected room
        room_name = self.scope_room_selector.currentText()
        if not room_name:
            return
        
        # If row not specified, get from selection
        if selected_row is None:
            selected_rows = self.line_items_table.selectedIndexes()
            if not selected_rows:
                QMessageBox.warning(self, "Warning", "No line item selected")
                return
            
            selected_row = selected_rows[0].row()
        
        # Get line items for current room
        room_items = self.project_controller.get_line_items(room_name)
        
        if selected_row >= len(room_items):
            return
        
        # Create a deep copy of the item
        import copy
        item_to_duplicate = copy.deepcopy(room_items[selected_row])
        
        # Modify name to indicate it's a copy
        item_to_duplicate["item"] = f"{item_to_duplicate['item']} (Copy)"
        
        # Add to project via controller
        self.project_controller.add_line_item(item_to_duplicate)
        
        # Show success message
        QMessageBox.information(self, "Success", f"Item '{room_items[selected_row]['item']}' duplicated")
    
    def delete_line_item(self, selected_row=None):
        """Delete the selected line item"""
        # Get selected room
        room_name = self.scope_room_selector.currentText()
        if not room_name:
            return
        
        # If row not specified, get from selection
        if selected_row is None:
            selected_rows = self.line_items_table.selectedIndexes()
            if not selected_rows:
                QMessageBox.warning(self, "Warning", "No line item selected")
                return
            
            selected_row = selected_rows[0].row()
        
        # Get line items for current room
        room_items = self.project_controller.get_line_items(room_name)
        
        if selected_row >= len(room_items):
            return
        
        item_name = room_items[selected_row]["item"]
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete '{item_name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Find the actual index in the full list
            all_items = self.project_controller.get_line_items()
            for i, item in enumerate(all_items):
                if item["room"] == room_name and item["item"] == item_name:
                    # Remove from project data via controller
                    self.project_controller.delete_line_item(i)
                    break
    
    def edit_item_with_options(self, index=None):
        """Open the options dialog to edit the selected item"""
        # Get selected room
        room_name = self.scope_room_selector.currentText()
        if not room_name:
            return
        
        # Get selected row
        if index is None or not index.isValid():
            selected_rows = self.line_items_table.selectedIndexes()
            if not selected_rows:
                QMessageBox.warning(self, "Warning", "No line item selected")
                return
            
            row = selected_rows[0].row()
        else:
            row = index.row()
        
        # Get line items for current room
        room_items = self.project_controller.get_line_items(room_name)
        
        if row >= len(room_items):
            return
        
        # Get the actual item index in the full list
        all_items = self.project_controller.get_line_items()
        item_index = -1
        item_to_edit = None
        
        for i, item in enumerate(all_items):
            if item["room"] == room_name and item == room_items[row]:
                item_index = i
                item_to_edit = item.copy()
                break
        
        if item_index == -1 or not item_to_edit:
            return
        
        # Show options dialog
        dialog = ItemOptionsDialog(self, item_to_edit, self.calculation_controller)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get updated item data
            updated_item = dialog.get_item_data()
            
            # Calculate amount
            updated_item["amount"] = self.calculation_controller.calculate_item_amount(updated_item)
            
            # Update in project controller
            self.project_controller.update_line_item(item_index, updated_item)
    
    def bulk_edit_items(self):
        """Open dialog for bulk editing material and add-on options"""
        # Get selected room
        room_name = self.scope_room_selector.currentText()
        if not room_name:
            # If no room selected, use all items from all rooms
            all_items = self.project_controller.get_line_items()
            if not all_items:
                QMessageBox.warning(self, "Warning", "No items to edit")
                return
            
            # Show the bulk edit dialog
            dialog = BulkMaterialOptionsDialog(self, all_items, self.calculation_controller)
            result = dialog.exec_()
            
            if result == QDialog.Accepted:
                # Get changed items and apply updates
                changed_items = dialog.get_changed_items()
                for change in changed_items:
                    self.project_controller.update_line_item(change["index"], change["item"])
        else:
            # Use items from the selected room
            room_items = self.project_controller.get_line_items(room_name)
            if not room_items:
                QMessageBox.warning(self, "Warning", "No items in the selected room")
                return
            
            # Show the bulk edit dialog
            dialog = BulkMaterialOptionsDialog(self, room_items, self.calculation_controller)
            result = dialog.exec_()
            
            if result == QDialog.Accepted:
                # Get changed items and apply updates
                changed_items = dialog.get_changed_items()
                
                # Find the actual indices in the full list
                all_items = self.project_controller.get_line_items()
                
                for change in changed_items:
                    room_item = room_items[change["index"]]
                    for i, item in enumerate(all_items):
                        if item["room"] == room_name and item == room_item:
                            # Update the item
                            self.project_controller.update_line_item(i, change["item"])
                            break
    
    def add_from_rate_card(self):
        """Add items from rate card to quote"""
        # Check if any rooms exist
        if len(self.project_controller.get_rooms()) == 0:
            QMessageBox.warning(self, "Warning", "Add at least one room first")
            return
        
        # Get selected room
        room_name = self.scope_room_selector.currentText()
        if not room_name:
            return
        
        # Create and show dialog
        dialog = SelectFromRateCardDialog(self, self.rate_card_controller, self.calculation_controller)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get selected items
            selected_items = dialog.get_selected_items()
            
            # Add each item to the quote
            for item_data in selected_items:
                # Create new line item with room info
                new_item = item_data.copy()
                new_item["room"] = room_name
                
                # Ensure amount is calculated
                new_item["amount"] = self.calculation_controller.calculate_item_amount(new_item)
                
                # Add to project via controller
                self.project_controller.add_line_item(new_item)
            
            # Show success message
            if selected_items:
                QMessageBox.information(
                    self, "Success",
                    f"{len(selected_items)} items added to {room_name}"
                )
    
    def update_line_items_table(self):
        """Update the line items table for the selected room"""
        # Block signals temporarily to prevent triggering cell change events
        self.line_items_table.blockSignals(True)
        
        # Clear table
        self.line_items_table.setRowCount(0)
        
        # Get selected room
        room_name = self.scope_room_selector.currentText()
        if not room_name:
            self.line_items_table.blockSignals(False)
            return
        
        # Get line items for selected room
        room_items = self.project_controller.get_line_items(room_name)
        
        # Add rows
        for i, item in enumerate(room_items):
            self.line_items_table.insertRow(i)
            self.line_items_table.setItem(i, 0, QTableWidgetItem(item.get("item", "")))
            self.line_items_table.setItem(i, 1, QTableWidgetItem(item.get("uom", "")))
            self.line_items_table.setItem(i, 2, QTableWidgetItem(str(item.get("length", ""))))
            self.line_items_table.setItem(i, 3, QTableWidgetItem(str(item.get("height", ""))))
            self.line_items_table.setItem(i, 4, QTableWidgetItem(str(item.get("quantity", ""))))
            
            # Material column - display selected material if available
            material_text = ""
            if "material" in item and item["material"].get("selected"):
                material_text = item["material"]["selected"]
            self.line_items_table.setItem(i, 5, QTableWidgetItem(material_text))
            
            self.line_items_table.setItem(i, 6, QTableWidgetItem(str(item.get("rate", ""))))
            self.line_items_table.setItem(i, 7, QTableWidgetItem(f"{item.get('amount', 0):.2f}"))
        
        # Restore signals
        self.line_items_table.blockSignals(False)
    
    def update_from_model(self):
        """Update UI from model data via controller"""
        # Update room selector
        self.update_room_selector()
        
        # Update line items
        self.update_line_items_table()
    
    def update_room_selector(self):
        """Update the room selector combobox"""
        # Save current selection
        current_room = self.scope_room_selector.currentText()
        
        # Clear selector
        self.scope_room_selector.blockSignals(True)
        self.scope_room_selector.clear()
        
        # Add rooms
        rooms = self.project_controller.get_rooms()
        for room in rooms:
            self.scope_room_selector.addItem(room["name"])
        
        # Restore selection if possible
        if current_room:
            index = self.scope_room_selector.findText(current_room)
            if index >= 0:
                self.scope_room_selector.setCurrentIndex(index)
        
        self.scope_room_selector.blockSignals(False)
        
        # Update line items if we have a selection
        if self.scope_room_selector.count() > 0:
            self.update_line_items_table()