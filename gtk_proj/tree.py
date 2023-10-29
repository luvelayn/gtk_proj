from gi.repository import Gtk
import json


class TreeViewHelper:
    def __init__(self):
        self.store = Gtk.TreeStore(str, str)

    def load_data_from_json(self, json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            self._fill_treeview(None, data)

    def _fill_treeview(self, parent, data):
        for key, value in data.items():
            if isinstance(value, dict):
                item = self.store.append(parent, [key, ''])
                self._fill_treeview(item, value)
            else:
                self.store.append(parent, [key, str(value)])
