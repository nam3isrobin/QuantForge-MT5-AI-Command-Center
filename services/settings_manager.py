import json
import os
import config

SETTINGS_FILE = os.path.join(config.BASE_DIR, "settings.json")
EXAMPLE_SETTINGS_FILE = os.path.join(config.BASE_DIR, "settings.example.json")

def load_settings():
    for path in (SETTINGS_FILE, EXAMPLE_SETTINGS_FILE):
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError):
                continue
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)
