from engine import Engine
from gui_handler import Handler
from gi.repository import Gtk

debugger = Engine()
response = debugger.start()
print response

builder = Gtk.Builder()
builder.add_from_file("gui.glade")
builder.connect_signals(Handler(builder, debugger))

builder.get_object("textview_code").get_buffer().set_text("bollocks")

window = builder.get_object("window_main")
window.show_all()

Gtk.main()

print 'Closed.'
