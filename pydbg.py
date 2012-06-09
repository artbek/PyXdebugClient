from engine import Engine
from gi.repository import Gtk
from xml.etree import ElementTree

debugger = Engine()
response = debugger.start()
print response

def _get_attributes(s):
	# neccessary for etree to work
	s = s.replace('\x00', '')

	element = ElementTree.XML(s)
	tag = element.iter()
	tag.next(); # <response></response>

	return tag.next().items()


class Handler:
	_codeview = None

	def __init__(self):
		self._codeview = builder.get_object("textview_code").get_buffer()

	def delete_window(self, *args):
		debugger.stop()
		Gtk.main_quit(*args)

	def run(self, button):
		sent, response = debugger.run()
		self._codeview.set_text(response)

	def step_over(self, button):
		sent, response = debugger.step_over()
		(lineno, filename) = _get_attributes(response)
		f = open(filename[1].replace('file://', ''), 'r')
		print lineno
		print filename[1].replace('file://', '')
		print f
		self._codeview.set_text(f.read())
		f.close()

	def step_into(self, button):
		sent, response = debugger.step_into()
		self._codeview.set_text(response)


builder = Gtk.Builder()
builder.add_from_file("gui.glade")
builder.connect_signals(Handler())

builder.get_object("textview_code").get_buffer().set_text("bollocks")

window = builder.get_object("window_main")
window.show_all()

Gtk.main()

print 'Closed.'
