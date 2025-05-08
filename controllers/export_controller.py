"""
Export Controller - Handles export operations for the project
"""
import os
import pandas as pd
import datetime
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QSettings
from models.company import Company

# For PDF export - check if ReportLab is available
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class TemplateManager:
    """Manager for export templates"""
    
    def __init__(self):
        """Initialize template manager"""
        self.templates = []
        self.load_templates()
    
    def load_templates(self):
        """Load templates from settings"""
        settings = QSettings("HomeProject", "InteriorDesignQuoteTool")
        templates = settings.value("export_templates", [])
        
        # Convert to proper format if needed
        if isinstance(templates, list):
            self.templates = templates
        else:
            self.templates = []
            
        # Add default template if none exists
        if not self.templates:
            self.add_default_template()
    
    def save_templates(self):
        """Save templates to settings"""
        settings = QSettings("HomeProject", "InteriorDesignQuoteTool")
        settings.setValue("export_templates", self.templates)
    
    def add_default_template(self):
        """Add a default template"""
        default_template = {
            "name": "Standard Template",
            "include_logo": True,
            "include_company_details": True,
            "include_images": False,
            "include_terms": True,
            "terms_text": ("1. 50% advance payment before work begins.\n"
                           "2. Balance payment on completion.\n"
                           "3. Taxes as per government regulations.\n"
                           "4. Delivery within 4-6 weeks from confirmation."),
            "primary_color": Company.PRIMARY_COLOR,
            "header_text": "Interior Design Quote",
            "footer_text": f"Thank you for choosing {Company.COMPANY_NAME}",
            "font_family": "Arial",
            "font_size": 10,
            "layout_type": 2  # Detailed layout
        }
        self.templates.append(default_template)
        self.save_templates()
    
    def add_template(self, template):
        """Add a new template"""
        self.templates.append(template)
        self.save_templates()
        return len(self.templates) - 1  # Return index of new template
    
    def update_template(self, index, template):
        """Update an existing template"""
        if 0 <= index < len(self.templates):
            self.templates[index] = template
            self.save_templates()
            return True
        return False
    
    def delete_template(self, index):
        """Delete a template by index"""
        if 0 <= index < len(self.templates):
            del self.templates[index]
            self.save_templates()
            return True
        return False
    
    def get_templates(self):
        """Get all templates"""
        return self.templates.copy()
    
    def get_template(self, index):
        """Get template by index"""
        if 0 <= index < len(self.templates):
            return self.templates[index].copy()
        return None
    
    def get_template_names(self):
        """Get list of template names"""
        return [template["name"] for template in self.templates]

class ExportController:
    """Controller for exporting project data"""
    
    def __init__(self, project_model, calculation_controller):
        """Initialize with Project model and Calculator"""
        self.project_model = project_model
        self.calculation_controller = calculation_controller
        self.template_manager = TemplateManager()
        self.logo_path = Company.get_logo_path()
    
    def export_to_excel(self, file_path=None, template_index=0, parent_widget=None, options=None):
        """Export project to Excel file"""
        if options is None:
            options = {}
        
        # Get project data
        project_data = self._prepare_project_data()
        
        # Check if there's anything to export
        if not project_data["line_items"]:
            if parent_widget:
                QMessageBox.warning(parent_widget, "Warning", "No line items to export. Add some items first.")
            return False
        
        # Get template
        template = self.template_manager.get_template(template_index) or {}
        
        # Get file path if not provided
        if not file_path:
            file_path, _ = QFileDialog.getSaveFileName(
                parent_widget, "Export to Excel", "", "Excel Files (*.xlsx)"
            )
            
        if not file_path:
            return False
            
        # Add .xlsx extension if not present
        if not file_path.lower().endswith('.xlsx'):
            file_path += '.xlsx'
        
        try:
            # Create a pandas Excel writer
            writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
            workbook = writer.book
            
            # Define formats
            primary_color = template.get("primary_color", Company.PRIMARY_COLOR)
            header_format = workbook.add_format({
                'bold': True, 
                'bg_color': primary_color, 
                'font_color': 'white'
            })
            
            bold_format = workbook.add_format({'bold': True})
            money_format = workbook.add_format({'num_format': '₹#,##0.00'})
            date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
            
            # Project info sheet
            project_info = project_data["project_info"]
            info_data = [
                ["Project Name", project_info["name"]],
                ["Client Name", project_info["client_name"]],
                ["Site Address", project_info["site_address"]],
                ["Contact", project_info["contact_info"]],
                ["Project Type", project_info["project_type"]],
                ["Date", datetime.datetime.now().strftime("%Y-%m-%d")],
            ]
            
            # Add company details if included
            include_company_details = options.get("include_company_details", 
                                                template.get("include_company_details", True))
            
            if include_company_details:
                company_details = Company.get_company_details()
                company_name = options.get("company_name", company_details["name"])
                company_address = options.get("company_address", company_details["address"])
                company_contact = options.get("company_contact", company_details["contact"])
                
                info_data.extend([
                    ["Company Name", company_name],
                    ["Company Address", company_address],
                    ["Company Contact", company_contact]
                ])
            
            info_df = pd.DataFrame(info_data, columns=["Field", "Value"])
            info_df.to_excel(writer, sheet_name='Project Info', index=False)
            
            # Format the project info sheet
            worksheet = writer.sheets['Project Info']
            for col_num, value in enumerate(info_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Add company logo if available and included
            include_logo = options.get("include_logo", template.get("include_logo", True))
            
            if include_logo:
                logo_path = options.get("logo_path", self.logo_path)
                if logo_path and os.path.exists(logo_path):
                    try:
                        worksheet.insert_image('D1', logo_path, {'x_offset': 10, 'y_offset': 10, 'x_scale': 0.5, 'y_scale': 0.5})
                    except Exception as e:
                        print(f"Error adding logo to Excel: {str(e)}")
            
            # Auto-adjust column widths
            worksheet.set_column(0, 0, 20)
            worksheet.set_column(1, 1, 40)
            
            # Quote details sheet with items grouped by room
            rooms = {}
            for item in project_data["line_items"]:
                room = item["room"]
                if room not in rooms:
                    rooms[room] = []
                rooms[room].append(item)
            
            if rooms:
                # Create sheet
                worksheet = workbook.add_worksheet('Quote Details')
                
                # Write headers
                headers = ["Room", "Item", "UOM", "Length", "Height", "Quantity", "Rate (₹)", "Amount (₹)"]
                for col, header in enumerate(headers):
                    worksheet.write(0, col, header, header_format)
                
                # Write data
                row = 1
                for room, items in rooms.items():
                    # Add room items
                    for item in items:
                        worksheet.write(row, 0, room)
                        worksheet.write(row, 1, item["item"])
                        worksheet.write(row, 2, item["uom"])
                        worksheet.write(row, 3, item["length"])
                        worksheet.write(row, 4, item["height"])
                        worksheet.write(row, 5, item["quantity"])
                        worksheet.write(row, 6, item["rate"])
                        worksheet.write(row, 7, item["amount"], money_format)
                        row += 1
                
                # Format columns
                worksheet.set_column(0, 0, 15)  # Room
                worksheet.set_column(1, 1, 30)  # Item
                worksheet.set_column(2, 2, 8)   # UOM
                worksheet.set_column(3, 5, 10)  # Dimensions & Quantity
                worksheet.set_column(6, 7, 12)  # Rate & Amount
            
            # Summary sheet
            settings = project_data["settings"]
            room_totals = self.calculation_controller.calculate_room_totals()
            
            if room_totals:
                # Create sheet
                worksheet = workbook.add_worksheet('Summary')
                
                # Write headers
                worksheet.write(0, 0, "Item", header_format)
                worksheet.write(0, 1, "Amount (₹)", header_format)
                
                # Write room totals
                row = 1
                subtotal = 0
                
                for room, amount in room_totals.items():
                    worksheet.write(row, 0, room)
                    worksheet.write(row, 1, amount, money_format)
                    subtotal += amount
                    row += 1
                
                # Write summary
                worksheet.write(row, 0, "Subtotal", bold_format)
                worksheet.write(row, 1, subtotal, money_format)
                row += 1
                
                gst_amount = self.calculation_controller.calculate_gst()
                worksheet.write(row, 0, f"GST ({settings['gst']}%)", bold_format)
                worksheet.write(row, 1, gst_amount, money_format)
                row += 1
                
                discount_amount = self.calculation_controller.calculate_discount()
                worksheet.write(row, 0, f"Discount ({settings['discount']}%)", bold_format)
                worksheet.write(row, 1, discount_amount, money_format)
                row += 1
                
                grand_total = self.calculation_controller.calculate_grand_total()
                worksheet.write(row, 0, "Grand Total", bold_format)
                worksheet.write(row, 1, grand_total, money_format)
                
                # Format columns
                worksheet.set_column(0, 0, 25)
                worksheet.set_column(1, 1, 15)
            
            # Save the Excel file
            writer.close()
            
            if parent_widget:
                QMessageBox.information(
                    parent_widget, "Success", "Project exported to Excel successfully"
                )
                
            return True
        
        except Exception as e:
            if parent_widget:
                QMessageBox.critical(parent_widget, "Error", f"Error exporting to Excel: {str(e)}")
            return False
    
    def export_to_pdf(self, file_path=None, template_index=0, parent_widget=None, options=None):
        """Export project to PDF file"""
        if not REPORTLAB_AVAILABLE:
            if parent_widget:
                QMessageBox.critical(
                    parent_widget, "Error", 
                    "PDF export requires ReportLab library. Please install it using 'pip install reportlab'"
                )
            return False
            
        if options is None:
            options = {}
        
        # Get project data
        project_data = self._prepare_project_data()
        
        # Check if there's anything to export
        if not project_data["line_items"]:
            if parent_widget:
                QMessageBox.warning(
                    parent_widget, "Warning", 
                    "No line items to export. Add some items first."
                )
            return False
        
        # Get template
        template = self.template_manager.get_template(template_index) or {}
        
        # Get file path if not provided
        if not file_path:
            file_path, _ = QFileDialog.getSaveFileName(
                parent_widget, "Export to PDF", "", "PDF Files (*.pdf)"
            )
            
        if not file_path:
            return False
            
        # Add .pdf extension if not present
        if not file_path.lower().endswith('.pdf'):
            file_path += '.pdf'
        
        try:
            # Get primary color from template
            primary_color_hex = template.get("primary_color", Company.PRIMARY_COLOR)
            # Convert hex to RGB color
            primary_color = colors.HexColor(primary_color_hex)
            
            # Create the PDF document
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            
            # Font options from template
            font_family = template.get("font_family", "Helvetica")
            font_size_base = template.get("font_size", 10)
            
            # Custom styles
            title_style = ParagraphStyle(
                'Title',
                parent=styles["Heading1"],
                fontName=font_family+"-Bold",
                fontSize=font_size_base + 8,
                alignment=1,  # Center
                textColor=primary_color
            )
            
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles["Heading2"],
                fontName=font_family+"-Bold",
                fontSize=font_size_base + 4,
                textColor=primary_color
            )
            
            normal_style = ParagraphStyle(
                'Normal',
                parent=styles["Normal"],
                fontName=font_family,
                fontSize=font_size_base
            )
            
            company_style = ParagraphStyle(
                'Company',
                parent=normal_style,
                fontSize=font_size_base + 2,
                alignment=1  # Center
            )
            
            room_style = ParagraphStyle(
                'Room',
                parent=styles['Heading3'],
                fontName=font_family+"-Bold",
                fontSize=font_size_base + 2,
                textColor=primary_color
            )
            
            # Logo
            include_logo = options.get("include_logo", template.get("include_logo", True))
            
            if include_logo:
                logo_path = options.get("logo_path", self.logo_path)
                if logo_path and os.path.exists(logo_path):
                    try:
                        img = Image(logo_path, width=2*inch, height=1*inch)
                        img.hAlign = 'CENTER'
                        elements.append(img)
                        elements.append(Spacer(1, 0.2*inch))
                    except Exception as e:
                        print(f"Error adding logo: {str(e)}")
            
            # Company details if included
            include_company_details = options.get("include_company_details", 
                                                template.get("include_company_details", True))
            
            if include_company_details:
                company_details = Company.get_company_details()
                company_name = options.get("company_name", company_details["name"])
                if company_name:
                    elements.append(Paragraph(company_name, company_style))
                
                company_address = options.get("company_address", company_details["address"])
                if company_address:
                    elements.append(Paragraph(company_address.replace("\n", "<br />"), company_style))
                
                company_contact = options.get("company_contact", company_details["contact"])
                if company_contact:
                    elements.append(Paragraph(company_contact, company_style))
                
                elements.append(Spacer(1, 0.2*inch))
            
            # Title
            header_text = template.get("header_text", "Interior Design Quote")
            elements.append(Paragraph(header_text, title_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Project Info Table
            project_info = project_data["project_info"]
            project_data_table = [
                ["Project Name:", project_info["name"]],
                ["Client Name:", project_info["client_name"]],
                ["Site Address:", project_info["site_address"]],
                ["Contact:", project_info["contact_info"]],
                ["Project Type:", project_info["project_type"]],
                ["Date:", datetime.datetime.now().strftime("%Y-%m-%d")],
            ]
            
            table = Table(project_data_table, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('FONTNAME', (0, 0), (0, -1), font_family+'-Bold'),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.5*inch))
            
            # Group line items by room
            rooms = {}
            for item in project_data["line_items"]:
                room = item["room"]
                if room not in rooms:
                    rooms[room] = []
                rooms[room].append(item)
            
            # Create tables for each room
            if not rooms:
                elements.append(Paragraph("No items added to quote yet.", normal_style))
            else:
                for room, items in rooms.items():
                    elements.append(Paragraph(f"Room: {room}", room_style))
                    elements.append(Spacer(1, 0.1*inch))
                    
                    # Table data
                    data = [["Item", "UOM", "Length", "Height", "Quantity", "Rate (₹)", "Amount (₹)"]]
                    
                    room_total = 0
                    for item in items:
                        data.append([
                            item["item"],
                            item["uom"],
                            str(item["length"]) if item["length"] else "N/A",
                            str(item["height"]) if item["height"] else "N/A",
                            str(item["quantity"]),
                            f"₹{item['rate']:.2f}",
                            f"₹{item['amount']:.2f}"
                        ])
                        room_total += item["amount"]
                    
                    # Add room total row
                    data.append(["", "", "", "", "", "Room Total:", f"₹{room_total:.2f}"])
                    
                    # Create table
                    col_widths = [2.5*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.8*inch, 1*inch]
                    table = Table(data, colWidths=col_widths)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('PADDING', (0, 0), (-1, -1), 4),
                        ('FONTNAME', (0, 0), (-1, 0), font_family+'-Bold'),
                        ('FONTNAME', (-2, -1), (-1, -1), font_family+'-Bold'),
                        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                    ]))
                    
                    elements.append(table)
                    elements.append(Spacer(1, 0.3*inch))
                
                # Summary
                elements.append(Paragraph("Quote Summary", subtitle_style))
                elements.append(Spacer(1, 0.1*inch))
                
                settings = project_data["settings"]
                subtotal = self.calculation_controller.calculate_subtotal()
                gst_amount = self.calculation_controller.calculate_gst()
                discount_amount = self.calculation_controller.calculate_discount()
                grand_total = self.calculation_controller.calculate_grand_total()
                
                summary_data = [
                    ["Description", "Amount (₹)"],
                    ["Subtotal", f"₹{subtotal:.2f}"],
                    [f"GST ({settings['gst']}%)", f"₹{gst_amount:.2f}"],
                    [f"Discount ({settings['discount']}%)", f"₹{discount_amount:.2f}"],
                    ["Grand Total", f"₹{grand_total:.2f}"]
                ]
                
                table = Table(summary_data, colWidths=[4*inch, 2*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('PADDING', (0, 0), (-1, -1), 6),
                    ('FONTNAME', (0, 0), (-1, 0), font_family+'-Bold'),
                    ('FONTNAME', (0, -1), (-1, -1), font_family+'-Bold'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ]))
                
                elements.append(table)
                
                # Terms and conditions
                include_terms = options.get("include_terms", template.get("include_terms", True))
                terms_text = options.get("terms_text", template.get("terms_text", ""))
                
                if include_terms and terms_text:
                    elements.append(Spacer(1, 0.5*inch))
                    elements.append(Paragraph("Terms and Conditions", subtitle_style))
                    elements.append(Spacer(1, 0.1*inch))
                    elements.append(Paragraph(terms_text, normal_style))
                
                # Footer text if available
                footer_text = template.get("footer_text", "")
                if footer_text:
                    elements.append(Spacer(1, 0.5*inch))
                    footer_style = ParagraphStyle(
                        'Footer',
                        parent=normal_style,
                        alignment=1,  # Center
                        fontSize=font_size_base - 1,
                        textColor=colors.darkgrey
                    )
                    elements.append(Paragraph(footer_text, footer_style))
            
            # Build PDF
            doc.build(elements)
            
            if parent_widget:
                QMessageBox.information(
                    parent_widget, "Success", "Project exported to PDF successfully"
                )
                
            return True
            
        except Exception as e:
            if parent_widget:
                QMessageBox.critical(parent_widget, "Error", f"Error exporting to PDF: {str(e)}")
            return False
    
    def _prepare_project_data(self):
        """Prepare project data for export"""
        project_info = self.project_model.get_project_info()
        rooms = self.project_model.get_rooms()
        line_items = self.project_model.get_line_items()
        settings = self.project_model.get_settings()
        
        return {
            "project_info": project_info,
            "rooms": rooms,
            "line_items": line_items,
            "settings": settings
        }
    
    def get_templates(self):
        """Get all available templates"""
        return self.template_manager.get_templates()
    
    def get_template(self, index):
        """Get template by index"""
        return self.template_manager.get_template(index)
    
    def get_template_names(self):
        """Get list of template names"""
        return self.template_manager.get_template_names()
    
    def add_template(self, template_data):
        """Add a new template"""
        return self.template_manager.add_template(template_data)
    
    def update_template(self, index, template_data):
        """Update an existing template"""
        return self.template_manager.update_template(index, template_data)
    
    def delete_template(self, index):
        """Delete a template"""
        return self.template_manager.delete_template(index)
    
    def set_logo_path(self, path):
        """Set logo path for exports"""
        if os.path.exists(path):
            self.logo_path = path
            return True
        return False
    
    def get_logo_path(self):
        """Get currently set logo path"""
        return self.logo_path