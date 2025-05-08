"""
Calculation Controller - Handles calculation operations between models and views
"""
from models.calculation import Calculator

class CalculationController:
    """Controller for calculation operations"""
    
    def __init__(self, project_model):
        """Initialize with Project model"""
        self.project_model = project_model
        self.calculator = Calculator()
    
    def calculate_item_amount(self, item):
        """Calculate the amount for a single line item"""
        return self.calculator.calculate_item_amount(item)
    
    def calculate_room_totals(self):
        """Calculate totals grouped by room"""
        line_items = self.project_model.get_line_items()
        return self.calculator.calculate_room_totals(line_items)
    
    def calculate_subtotal(self):
        """Calculate the project subtotal"""
        room_totals = self.calculate_room_totals()
        return self.calculator.calculate_subtotal(room_totals)
    
    def calculate_gst(self):
        """Calculate GST amount"""
        subtotal = self.calculate_subtotal()
        settings = self.project_model.get_settings()
        gst_percent = settings.get("gst", 18)
        return self.calculator.calculate_gst(subtotal, gst_percent)
    
    def calculate_discount(self):
        """Calculate discount amount"""
        subtotal = self.calculate_subtotal()
        settings = self.project_model.get_settings()
        discount_percent = settings.get("discount", 0)
        return self.calculator.calculate_discount(subtotal, discount_percent)
    
    def calculate_grand_total(self):
        """Calculate grand total"""
        subtotal = self.calculate_subtotal()
        gst_amount = self.calculate_gst()
        discount_amount = self.calculate_discount()
        return self.calculator.calculate_grand_total(subtotal, gst_amount, discount_amount)
    
    def get_item_breakdown_by_type(self):
        """Group items by type (e.g., UOM)"""
        line_items = self.project_model.get_line_items()
        return self.calculator.get_item_breakdown_by_type(line_items)
    
    def get_material_options_from_rate_card(self, rate_card_item):
        """Extract material options from rate card item"""
        return self.calculator.get_material_options_from_rate_card(rate_card_item)
    
    def get_add_ons_from_rate_card(self, rate_card_item):
        """Extract add-ons from rate card item"""
        return self.calculator.get_add_ons_from_rate_card(rate_card_item)
    
    def calculate_project_statistics(self):
        """Calculate various project statistics"""
        line_items = self.project_model.get_line_items()
        room_totals = self.calculate_room_totals()
        
        # Initialize statistics
        stats = {
            "total_rooms": len(room_totals),
            "total_items": len(line_items),
            "avg_room_cost": 0,
            "avg_item_cost": 0,
            "highest_cost_room": {"name": "None", "amount": 0},
            "highest_cost_item": {"name": "None", "room": "None", "amount": 0}
        }
        
        # Calculate average room cost
        if stats["total_rooms"] > 0:
            stats["avg_room_cost"] = sum(room_totals.values()) / stats["total_rooms"]
        
        # Calculate average item cost
        if stats["total_items"] > 0:
            stats["avg_item_cost"] = sum(item["amount"] for item in line_items) / stats["total_items"]
        
        # Find highest cost room
        if room_totals:
            highest_room = max(room_totals.items(), key=lambda x: x[1])
            stats["highest_cost_room"] = {"name": highest_room[0], "amount": highest_room[1]}
        
        # Find highest cost item
        if line_items:
            highest_item = max(line_items, key=lambda x: x["amount"])
            stats["highest_cost_item"] = {
                "name": highest_item["item"],
                "room": highest_item["room"],
                "amount": highest_item["amount"]
            }
        
        return stats