
class QuoteCalculator:
    def calculate_room_total(self, room):
        total = 0
        if "items" in room:
            for item in room["items"]:
                total += item.total_cost()
        return round(total, 2)

    def calculate_project_total(self, rooms):
        return round(sum(self.calculate_room_total(room) for room in rooms), 2)

    def generate_room_summary(self, room):
        summary = {
            "room_name": room["name"],
            "area_sqft": room["length"] * room["width"],
            "volume_cft": room["length"] * room["width"] * room["height"],
            "items": [item.to_dict() for item in room.get("items", [])],
            "total": self.calculate_room_total(room)
        }
        return summary

    def generate_project_summary(self, rooms):
        return {
            "rooms": [self.generate_room_summary(room) for room in rooms],
            "grand_total": self.calculate_project_total(rooms)
        }
