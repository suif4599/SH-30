import os
import json

with open(os.path.join(os.path.dirname(__file__), 'config.json')) as f:
    config = json.load(f)

API_KEY = config.get("API_KEY", None)
if API_KEY is None:
    raise ValueError("API_KEY is not set in the config.json file.")