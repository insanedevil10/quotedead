
import json
import os

RATE_CARD_FILE = "rate_card.json"
DEFAULT_RATE_CARD = {
    "material": [],
    "furniture": [],
    "decorative": []
}

class RateCardManager:
    def __init__(self, filepath=RATE_CARD_FILE):
        self.filepath = filepath
        self.data = DEFAULT_RATE_CARD.copy()
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                self.data = json.load(f)
        else:
            self.save()

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.data, f, indent=2)

    def get_items(self, category):
        return self.data.get(category, [])

    def add_item(self, category, name, uom, rate):
        self.data[category].append({"name": name, "uom": uom, "rate": rate})
        self.save()

    def update_item(self, category, index, name, uom, rate):
        if 0 <= index < len(self.data[category]):
            self.data[category][index] = {"name": name, "uom": uom, "rate": rate}
            self.save()

    def delete_item(self, category, index):
        if 0 <= index < len(self.data[category]):
            del self.data[category][index]
            self.save()
