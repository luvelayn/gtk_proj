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


def save_last_tab(tab_index):
    data = {"last_tab": tab_index}
    with open(cache_file, "w") as file:
        json.dump(data, file)


def get_last_tab():
    try:
        with open(cache_file, "r") as file:
            data = json.load(file)

            if "last_tab" in data:
                return data["last_tab"]
            else:
                return 0

    except FileNotFoundError:
        return None
