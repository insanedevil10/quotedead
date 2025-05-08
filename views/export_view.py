"""
Export View - Handles the export tab UI
"""
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QCheckBox, QGroupBox, 
                             QFormLayout, QComboBox, QTextEdit, QTabWidget, 
                             QColorDialog, QFontDialog, QDialog, QDialogButtonBox,
                             QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont, QColor

from models.company import Company
from views.dialogs.template_dialog import TemplateDialog

class ExportView(QWidget):
    """View for export functionality"""
    
    def __init__(self, project_controller, calculation_controller, export_controller):
        """Initialize with controllers"""
        super().__init__()
        
        self.project_controller = project_controller
        self.calculation_controller = calculation_controller
        self.export_controller = export_controller
        
        self.init_ui()
        
        # Register for updates from the model (via controller)
        self.project_controller.register_view(self)
        
        # Load initial data
        self.update_from_model()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tabs for export options
        tabs = QTabWidget()
        
        # Basic tab
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # Export options group
        options_group = QGroupBox("Export Options")
        options_layout = QFormLayout(options_group)
        
        # Template selection
        self.template_combo = QComboBox()
        self.template_combo.addItems(self.export_controller.get_template_names())
        self.template_combo.currentIndexChanged.connect(self.on_template_changed)
        
        template_layout = QHBoxLayout()
        template_layout.addWidget(self.template_combo)
        
        self.new_template_btn = QPushButton("New")
        self.new_template_btn.clicked.connect(self.create_template)
        template_layout.addWidget(self.new_template_btn)
        
        self.edit_template_btn = QPushButton("Edit")
        self.edit_template_btn.clicked.connect(self.edit_template)
        template_layout.addWidget(self.edit_template_btn)
        
        self.delete_template_btn = QPushButton("Delete")
        self.delete_template_btn.clicked.connect(self.delete_template)
        template_layout.addWidget(self.delete_template_btn)
        
        options_layout.addRow("Template:", template_layout)
        
        # Logo selection
        logo_layout = QHBoxLayout()
        self.logo_path = QLineEdit()
        self.logo_path.setReadOnly(True)
        self.logo_path.setText(self.export_controller.get_logo_path())
        self.logo_path.setPlaceholderText("Default logo will be used")
        logo_layout.addWidget(self.logo_path)
        
        logo_btn = QPushButton("Change Logo")
        logo_btn.clicked.connect(self.select_logo)
        logo_layout.addWidget(logo_btn)
        
        options_layout.addRow("Company Logo:", logo_layout)
        
        # Logo preview
        self.logo_preview = QLabel()
        
        # Display company logo by default
        logo_path = self.export_controller.get_logo_path()
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            if not logo_pixmap.isNull():
                scaled_pixmap = logo_pixmap.scaled(200, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_preview.setPixmap(scaled_pixmap)
            else:
                self.logo_preview.setText("Invalid logo image")
        else:
            self.logo_preview.setText("No logo file found")
            
        self.logo_preview.setAlignment(Qt.AlignCenter)
        self.logo_preview.setStyleSheet("background-color: #333; min-height: 80px; max-height: 80px;")
        options_layout.addRow("Logo Preview:", self.logo_preview)
        
        # Export format
        self.export_format = QComboBox()
        self.export_format.addItems(["Excel (.xlsx)", "PDF (.pdf)"])
        options_layout.addRow("Export Format:", self.export_format)
        
        # Additional export options
        self.include_images = QCheckBox("Include Item Images in Quote")
        options_layout.addRow(self.include_images)
        
        self.include_company_details = QCheckBox("Include Company Details")
        self.include_company_details.setChecked(True)
        options_layout.addRow(self.include_company_details)
        
        basic_layout.addWidget(options_group)
        
        # Company info group
        company_group = QGroupBox("Company Information")
        company_layout = QFormLayout(company_group)
        
        # Company info - pre-filled with company details
        company_details = Company.get_company_details()
        
        self.company_name = QLineEdit(company_details["name"])
        company_layout.addRow("Company Name:", self.company_name)
        
        self.company_address = QTextEdit()
        self.company_address.setMaximumHeight(60)
        self.company_address.setText(company_details["address"])
        company_layout.addRow("Address:", self.company_address)
        
        self.company_contact = QLineEdit(company_details["contact"])
        company_layout.addRow("Contact:", self.company_contact)
        
        basic_layout.addWidget(company_group)
        
        # Terms and conditions
        terms_group = QGroupBox("Terms and Conditions")
        terms_layout = QVBoxLayout(terms_group)
        
        self.include_terms = QCheckBox("Include Terms and Conditions")
        self.include_terms.setChecked(True)
        terms_layout.addWidget(self.include_terms)
        
        self.terms_text = QTextEdit()
        self.terms_text.setPlaceholderText("Enter terms and conditions here...")
        # Set default terms
        default_terms = "1. 50% advance payment before work begins.\n2. Balance payment on completion.\n3. Taxes as per government regulations.\n4. Delivery within 4-6 weeks from confirmation."
        self.terms_text.setText(default_terms)
        terms_layout.addWidget(self.terms_text)
        
        basic_layout.addWidget(terms_group)
        
        # Add basic tab
        tabs.addTab(basic_tab, "Basic Options")
        
        # Advanced tab (for future features)
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        
        # Add placeholder for future features
        advanced_layout.addWidget(QLabel("Advanced export options will be available in a future update."))
        
        # Add tabs to layout
        tabs.addTab(advanced_tab, "Advanced Options")
        
        # Add tabs to main layout
        layout.addWidget(tabs)
        
        # Export buttons
        buttons_layout = QHBoxLayout()
        
        export_btn = QPushButton("Export Quote")
        export_btn.clicked.connect(self.export_quote)
        buttons_layout.addWidget(export_btn)
        
        preview_btn = QPushButton("Update Preview")
        preview_btn.clicked.connect(self.update_preview)
        buttons_layout.addWidget(preview_btn)
        
        layout.addLayout(buttons_layout)
        
        # Preview area
        preview_group = QGroupBox("Export Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QTextEdit()
        self.preview_label.setReadOnly(True)
        self.preview_label.setStyleSheet("background-color: white; color: black; padding: 10px;")
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_group)
        
        # Add description at the bottom
        description = QLabel("Export your quote in Excel or PDF format with customized templates.")
        description.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(description)
    
    def on_template_changed(self, index):
        """Handle template selection change"""
        if index < 0:
            return
            
        template = self.export_controller.get_template(index)
        if template:
            # Update UI with template settings
            self.include_company_details.setChecked(template.get("include_company_details", True))
            self.include_images.setChecked(template.get("include_images", False))
            self.include_terms.setChecked(template.get("include_terms", True))
            
            if template.get("include_terms", True) and template.get("terms_text"):
                self.terms_text.setText(template.get("terms_text", ""))
            
            # Update preview
            self.update_preview()
    
    def create_template(self):
        """Create a new export template"""
        dialog = TemplateDialog(self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            template_data = dialog.get_template_data()
            
            # Add to template manager via controller
            index = self.export_controller.add_template(template_data)
            
            # Update template combo
            self.template_combo.blockSignals(True)
            self.template_combo.clear()
            self.template_combo.addItems(self.export_controller.get_template_names())
            self.template_combo.setCurrentIndex(index)
            self.template_combo.blockSignals(False)
            
            # Update UI with new template
            self.on_template_changed(index)
    
    def edit_template(self):
        """Edit the selected template"""
        index = self.template_combo.currentIndex()
        template = self.export_controller.get_template(index)
        
        if not template:
            return
        
        dialog = TemplateDialog(self, template)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            template_data = dialog.get_template_data()
            
            # Update in template manager via controller
            self.export_controller.update_template(index, template_data)
            
            # Update template combo
            self.template_combo.blockSignals(True)
            self.template_combo.clear()
            self.template_combo.addItems(self.export_controller.get_template_names())
            self.template_combo.setCurrentIndex(index)
            self.template_combo.blockSignals(False)
            
            # Update UI with edited template
            self.on_template_changed(index)
    
    def delete_template(self):
        """Delete the selected template"""
        index = self.template_combo.currentIndex()
        
        # Don't allow deleting the last template
        if self.template_combo.count() <= 1:
            QMessageBox.warning(self, "Warning", "Cannot delete the last template")
            return
        
        template = self.export_controller.get_template(index)
        if not template:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete the template '{template['name']}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Delete from template manager via controller
        self.export_controller.delete_template(index)
        
        # Update template combo
        self.template_combo.blockSignals(True)
        self.template_combo.clear()
        self.template_combo.addItems(self.export_controller.get_template_names())
        self.template_combo.setCurrentIndex(0)  # Select first template
        self.template_combo.blockSignals(False)
        
        # Update UI with new selection
        self.on_template_changed(0)
    
    def select_logo(self):
        """Open file dialog to select logo image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Logo Image", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if not file_path:
            return
            
        # Set logo path in export controller
        if self.export_controller.set_logo_path(file_path):
            # Update UI
            self.logo_path.setText(file_path)
            
            # Update logo preview
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale to fit preview area while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(200, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_preview.setPixmap(scaled_pixmap)
            else:
                self.logo_preview.setText("Invalid image")
            
            # Update preview
            self.update_preview()
        else:
            QMessageBox.warning(self, "Error", "Failed to set logo path. The file may not exist or is not accessible.")
    
    def export_quote(self):
        """Export quote based on selected format and template"""
        # Get current template index
        template_index = self.template_combo.currentIndex()
        
        # Get export options
        options = {
            "include_images": self.include_images.isChecked(),
            "logo_path": self.logo_path.text() or self.export_controller.get_logo_path(),
            "include_company_details": self.include_company_details.isChecked(),
            "company_name": self.company_name.text(),
            "company_address": self.company_address.toPlainText(),
            "company_contact": self.company_contact.text(),
            "include_terms": self.include_terms.isChecked(),
            "terms_text": self.terms_text.toPlainText(),
        }
        
        # Determine export format
        export_format = self.export_format.currentText()
        
        # Call appropriate export function
        if "Excel" in export_format:
            self.export_controller.export_to_excel(None, template_index, self, options)
        elif "PDF" in export_format:
            self.export_controller.export_to_pdf(None, template_index, self, options)
    
    def update_preview(self):
        """Update the preview area with a simplified view of the quote"""
        try:
            # Get project info
            project_info = self.project_controller.get_project_info()
            
            # Get current template
            template_index = self.template_combo.currentIndex()
            template = self.export_controller.get_template(template_index)
            
            # Get style options from template
            primary_color = template.get("primary_color", Company.PRIMARY_COLOR)
            font_family = template.get("font_family", "Arial")
            font_size = template.get("font_size", 10)
            header_text = template.get("header_text", "Interior Design Quote")
            footer_text = template.get("footer_text", "")
            
            # Start building the preview HTML
            preview_html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: {font_family}, sans-serif; color: black; font-size: {font_size}pt; }}
                    h1 {{ color: {primary_color}; text-align: center; }}
                    h2 {{ color: {primary_color}; }}
                    .header {{ background-color: {Company.HEADER_BG_COLOR}; padding: 15px; text-align: center; }}
                    .header h3 {{ color: {Company.HEADER_TEXT_COLOR}; margin: 5px 0; }}
                    .footer {{ background-color: #f8f8f8; padding: 10px; text-align: center; font-style: italic; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                    th {{ background-color: {primary_color}; color: white; text-align: left; padding: 5px; }}
                    td {{ border: 1px solid #ddd; padding: 5px; }}
                    .total {{ font-weight: bold; }}
                </style>
            </head>
            <body>
            """
            
            # Company details if enabled
            if self.include_company_details.isChecked():
                preview_html += f"""
                <div class="header">
                    <h3 style="color: {Company.HEADER_TEXT_COLOR};">{self.company_name.text()}</h3>
                    <p style="color: {Company.HEADER_TEXT_COLOR};">{self.company_address.toPlainText().replace("\n", "<br />")}<br>{self.company_contact.text()}</p>
                </div>
                """
            
            # Quote title
            preview_html += f"""
            <h1>{header_text}</h1>
            
            <h2>Project Details</h2>
            <table>
                <tr><td><strong>Project Name:</strong></td><td>{project_info.get("name", "")}</td></tr>
                <tr><td><strong>Client Name:</strong></td><td>{project_info.get("client_name", "")}</td></tr>
                <tr><td><strong>Site Address:</strong></td><td>{project_info.get("site_address", "")}</td></tr>
                <tr><td><strong>Contact:</strong></td><td>{project_info.get("contact_info", "")}</td></tr>
                <tr><td><strong>Project Type:</strong></td><td>{project_info.get("project_type", "")}</td></tr>
            </table>
            """
            
            # Get line items
            line_items = self.project_controller.get_line_items()
            
            # Check if there are any line items
            if not line_items:
                preview_html += "<p>No items added to quote yet.</p>"
            else:
                # Group items by room
                rooms = {}
                for item in line_items:
                    room = item["room"]
                    if room not in rooms:
                        rooms[room] = []
                    rooms[room].append(item)
                
                # Add each room with its items
                preview_html += "<h2>Quote Details</h2>"
                
                subtotal = 0
                for room, items in rooms.items():
                    preview_html += f"<h3>Room: {room}</h3>"
                    preview_html += """
                    <table>
                        <tr>
                            <th>Item</th>
                            <th>UOM</th>
                            <th>Dimensions</th>
                            <th>Quantity</th>
                            <th>Material</th>
                            <th>Rate (₹)</th>
                            <th>Amount (₹)</th>
                        </tr>
                    """
                    
                    room_total = 0
                    for item in items:
                        # Format dimensions based on UOM
                        if item["uom"] == "SFT":
                            dimensions = f"{item['length']} × {item['height']}"
                        elif item["uom"] == "RFT":
                            dimensions = f"{item['length']}"
                        else:
                            dimensions = "N/A"
                        
                        # Get material if available
                        material = ""
                        if "material" in item and item["material"].get("selected"):
                            material = item["material"]["selected"]
                        
                        preview_html += f"""
                        <tr>
                            <td>{item["item"]}</td>
                            <td>{item["uom"]}</td>
                            <td>{dimensions}</td>
                            <td>{item["quantity"]}</td>
                            <td>{material}</td>
                            <td>{item["rate"]}</td>
                            <td>₹{item["amount"]:.2f}</td>
                        </tr>
                        """
                        room_total += item["amount"]
                    
                    preview_html += f"""
                        <tr class="total">
                            <td colspan="6" style="text-align: right;">Room Total:</td>
                            <td>₹{room_total:.2f}</td>
                        </tr>
                    </table>
                    """
                    subtotal += room_total
                
                # Add summary
                settings = self.project_controller.get_settings()
                gst_amount = self.calculation_controller.calculate_gst()
                discount_amount = self.calculation_controller.calculate_discount()
                grand_total = self.calculation_controller.calculate_grand_total()
                
                preview_html += f"""
                <h2>Quote Summary</h2>
                <table>
                    <tr>
                        <td>Subtotal:</td>
                        <td>₹{subtotal:.2f}</td>
                    </tr>
                    <tr>
                        <td>GST ({settings.get("gst", 18)}%):</td>
                        <td>₹{gst_amount:.2f}</td>
                    </tr>
                    <tr>
                        <td>Discount ({settings.get("discount", 0)}%):</td>
                        <td>₹{discount_amount:.2f}</td>
                    </tr>
                    <tr class="total">
                        <td>Grand Total:</td>
                        <td>₹{grand_total:.2f}</td>
                    </tr>
                </table>
                """
                
                # Terms and conditions if enabled
                if self.include_terms.isChecked() and self.terms_text.toPlainText():
                    preview_html += f"""
                    <h2>Terms and Conditions</h2>
                    <p>{self.terms_text.toPlainText().replace("\n", "<br />")}</p>
                    """
                
                # Footer text if available
                if footer_text:
                    preview_html += f"""
                    <div class="footer">
                        <p>{footer_text}</p>
                    </div>
                    """
            
            preview_html += """
            </body>
            </html>
            """
            
            # Set preview HTML
            self.preview_label.setHtml(preview_html)
        except Exception as e:
            # Handle any errors gracefully
            error_message = f"Error generating preview: {str(e)}"
            self.preview_label.setHtml(f"<p style='color: red;'>{error_message}</p>")
            print(error_message)  # Also print to console for debugging
    
    def update_from_model(self):
        """Update UI from model data via controller"""
        # Update the preview
        self.update_preview()