
import json
import os
from models.item import LineItem

TEMPLATE_DIR = "room_templates"

class TemplateManager:
    def __init__(self):
        os.makedirs(TEMPLATE_DIR, exist_ok=True)

    def save_template(self, name, items):
        filepath = os.path.join(TEMPLATE_DIR, f"{name}.json")
        with open(filepath, "w") as f:
            json.dump([item.to_dict() for item in items], f, indent=2)

    def load_template(self, name):
        filepath = os.path.join(TEMPLATE_DIR, f"{name}.json")
        if not os.path.exists(filepath):
            return []
        with open(filepath, "r") as f:
            data = json.load(f)
        return [LineItem(**item) for item in data]

    def list_templates(self):
        return [f.replace(".json", "") for f in os.listdir(TEMPLATE_DIR) if f.endswith(".json")]
