
from pathlib import Path
import json


def write_json(data):
    # Delete the old file if it exists
    try:
        File = Path("Config.json")
        File.unlink()
    except FileNotFoundError:
        pass

    # Write the new data to Config.json
    with open("Config.json", 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        f.close()

def read_json(data_out):
    try:
        with open("Config.json", "r", encoding="utf-8") as f:
            data_out.clear()
            data_out.update(json.load(f))
        return 0, "OK"
    except FileNotFoundError:
        return -1, "Fichier introuvable"
    except json.JSONDecodeError:
        return -2, "JSON invalide"


