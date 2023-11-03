import json
from pathlib import Path
from platformdirs import user_cache_dir
from . import __name__

cache_dir = Path(user_cache_dir()) / __name__
cache_file = (cache_dir / 'cache.json')
if not cache_dir.exists():
    cache_dir.mkdir()
if not cache_file.exists():
    cache_file.touch()

tab_data = {"default_tab": 0}

if cache_file.stat().st_size == 0:
    with open(cache_file, "w") as json_file:
        json.dump(tab_data, json_file)


def save_last_tab(tab_index):
    last_tab_data = {"last_tab": tab_index}
    with open(cache_file, "r+") as file:
        data = json.load(file)
        data.update(last_tab_data)
        file.seek(0)
        json.dump(data, file)


def get_last_tab():
    try:
        with open(cache_file, "r") as file:
            data = json.load(file)
            last_tab = data.get("last_tab")
            if last_tab is not None:
                return last_tab
            else:
                return data["default_tab"]
    except FileNotFoundError:
        return None
