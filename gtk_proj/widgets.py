from gi.repository import Gtk

from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import numpy as np

from .model import PlotData


class Window(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        Gtk.ApplicationWindow.__init__(self, *args, **kwargs)
        app = kwargs['application']

        fig = Figure(figsize=(5, 4), dpi=100, constrained_layout=True)

        self.ax = fig.add_subplot()
        self.user_line = None
        self.sin_line = None  # Линия для анимации синуса

        # Используем Gtk.HeaderBar вместо Gtk.Box
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(True)

        # Добавим кнопки в HeaderBar
        button_start_animation = Gtk.Button(label="Старт анимации")
        button_start_animation.connect('clicked', self.start_animation)

        button_stop_animation = Gtk.Button(label="Стоп анимации")
        button_stop_animation.connect('clicked', self.stop_animation)

        button_add_point = Gtk.Button(label="Добавить")
        button_add_point.connect('clicked', self.add_point)

        button_quit = Gtk.Button(label="Выйти")
        button_quit.connect('clicked', lambda x: app.quit())

        self.edit_x = Gtk.SpinButton(name="X", value=0)
        self.edit_y = Gtk.SpinButton(name="Y", value=0)

        for edit in {self.edit_x, self.edit_y}:
            edit.set_adjustment(Gtk.Adjustment(upper=100, step_increment=1, page_increment=10))

        header_bar.pack_start(self.edit_x)
        header_bar.pack_start(self.edit_y)
        header_bar.pack_start(button_add_point)
        header_bar.pack_start(button_quit)
        header_bar.pack_end(button_start_animation)
        header_bar.pack_end(button_stop_animation)

        self.set_titlebar(header_bar)

        self.data = PlotData()

        self.canvas = FigureCanvas(fig)
        self.canvas.set_size_request(800, 600)

        # Уберем Gtk.ScrolledWindow и добавим элементы прямо в окно
        self.set_child(self.canvas)

        # Добавим анимацию
        self.animation = FuncAnimation(fig, self.update_plot, frames=100, interval=50, repeat=True, blit=True)
        self.animation_running = True

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
