"""
Calculation Model - Handles all calculation logic for the application
"""

class Calculator:
    """Logic for calculating item amounts, totals, etc."""
    
    @staticmethod
    def calculate_item_amount(item):
        """Calculate the amount for a line item with material options and add-ons"""
        # Get base values
        uom = item.get("uom", "NOS")
        length = float(item.get("length", 0) or 0)
        height = float(item.get("height", 0) or 0)
        quantity = float(item.get("quantity", 0) or 0)
        rate = float(item.get("rate", 0) or 0)
        
        # Calculate base amount based on UOM
        base_amount = 0
        if uom == "SFT":  # Square feet
            # Area calculation: length × height
            area = length * height
            base_amount = area * quantity * rate
        elif uom == "RFT":  # Running feet
            # Linear calculation: length only
            base_amount = length * quantity * rate
        elif uom == "NOS":  # Numbers/count
            # Just quantity × rate
            base_amount = quantity * rate
        else:
            base_amount = quantity * rate
        
        # Apply material additional cost if specified
        total_amount = base_amount
        material_addition = 0
        
        if "material" in item and item["material"].get("selected"):
            selected_material = item["material"].get("selected")
            price_additions = item["material"].get("price_additions", {})
            
            # Get price addition for selected material (default to 0 if not found)
            if selected_material in price_additions:
                # Calculate additional cost based on UOM
                if uom == "SFT":
                    material_addition = price_additions[selected_material] * length * height * quantity
                elif uom == "RFT":
                    material_addition = price_additions[selected_material] * length * quantity
                else:  # NOS
                    material_addition = price_additions[selected_material] * quantity
            
            # Add material cost to total
            total_amount += material_addition
        
        # Calculate add-on costs
        add_on_cost = 0
        if "add_ons" in item and isinstance(item["add_ons"], dict):
            add_ons = item["add_ons"]
            
            # Process each add-on
            for add_on_name, add_on_info in add_ons.items():
                # Skip if not selected
                if not add_on_info.get("selected", False):
                    continue
                
                # Get add-on rate
                add_on_rate = float(add_on_info.get("rate_per_unit", 0) or 0)
                
                # Calculate add-on cost based on UOM
                if uom == "SFT":
                    # For SFT, apply to the total square footage
                    add_on_cost += add_on_rate * length * height * quantity
                elif uom == "RFT":
                    # For RFT, apply to the total running feet
                    add_on_cost += add_on_rate * length * quantity
                else:
                    # For NOS, apply to the quantity
                    add_on_cost += add_on_rate * quantity
        
        # Legacy support for string-based add-ons
        elif "add_ons" in item and isinstance(item["add_ons"], str) and item["add_ons"]:
            add_on_names = [x.strip().lower() for x in item["add_ons"].split(",")]
            
            # Process legacy string-based add-ons
            for add_on in add_on_names:
                if add_on == "profile door":
                    # Profile door: Additional ₹150 per SFT
                    if uom == "SFT":
                        add_on_cost += 150 * length * height * quantity
                
                elif add_on == "lights":
                    # Lights: Additional ₹250 per SFT
                    if uom == "SFT":
                        add_on_cost += 250 * length * height * quantity
        
        # Add add-on cost to total
        total_amount += add_on_cost
        
        return total_amount
    
    @staticmethod
    def calculate_room_totals(line_items):
        """Calculate totals grouped by room"""
        room_totals = {}
        for item in line_items:
            room = item["room"]
            amount = item["amount"]
            
            if room not in room_totals:
                room_totals[room] = 0
            
            room_totals[room] += amount
        
        return room_totals
    
    @staticmethod
    def calculate_subtotal(room_totals):
        """Calculate subtotal from room totals"""
        return sum(room_totals.values())
    
    @staticmethod
    def calculate_gst(subtotal, gst_percent):
        """Calculate GST amount"""
        return subtotal * (gst_percent / 100)
    
    @staticmethod
    def calculate_discount(subtotal, discount_percent):
        """Calculate discount amount"""
        return subtotal * (discount_percent / 100)
    
    @staticmethod
    def calculate_grand_total(subtotal, gst_amount, discount_amount):
        """Calculate grand total"""
        return subtotal + gst_amount - discount_amount
    
    @staticmethod
    def get_item_breakdown_by_type(line_items):
        """Group items by type (e.g., UOM)"""
        breakdown = {}
        for item in line_items:
            uom = item.get("uom", "Unknown")
            if uom not in breakdown:
                breakdown[uom] = 0
            breakdown[uom] += item["amount"]
        return breakdown
    
    @staticmethod
    def parse_price_mapping(price_string):
        """Parse a string of price mappings in the format 'Name1:Price1,Name2:Price2'"""
        price_map = {}
        if not price_string:
            return price_map
            
        # Split by comma to get pairs
        pairs = price_string.split(',')
        for pair in pairs:
            # Split by colon to get name and price
            if ':' in pair:
                name, price_str = pair.split(':', 1)
                name = name.strip()
                try:
                    price = float(price_str.strip())
                    price_map[name] = price
                except (ValueError, TypeError):
                    # Skip invalid price values
                    continue
                    
        return price_map
    
    @staticmethod
    def get_material_options_from_rate_card(rate_card_item):
        """Extract material options from rate card item"""
        material_options = []
        price_additions = {}
        base_material = None
        
        # Check if material_options field exists and has content
        if "material_options" in rate_card_item and rate_card_item["material_options"]:
            # Split by comma and strip whitespace
            options_str = rate_card_item["material_options"]
            options_list = [opt.strip() for opt in options_str.split(",")]
            
            # Set base material as the first option if available
            material_options = options_list
            if options_list:
                base_material = options_list[0]
                
                # Set default price additions (0 for base, use defaults for others)
                price_additions = {base_material: 0}  # Base material has no additional cost
                
                # Parse material prices from rate card if available
                material_prices = {}
                if "material_prices" in rate_card_item and rate_card_item["material_prices"]:
                    material_prices = Calculator.parse_price_mapping(rate_card_item["material_prices"])
                
                # Set prices for each material
                for option in options_list[1:]:  # Skip base material (already set to 0)
                    # Use price from rate card if available, otherwise use defaults
                    if option in material_prices:
                        price_additions[option] = material_prices[option]
                    else:
                        # Use default prices if not specified
                        option_lower = option.lower()
                        if option_lower == "laminate":
                            price_additions[option] = 0
                        elif option_lower == "veneer":
                            price_additions[option] = 500
                        elif option_lower == "pu":
                            price_additions[option] = 800
                        elif option_lower == "acrylic":
                            price_additions[option] = 600
                        elif option_lower == "premium":
                            price_additions[option] = 400
                        elif option_lower == "texture":
                            price_additions[option] = 200
                        else:
                            # Default addition of ₹300 per SFT
                            price_additions[option] = 300
        
        return {
            "options": material_options,
            "base_material": base_material,
            "price_additions": price_additions
        }
    
    @staticmethod
    def get_add_ons_from_rate_card(rate_card_item):
        """Extract add-ons from rate card item"""
        add_ons = {}
        
        # Check if add_ons field exists and has content
        if "add_ons" in rate_card_item and rate_card_item["add_ons"] and rate_card_item["add_ons"].lower() != "none":
            # Split by comma and strip whitespace
            add_ons_str = rate_card_item["add_ons"]
            add_ons_list = [addon.strip() for addon in add_ons_str.split(",")]
            
            # Parse add-on prices from rate card if available
            addon_prices = {}
            if "addon_prices" in rate_card_item and rate_card_item["addon_prices"]:
                addon_prices = Calculator.parse_price_mapping(rate_card_item["addon_prices"])
            
            # Create structured add-ons object
            for add_on in add_ons_list:
                # Get price from rate card if available, otherwise use defaults
                if add_on in addon_prices:
                    rate_per_unit = addon_prices[add_on]
                    description = f"{add_on} (₹{rate_per_unit} per unit)"
                else:
                    # Set reasonable default rates for common add-ons
                    rate_per_unit = 0
                    description = ""
                    
                    if add_on.lower() == "profile door":
                        rate_per_unit = 150
                        description = "Premium profile door finish"
                    elif add_on.lower() == "lights":
                        rate_per_unit = 250
                        description = "LED strip lighting"
                    else:
                        rate_per_unit = 100  # Default rate
                        description = f"Additional {add_on} feature"
                
                # Add to add-ons dictionary
                add_ons[add_on] = {
                    "selected": False,  # Default to not selected
                    "rate_per_unit": rate_per_unit,
                    "description": description
                }
        
        return add_ons