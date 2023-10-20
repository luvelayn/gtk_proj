from gi.repository import Gtk

from matplotlib.backends.backend_gtk4agg import \
    FigureCanvasGTK4Agg as FigureCanvas
from matplotlib.figure import Figure

from .model import PlotData


class Window(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        Gtk.ApplicationWindow.__init__(self, *args, **kwargs)
        app = kwargs['application']

        fig = Figure(figsize=(5, 4), dpi=100, constrained_layout=True)
        self.ax = fig.add_subplot()
        self.line = None

        sw = Gtk.ScrolledWindow(margin_top=10, margin_bottom=10,
                                margin_start=10, margin_end=10)

        self.set_child(sw)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, )
        sw.set_child(vbox)

        box = Gtk.Box(spacing=5)
        vbox.append(box)

        button_add_point = Gtk.Button()
        button_add_point.set_label("Добавить")

        button_add_point.connect('clicked', self.add_point)

        self.data = PlotData()

        self.edit_x = Gtk.SpinButton(name="X", value=0)
        self.edit_y = Gtk.SpinButton(name="Y", value=0)

        for edit in {self.edit_x, self.edit_y}:
            edit.set_adjustment(Gtk.Adjustment(upper=100, step_increment=1, page_increment=10))

        button_quit = Gtk.Button()
        button_quit.set_label("Выйти")
        button_quit.connect('clicked', lambda x: app.quit())

        controls = (button_add_point, self.edit_x, self.edit_y, button_quit)
        for c in controls:
            box.append(c)

        self.canvas = FigureCanvas(fig)
        self.canvas.set_size_request(800, 600)
        vbox.append(self.canvas)

    def add_point(self, *args, **kwargs):
        self.data.add_point(self.edit_x.get_value(), self.edit_y.get_value())
        if self.line is not None:
            self.line.remove()

        self.line, = self.ax.plot(*self.data)
        self.canvas.draw()
