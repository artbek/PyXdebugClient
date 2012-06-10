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
	_open_file = None

	def __init__(self):
		self._codeview = builder.get_object("textview_code")

	def delete_window(self, *args):
		debugger.stop()
		Gtk.main_quit(*args)

	def run(self, button):
		sent, response = debugger.run()
		self._codeview.get_buffer().set_text(response)

	def step_over(self, button):
		sent, response = debugger.step_over()
		(lineno, filename) = _get_attributes(response)
		print lineno
		file_to_open = filename[1].replace('file://', '')
		print file_to_open
		if (self._open_file != file_to_open):
			f = open(file_to_open, 'r')
			self._open_file = file_to_open
			print f
			self._codeview.get_buffer().set_text(f.read())
			f.close()

		iter = self._codeview.get_buffer().get_start_iter()
		iter.set_line(int(lineno[1]) - 1)
		mark = self._codeview.get_buffer().create_mark(None, iter, True)
		self._codeview.scroll_to_mark(mark, 0.0, True, 0.0, 0.5)

	def step_into(self, button):
		sent, response = debugger.step_into()
		self._codeview.get_buffer().set_text(response)


builder = Gtk.Builder()
builder.add_from_file("gui.glade")
builder.connect_signals(Handler())

builder.get_object("textview_code").get_buffer().set_text("bollocks")

window = builder.get_object("window_main")
window.show_all()

Gtk.main()

print 'Closed.'
