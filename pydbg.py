from engine import Engine
from gui_handler import Handler
from gi.repository import Gtk

builder = Gtk.Builder()
builder.add_from_file("gui.glade")


builder.connect_signals(Handler(builder))
window = builder.get_object("window_main")
window.show_all()


Gtk.main()
