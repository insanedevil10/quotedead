
class LineItem:
    def __init__(self, name, category, length=0, height=0, unit_cost=0, uom="SQFT", addons=None):
        self.name = name
        self.category = category  # e.g., 'material', 'furniture', 'decorative'
        self.length = length
        self.height = height
        self.unit_cost = unit_cost
        self.uom = uom  # e.g., SQFT, RFT, UNIT
        self.addons = addons or {}

    def quantity(self):
        if self.uom in ["SQFT", "RFT"]:
            return round(self.length * self.height, 2)
        elif self.uom == "UNIT":
            return 1
        elif self.uom == "LUMP_SUM":
            return 1
        else:
            return 0

    def addons_total(self):
        return sum(self.addons.values())

    def total_cost(self):
        base_cost = self.quantity() * (self.unit_cost + self.addons_total())
        return round(base_cost, 2)

    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category,
            "length": self.length,
            "height": self.height,
            "unit_cost": self.unit_cost,
            "uom": self.uom,
            "addons": self.addons,
            "quantity": self.quantity(),
            "total_cost": self.total_cost()
        }

class FurnitureItem(LineItem):
    def __init__(self, name, length, height, core_material, finish_material, unit_cost, addons=None):
        super().__init__(name, category="furniture", length=length, height=height, unit_cost=unit_cost, uom="SQFT", addons=addons)
        self.core_material = core_material
        self.finish_material = finish_material

    def to_dict(self):
        base = super().to_dict()
        base.update({
            "core_material": self.core_material,
            "finish_material": self.finish_material
        })
        return base
