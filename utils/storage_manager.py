
import json

class StorageManager:
    @staticmethod
    def save_project(project_data, rooms, filepath):
        serializable_rooms = []
        for room in rooms:
            serializable_room = room.copy()
            serializable_room["items"] = [item.to_dict() for item in room.get("items", [])]
            serializable_rooms.append(serializable_room)
        
        data = {
            "project": project_data,
            "rooms": serializable_rooms
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_project(filepath, item_class):
        with open(filepath, "r") as f:
            data = json.load(f)

        project = data.get("project", {})
        raw_rooms = data.get("rooms", [])
        rooms = []
        for r in raw_rooms:
            room = r.copy()
            room["items"] = [item_class(**item) for item in r.get("items", [])]
            rooms.append(room)

        return project, rooms


    @staticmethod
    def save_room_scope(room, filepath):
        from models.item import LineItem
        items = [item.to_dict() for item in room.get("items", [])]
        with open(filepath, "w") as f:
            json.dump({"room": room["name"], "items": items}, f, indent=2)

    @staticmethod
    def load_room_scope(filepath):
        from models.item import LineItem
        with open(filepath, "r") as f:
            data = json.load(f)
        room_name = data.get("room")
        items = [LineItem(**item) for item in data.get("items", [])]
        return room_name, items
