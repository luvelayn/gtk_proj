from gi.repository import Gtk
from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import numpy as np
from .model import PlotData
from .treeViewHelper import TreeViewHelper
from .cache import get_last_tab, save_last_tab


class Notebook(Gtk.Notebook):
    pass


class Confirmation(Gtk.MessageDialog):
    def __init__(self):
        Gtk.MessageDialog.__init__(self)
        self.set_markup('<b>Вы уверены, что хотите выйти?</b>')
        self.add_button('да', 1)
        self.add_button('нет', 0)


class TreeTab(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        treeview_helper = TreeViewHelper()
        treeview_helper.load_data_from_json('./gtk_proj/rickandmorty.json')
        treeview = Gtk.TreeView(model=treeview_helper.store)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Name", renderer, text=0)
        treeview.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Value", renderer, text=1)
        treeview.append_column(column)

        sw = Gtk.ScrolledWindow()
        sw.set_child(treeview)

        sw.set_size_request(1300, 800)

        self.append(sw)


class PlotTab(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        fig = Figure(figsize=(5, 4), dpi=100, constrained_layout=True)
        self.ax = fig.add_subplot()
        self.user_line = None
        self.sin_line = None

        self.data = PlotData()

        self.canvas = FigureCanvas(fig)
        self.canvas.set_size_request(800, 600)

        self.animation = FuncAnimation(fig, self.update_plot, frames=100, interval=50, repeat=True, blit=True)
        self.animation_running = True

        button_start_animation = Gtk.Button(label="Старт анимации")
        button_start_animation.connect('clicked', self.start_animation)

        button_stop_animation = Gtk.Button(label="Стоп анимации")
        button_stop_animation.connect('clicked', self.stop_animation)

        button_add_point = Gtk.Button(label="Добавить")
        button_add_point.connect('clicked', self.add_point)

        self.edit_x = Gtk.SpinButton(name="X", value=0)
        self.edit_y = Gtk.SpinButton(name="Y", value=0)

        for edit in {self.edit_x, self.edit_y}:
            edit.set_adjustment(Gtk.Adjustment(upper=100, step_increment=1, page_increment=10))

        buttons_box = Gtk.Box(spacing=5,
                              margin_top=10, margin_bottom=10,
                              margin_start=10, margin_end=10)

        controls = [self.edit_x, self.edit_y, button_add_point,
                    button_start_animation, button_stop_animation]

        for c in controls:
            buttons_box.append(c)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.append(buttons_box)

        self.append(vbox)
        self.append(self.canvas)

    def update_plot(self, frame):
        if self.sin_line is not None:
            self.sin_line.remove()

        x_range = np.linspace(0, max(self.data.x + [2 * np.pi]), 100)
        y = np.sin(x_range + frame * 2 * np.pi / 100)

        self.sin_line, = self.ax.plot(x_range, y)
        self.canvas.draw()

    def start_animation(self, *args, **kwargs):
        if not self.animation_running:
            self.animation.event_source.start()
            self.animation_running = True

    def stop_animation(self, *args, **kwargs):
        if self.animation_running:
            self.animation.event_source.stop()
            self.animation_running = False

    def add_point(self, *args, **kwargs):
        self.data.add_point(self.edit_x.get_value(), self.edit_y.get_value())
        if self.user_line is not None:
            self.user_line.remove()

        self.user_line, = self.ax.plot(*self.data)
        self.canvas.draw()


class Window(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        Gtk.ApplicationWindow.__init__(self, *args, **kwargs)

        self.app = kwargs['application']
        self.connect('close-request', self.handle_exit)

        self.notebook = Notebook()

        plot_tab = PlotTab(self.app)
        tree_tab = TreeTab(self.app)

        self.notebook.append_page(plot_tab, Gtk.Label.new("График"))
        self.notebook.append_page(tree_tab, Gtk.Label.new("Дерево"))

        self.restore_last_tab()

        self.set_child(self.notebook)

    def restore_last_tab(self):
        last_tab = get_last_tab()
        if last_tab is not None:
            self.notebook.set_current_page(last_tab)

    # def save_current_tab(self):
    #     current_tab = self.notebook.get_current_page()
    #     with open('./user_cache_dir/last_tab_info.txt', 'w') as config_file:
    #         config_file.write(str(current_tab))
    #
    # def load_last_tab(self):
    #     try:
    #         with open('./user_cache_dir/last_tab_info.txt', 'r') as config_file:
    #             last_tab = int(config_file.read())
    #             self.notebook.set_current_page(last_tab)
    #     except FileNotFoundError:
    #         pass

    def handle_exit(self, _):
        dialog = Confirmation()
        dialog.set_transient_for(self)
        dialog.show()
        dialog.connect('response', self.exit)
        return True

    def exit(self, widget, response):
        if response == 1:
            last_tab = self.notebook.get_current_page()
            save_last_tab(last_tab)
            self.app.quit()
        widget.destroy()
