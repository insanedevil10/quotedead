
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import traceback
from models.item import LineItem, FurnitureItem
from utils.quote_calculator import QuoteCalculator
from utils.storage_manager import StorageManager
from utils.rate_card_excel import RateCardExcel
from utils.template_manager import TemplateManager
from export_utils import export_quote_to_pdf
from export_utils_excel import export_quote_to_excel

class QuoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interior Quote Tool")
        self.root.geometry("1200x800")
        
        # Initialize storage and calculator
        self.storage_manager = StorageManager()
        self.quote_calculator = QuoteCalculator()
        self.rate_card = RateCardExcel()
        self.template_manager = TemplateManager()
        
        # Project data
        self.project_data = {
            "client_name": "",
            "location": "",
            "project_type": "",
            "area": 0
        }
        
        self.rooms = []
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.project_frame = ttk.Frame(self.notebook)
        self.rooms_frame = ttk.Frame(self.notebook)
        self.scope_frame = ttk.Frame(self.notebook)
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.export_frame = ttk.Frame(self.notebook)
        self.rate_card_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.project_frame, text="Project Info")
        self.notebook.add(self.rooms_frame, text="Rooms")
        self.notebook.add(self.scope_frame, text="Scope of Work")
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.notebook.add(self.export_frame, text="Export")
        self.notebook.add(self.rate_card_frame, text="Rate Card")
        self.notebook.pack(fill='both', expand=True)

        # Build each tab
        self.build_project_info_tab()
        self.build_rooms_tab()
        self.build_scope_tab()
        self.build_dashboard_tab()
        self.build_export_tab()
        self.build_rate_card_tab()

    def build_project_info_tab(self):
        frame = ttk.LabelFrame(self.project_frame, text="Project Details")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Client name
        ttk.Label(frame, text="Client Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.client_name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.client_name_var).grid(row=0, column=1, padx=5, pady=5)
        
        # Location
        ttk.Label(frame, text="Location:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.location_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.location_var).grid(row=1, column=1, padx=5, pady=5)
        
        # Project type
        ttk.Label(frame, text="Project Type:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.project_type_var = tk.StringVar()
        project_types = ["Residential", "Commercial", "Office", "Retail", "Other"]
        ttk.Combobox(frame, textvariable=self.project_type_var, values=project_types).grid(row=2, column=1, padx=5, pady=5)
        
        # Area
        ttk.Label(frame, text="Total Area (sq ft):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.area_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.area_var).grid(row=3, column=1, padx=5, pady=5)
        
        # Save button
        ttk.Button(frame, text="Save Project Info", command=self.save_project_info).grid(row=4, column=0, columnspan=2, pady=20)

    def save_project_info(self):
        try:
            self.project_data["client_name"] = self.client_name_var.get()
            self.project_data["location"] = self.location_var.get()
            self.project_data["project_type"] = self.project_type_var.get()
            
            # Validate area is a number
            try:
                self.project_data["area"] = float(self.area_var.get())
            except ValueError:
                messagebox.showerror("Invalid Input", "Area must be a number")
                return
                
            messagebox.showinfo("Success", "Project information saved successfully")
            # Move to the next tab
            self.notebook.select(1)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project information: {str(e)}")

    def build_rooms_tab(self):
        # Left panel for room list
        left_frame = ttk.Frame(self.rooms_frame)
        left_frame.pack(side="left", fill="both", expand=False, padx=10, pady=10)
        
        ttk.Label(left_frame, text="Rooms").pack(anchor="w")
        
        # Room list with scrollbar
        scroll = ttk.Scrollbar(left_frame)
        self.room_listbox = tk.Listbox(left_frame, width=25, yscrollcommand=scroll.set)
        scroll.config(command=self.room_listbox.yview)
        self.room_listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        # Button frame
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(btn_frame, text="Add Room", command=self.add_room).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Edit", command=self.edit_room).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_room).pack(side="left", padx=2)
        
        # Right panel for room details
        self.room_details_frame = ttk.LabelFrame(self.rooms_frame, text="Room Details")
        self.room_details_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Room name field
        ttk.Label(self.room_details_frame, text="Room Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.room_name_var = tk.StringVar()
        ttk.Entry(self.room_details_frame, textvariable=self.room_name_var).grid(row=0, column=1, padx=5, pady=5)
        
        # Room type field
        ttk.Label(self.room_details_frame, text="Room Type:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.room_type_var = tk.StringVar()
        room_types = ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Office", "Other"]
        ttk.Combobox(self.room_details_frame, textvariable=self.room_type_var, values=room_types).grid(row=1, column=1, padx=5, pady=5)
        
        # Dimensions
        ttk.Label(self.room_details_frame, text="Length (ft):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.room_length_var = tk.StringVar()
        ttk.Entry(self.room_details_frame, textvariable=self.room_length_var).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self.room_details_frame, text="Width (ft):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.room_width_var = tk.StringVar()
        ttk.Entry(self.room_details_frame, textvariable=self.room_width_var).grid(row=3, column=1, padx=5, pady=5)
        
        # Save button
        ttk.Button(self.room_details_frame, text="Save Room", command=self.save_room).grid(row=4, column=0, columnspan=2, pady=20)

    def add_room(self):
        # Clear existing fields for new entry
        self.room_name_var.set("")
        self.room_type_var.set("")
        self.room_length_var.set("")
        self.room_width_var.set("")
        self.room_details_frame.config(text="Add New Room")
        
    def edit_room(self):
        selected = self.room_listbox.curselection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a room to edit")
            return
            
        idx = selected[0]
        room = self.rooms[idx]
        
        self.room_name_var.set(room.get("name", ""))
        self.room_type_var.set(room.get("type", ""))
        self.room_length_var.set(str(room.get("length", "")))
        self.room_width_var.set(str(room.get("width", "")))
        self.room_details_frame.config(text=f"Edit Room: {room.get('name', '')}")

    def delete_room(self):
        selected = self.room_listbox.curselection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a room to delete")
            return
            
        idx = selected[0]
        room_name = self.rooms[idx].get("name", "Unknown")
        
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {room_name}?")
        if confirm:
            del self.rooms[idx]
            self.update_room_list()
            messagebox.showinfo("Success", f"{room_name} has been deleted")

    def save_room(self):
        try:
            room_data = {
                "name": self.room_name_var.get(),
                "type": self.room_type_var.get(),
                "items": []
            }
            
            # Validate numeric inputs
            try:
                if self.room_length_var.get():
                    room_data["length"] = float(self.room_length_var.get())
                if self.room_width_var.get():
                    room_data["width"] = float(self.room_width_var.get())
                    
                # Calculate area if both dimensions provided
                if "length" in room_data and "width" in room_data:
                    room_data["area"] = room_data["length"] * room_data["width"]
            except ValueError:
                messagebox.showerror("Invalid Input", "Length and width must be numbers")
                return
                
            # Check if we're editing an existing room
            selected = self.room_listbox.curselection()
            if selected:
                idx = selected[0]
                # Preserve the items from the existing room
                room_data["items"] = self.rooms[idx].get("items", [])
                self.rooms[idx] = room_data
            else:
                # Add as new room
                self.rooms.append(room_data)
                
            self.update_room_list()
            messagebox.showinfo("Success", f"Room '{room_data['name']}' saved successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save room: {str(e)}")

    def update_room_list(self):
        self.room_listbox.delete(0, tk.END)
        for room in self.rooms:
            self.room_listbox.insert(tk.END, room.get("name", "Unnamed Room"))

    def build_scope_tab(self):
        # Left panel for room selection
        left_frame = ttk.Frame(self.scope_frame)
        left_frame.pack(side="left", fill="both", expand=False, padx=10, pady=10)
        
        ttk.Label(left_frame, text="Select Room:").pack(anchor="w")
        
        # Room selection list
        scroll = ttk.Scrollbar(left_frame)
        self.scope_room_listbox = tk.Listbox(left_frame, width=25, yscrollcommand=scroll.set)
        scroll.config(command=self.scope_room_listbox.yview)
        self.scope_room_listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.scope_room_listbox.bind('<<ListboxSelect>>', self.load_room_items)
        
        # Right panel for items
        right_frame = ttk.Frame(self.scope_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Items table (using Treeview)
        ttk.Label(right_frame, text="Room Items:").pack(anchor="w")
        
        # Item control buttons
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(btn_frame, text="Add Item", command=self.add_item).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Edit Item", command=self.edit_item).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Remove Item", command=self.remove_item).pack(side="left", padx=2)
        
        # Items table
        columns = ("name", "category", "quantity", "uom", "cost")
        self.items_tree = ttk.Treeview(right_frame, columns=columns, show="headings")
        
        # Define column headings
        self.items_tree.heading("name", text="Item Name")
        self.items_tree.heading("category", text="Category")
        self.items_tree.heading("quantity", text="Quantity")
        self.items_tree.heading("uom", text="UOM")
        self.items_tree.heading("cost", text="Unit Cost")
        
        # Define column widths
        self.items_tree.column("name", width=150)
        self.items_tree.column("category", width=100)
        self.items_tree.column("quantity", width=80)
        self.items_tree.column("uom", width=80)
        self.items_tree.column("cost", width=100)
        
        self.items_tree.pack(fill="both", expand=True)

    def load_room_items(self, event=None):
        selected = self.scope_room_listbox.curselection()
        if not selected:
            return
            
        idx = selected[0]
        room = self.rooms[idx]
        
        # Clear existing items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
            
        # Add room items to the treeview
        for item in room.get("items", []):
            self.items_tree.insert("", "end", values=(
                item.get("name", ""),
                item.get("category", ""),
                item.get("quantity", ""),
                item.get("uom", ""),
                item.get("unit_cost", "")
            ))

    def add_item(self):
        selected = self.scope_room_listbox.curselection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a room first")
            return
            
        # Create a popup window for item entry
        self.item_window = tk.Toplevel(self.root)
        self.item_window.title("Add Item")
        self.item_window.geometry("400x400")
        
        # Item details form
        ttk.Label(self.item_window, text="Item Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.item_name_var = tk.StringVar()
        ttk.Entry(self.item_window, textvariable=self.item_name_var).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.item_window, text="Category:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.item_category_var = tk.StringVar()
        categories = ["Furniture", "Flooring", "Paint", "Electrical", "Plumbing", "Accessories", "Labor", "Other"]
        ttk.Combobox(self.item_window, textvariable=self.item_category_var, values=categories).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.item_window, text="Quantity:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.item_quantity_var = tk.StringVar()
        ttk.Entry(self.item_window, textvariable=self.item_quantity_var).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self.item_window, text="Unit of Measure:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.item_uom_var = tk.StringVar()
        uoms = ["Each", "Square Feet", "Linear Feet", "Hours", "Days"]
        ttk.Combobox(self.item_window, textvariable=self.item_uom_var, values=uoms).grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(self.item_window, text="Unit Cost (₹):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.item_cost_var = tk.StringVar()
        ttk.Entry(self.item_window, textvariable=self.item_cost_var).grid(row=4, column=1, padx=5, pady=5)
        
        # Add-ons frame
        addon_frame = ttk.LabelFrame(self.item_window, text="Add-ons (optional)")
        addon_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="we")
        
        ttk.Label(addon_frame, text="Premium Material:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.premium_var = tk.StringVar(value="0")
        ttk.Entry(addon_frame, textvariable=self.premium_var, width=5).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(addon_frame, text="% extra").grid(row=0, column=2, padx=0, pady=2, sticky="w")
        
        ttk.Label(addon_frame, text="Custom Design:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.custom_var = tk.StringVar(value="0")
        ttk.Entry(addon_frame, textvariable=self.custom_var, width=5).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(addon_frame, text="% extra").grid(row=1, column=2, padx=0, pady=2, sticky="w")
        
        # Save button
        ttk.Button(self.item_window, text="Save Item", command=self.save_item).grid(row=6, column=0, columnspan=2, pady=20)

    def save_item(self):
        try:
            # Get selected room
            room_idx = self.scope_room_listbox.curselection()[0]
            
            # Create item dict
            item_data = {
                "name": self.item_name_var.get(),
                "category": self.item_category_var.get(),
                "uom": self.item_uom_var.get(),
                "addons": {}
            }
            
            # Validate numeric inputs
            try:
                item_data["quantity"] = float(self.item_quantity_var.get())
                item_data["unit_cost"] = float(self.item_cost_var.get())
                
                # Add any non-zero add-ons
                premium = float(self.premium_var.get() or 0)
                custom = float(self.custom_var.get() or 0)
                
                if premium > 0:
                    item_data["addons"]["premium"] = premium
                if custom > 0:
                    item_data["addons"]["custom"] = custom
                    
                # Calculate total cost with add-ons
                total = item_data["quantity"] * item_data["unit_cost"]
                addon_multiplier = 1.0
                for addon_value in item_data["addons"].values():
                    addon_multiplier += (addon_value / 100.0)
                item_data["total_cost"] = total * addon_multiplier
                
            except ValueError:
                messagebox.showerror("Invalid Input", "Quantity, cost, and add-ons must be numbers")
                return
                
            # Add item to room
            self.rooms[room_idx]["items"].append(item_data)
            
            # Update the UI
            self.load_room_items()
            self.item_window.destroy()
            messagebox.showinfo("Success", f"Item '{item_data['name']}' added successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save item: {str(e)}")

    def edit_item(self):
        # Similar to add_item but pre-populates fields with selected item data
        # Implementation left as an exercise
        messagebox.showinfo("Not Implemented", "Edit item functionality not yet implemented")

    def remove_item(self):
        # Get selected room and item
        room_idx = self.scope_room_listbox.curselection()
        if not room_idx:
            messagebox.showinfo("Selection Required", "Please select a room first")
            return
            
        selected_item = self.items_tree.selection()
        if not selected_item:
            messagebox.showinfo("Selection Required", "Please select an item to remove")
            return
            
        # Get item index - this depends on the order in the treeview matching the order in the data
        item_idx = self.items_tree.index(selected_item[0])
        
        # Remove the item
        room = self.rooms[room_idx[0]]
        item_name = room["items"][item_idx]["name"]
        
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {item_name}?")
        if confirm:
            del room["items"][item_idx]
            self.load_room_items()
            messagebox.showinfo("Success", f"{item_name} has been removed")

    def build_dashboard_tab(self):
        # Create frames for different sections
        summary_frame = ttk.LabelFrame(self.dashboard_frame, text="Project Summary")
        summary_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Project info summary
        info_frame = ttk.Frame(summary_frame)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        self.summary_client_label = ttk.Label(info_frame, text="Client: Not set")
        self.summary_client_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        self.summary_location_label = ttk.Label(info_frame, text="Location: Not set")
        self.summary_location_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        self.summary_type_label = ttk.Label(info_frame, text="Project Type: Not set")
        self.summary_type_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        
        self.summary_area_label = ttk.Label(info_frame, text="Total Area: 0 sq ft")
        self.summary_area_label.grid(row=3, column=0, sticky="w", padx=5, pady=2)
        
        # Room costs table
        ttk.Label(summary_frame, text="Room Costs:").pack(anchor="w", padx=10, pady=5)
        
        # Treeview for room costs
        columns = ("room", "items", "total")
        self.room_costs_tree = ttk.Treeview(summary_frame, columns=columns, show="headings", height=6)
        
        self.room_costs_tree.heading("room", text="Room")
        self.room_costs_tree.heading("items", text="Items")
        self.room_costs_tree.heading("total", text="Total Cost")
        
        self.room_costs_tree.column("room", width=150)
        self.room_costs_tree.column("items", width=80)
        self.room_costs_tree.column("total", width=150)
        
        self.room_costs_tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Total cost
        total_frame = ttk.Frame(summary_frame)
        total_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(total_frame, text="Grand Total:").pack(side="left")
        self.grand_total_label = ttk.Label(total_frame, text="₹0", font=("Helvetica", 12, "bold"))
        self.grand_total_label.pack(side="left", padx=10)
        
        # Refresh button
        ttk.Button(self.dashboard_frame, text="Refresh Dashboard", command=self.refresh_dashboard).pack(pady=10)

    def refresh_dashboard(self):
        # Update project info summary
        self.summary_client_label.config(text=f"Client: {self.project_data.get('client_name', 'Not set')}")
        self.summary_location_label.config(text=f"Location: {self.project_data.get('location', 'Not set')}")
        self.summary_type_label.config(text=f"Project Type: {self.project_data.get('project_type', 'Not set')}")
        self.summary_area_label.config(text=f"Total Area: {self.project_data.get('area', 0)} sq ft")
        
        # Clear existing room data
        for item in self.room_costs_tree.get_children():
            self.room_costs_tree.delete(item)
            
        # Add room cost data
        grand_total = 0
        for room in self.rooms:
            room_total = sum(item.get("total_cost", 0) for item in room.get("items", []))
            grand_total += room_total
            
            self.room_costs_tree.insert("", "end", values=(
                room.get("name", "Unnamed"),
                len(room.get("items", [])),
                f"₹{room_total:,.2f}"
            ))
            
        # Update grand total
        self.grand_total_label.config(text=f"₹{grand_total:,.2f}")

    def build_export_tab(self):
        frame = ttk.Frame(self.export_frame)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="Export Quote", font=("Helvetica", 14)).pack(pady=10)
        
        # Export options
        options_frame = ttk.LabelFrame(frame, text="Export Options")
        options_frame.pack(fill="x", pady=10)
        
        # PDF Export
        pdf_frame = ttk.Frame(options_frame)
        pdf_frame.pack(fill="x", pady=10, padx=10)
        
        ttk.Label(pdf_frame, text="PDF Export:").pack(side="left")
        ttk.Button(pdf_frame, text="Export to PDF", command=self.export_pdf).pack(side="left", padx=10)
        
        # Excel Export
        excel_frame = ttk.Frame(options_frame)
        excel_frame.pack(fill="x", pady=10, padx=10)
        
        ttk.Label(excel_frame, text="Excel Export:").pack(side="left")
        ttk.Button(excel_frame, text="Export to Excel", command=self.export_excel).pack(side="left", padx=10)

    def export_pdf(self):
        if not self.rooms:
            messagebox.showwarning("No Data", "There are no rooms to export")
            return
            
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            
            if filepath:
                export_quote_to_pdf(filepath, self.project_data, self.rooms, self.quote_calculator)
                messagebox.showinfo("Export Successful", f"Quote exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export PDF: {str(e)}")

    def export_excel(self):
        if not self.rooms:
            messagebox.showwarning("No Data", "There are no rooms to export")
            return
            
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if filepath:
                export_quote_to_excel(filepath, self.project_data, self.rooms, self.quote_calculator)
                messagebox.showinfo("Export Successful", f"Quote exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export Excel: {str(e)}")

    def build_rate_card_tab(self):
        frame = ttk.Frame(self.rate_card_frame)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="Rate Card Management", font=("Helvetica", 14)).pack(pady=10)
        
        # Rate card options
        options_frame = ttk.Frame(frame)
        options_frame.pack(fill="x", pady=10)
        
        ttk.Button(options_frame, text="Load Rate Card", command=self.load_rate_card).pack(side="left", padx=5)
        ttk.Button(options_frame, text="Save Rate Card", command=self.save_rate_card).pack(side="left", padx=5)
        ttk.Button(options_frame, text="Reset to Default", command=self.reset_rate_card).pack(side="left", padx=5)
        
        # Rate card table
        ttk.Label(frame, text="Rate Card Items:").pack(anchor="w", pady=5)
        
        # Treeview for rate card items
        columns = ("category", "item", "uom", "rate")
        self.rate_card_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        self.rate_card_tree.heading("category", text="Category")
        self.rate_card_tree.heading("item", text="Item")
        self.rate_card_tree.heading("uom", text="UOM")
        self.rate_card_tree.heading("rate", text="Rate (₹)")
        
        self.rate_card_tree.column("category", width=150)
        self.rate_card_tree.column("item", width=200)
        self.rate_card_tree.column("uom", width=100)
        self.rate_card_tree.column("rate", width=100)
        
        self.rate_card_tree.pack(fill="both", expand=True, pady=5)
        
        # Item management buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Add Item", command=self.add_rate_card_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Edit Item", command=self.edit_rate_card_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Item", command=self.delete_rate_card_item).pack(side="left", padx=5)

    def load_rate_card(self):
        try:
            filepath = filedialog.askopenfilename(
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if filepath:
                self.rate_card.load_from_excel(filepath)
                self.refresh_rate_card_display()
                messagebox.showinfo("Success", "Rate card loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load rate card: {str(e)}")

    def save_rate_card(self):
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if filepath:
                self.rate_card.save_to_excel(filepath)
                messagebox.showinfo("Success", f"Rate card saved to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save rate card: {str(e)}")

    def reset_rate_card(self):
        confirm = messagebox.askyesno("Confirm Reset", "Are you sure you want to reset to the default rate card?")
        if confirm:
            try:
                self.rate_card.load_default_rates()
                self.refresh_rate_card_display()
                messagebox.showinfo("Success", "Rate card reset to defaults")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset rate card: {str(e)}")

    def refresh_rate_card_display(self):
        # Clear existing items
        for item in self.rate_card_tree.get_children():
            self.rate_card_tree.delete(item)
            
        # Add rate card items
        for category, items in self.rate_card.get_all_rates().items():
            for item_name, details in items.items():
                self.rate_card_tree.insert("", "end", values=(
                    category,
                    item_name,
                    details.get("uom", ""),
                    details.get("rate", "")
                ))

    def add_rate_card_item(self):
        self.rate_item_window = tk.Toplevel(self.root)
        self.rate_item_window.title("Add Rate Card Item")
        self.rate_item_window.geometry("400x250")
        
        # Rate card item form
        ttk.Label(self.rate_item_window, text="Category:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.rate_category_var = tk.StringVar()
        categories = ["Furniture", "Flooring", "Paint", "Electrical", "Plumbing", "Accessories", "Labor", "Other"]
        ttk.Combobox(self.rate_item_window, textvariable=self.rate_category_var, values=categories).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.rate_item_window, text="Item Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.rate_item_name_var = tk.StringVar()
        ttk.Entry(self.rate_item_window, textvariable=self.rate_item_name_var).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.rate_item_window, text="Unit of Measure:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.rate_uom_var = tk.StringVar()
        uoms = ["Each", "Square Feet", "Linear Feet", "Hours", "Days"]
        ttk.Combobox(self.rate_item_window, textvariable=self.rate_uom_var, values=uoms).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self.rate_item_window, text="Rate (₹):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.rate_amount_var = tk.StringVar()
        ttk.Entry(self.rate_item_window, textvariable=self.rate_amount_var).grid(row=3, column=1, padx=5, pady=5)
        
        # Save button
        ttk.Button(self.rate_item_window, text="Save Item", command=self.save_rate_card_item).grid(row=4, column=0, columnspan=2, pady=20)

    def save_rate_card_item(self):
        try:
            category = self.rate_category_var.get()
            item_name = self.rate_item_name_var.get()
            uom = self.rate_uom_var.get()
            
            try:
                rate = float(self.rate_amount_var.get())
            except ValueError:
                messagebox.showerror("Invalid Input", "Rate must be a number")
                return
                
            # Add item to rate card
            self.rate_card.add_item(category, item_name, uom, rate)
            
            # Refresh display
            self.refresh_rate_card_display()
            self.rate_item_window.destroy()
            messagebox.showinfo("Success", f"Item '{item_name}' added to rate card")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add rate card item: {str(e)}")

    def edit_rate_card_item(self):
        selected = self.rate_card_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select an item to edit")
            return
            
        item = self.rate_card_tree.item(selected[0])
        values = item['values']
        
        self.rate_item_window = tk.Toplevel(self.root)
        self.rate_item_window.title("Edit Rate Card Item")
        self.rate_item_window.geometry("400x250")
        
        # Rate card item form (pre-populated)
        ttk.Label(self.rate_item_window, text="Category:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.rate_category_var = tk.StringVar(value=values[0])
        categories = ["Furniture", "Flooring", "Paint", "Electrical", "Plumbing", "Accessories", "Labor", "Other"]
        ttk.Combobox(self.rate_item_window, textvariable=self.rate_category_var, values=categories).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.rate_item_window, text="Item Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.rate_item_name_var = tk.StringVar(value=values[1])
        ttk.Entry(self.rate_item_window, textvariable=self.rate_item_name_var).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.rate_item_window, text="Unit of Measure:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.rate_uom_var = tk.StringVar(value=values[2])
        uoms = ["Each", "Square Feet", "Linear Feet", "Hours", "Days"]
        ttk.Combobox(self.rate_item_window, textvariable=self.rate_uom_var, values=uoms).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self.rate_item_window, text="Rate (₹):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.rate_amount_var = tk.StringVar(value=values[3])
        ttk.Entry(self.rate_item_window, textvariable=self.rate_amount_var).grid(row=3, column=1, padx=5, pady=5)
        
        # Store original values for update
        self.original_rate_values = values
        
        # Update button
        ttk.Button(self.rate_item_window, text="Update Item", command=self.update_rate_card_item).grid(row=4, column=0, columnspan=2, pady=20)

    def update_rate_card_item(self):
        try:
            old_category = self.original_rate_values[0]
            old_item_name = self.original_rate_values[1]
            
            new_category = self.rate_category_var.get()
            new_item_name = self.rate_item_name_var.get()
            new_uom = self.rate_uom_var.get()
            
            try:
                new_rate = float(self.rate_amount_var.get())
            except ValueError:
                messagebox.showerror("Invalid Input", "Rate must be a number")
                return
                
            # Update item in rate card
            self.rate_card.update_item(old_category, old_item_name, new_category, new_item_name, new_uom, new_rate)
            
            # Refresh display
            self.refresh_rate_card_display()
            self.rate_item_window.destroy()
            messagebox.showinfo("Success", f"Item '{new_item_name}' updated in rate card")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update rate card item: {str(e)}")

    def delete_rate_card_item(self):
        selected = self.rate_card_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select an item to delete")
            return
            
        item = self.rate_card_tree.item(selected[0])
        values = item['values']
        
        category = values[0]
        item_name = values[1]
        
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {item_name} from {category}?")
        if confirm:
            try:
                self.rate_card.delete_item(category, item_name)
                self.refresh_rate_card_display()
                messagebox.showinfo("Success", f"Item '{item_name}' deleted from rate card")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete rate card item: {str(e)}")


if __name__ == "__main__":
    try:
        print("Launching GUI...")
        root = tk.Tk()
        app = QuoteApp(root)
        root.mainloop()
    except Exception as e:
        with open("error.log", "w") as log_file:
            log_file.write("An error occurred:\n")
            traceback.print_exc(file=log_file)
        print("An error occurred. Check error.log for details.")