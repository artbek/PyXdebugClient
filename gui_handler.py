from xml.etree import ElementTree
from gi.repository import Gtk

class Handler:
	_codeview = None
	_open_file = None
	_debugger = None

	def __init__(self, builder, debugger):
		self._codeview = builder.get_object("textview_code")
		self._buf = self._codeview.get_buffer()
		self._debugger = debugger
		self._tag = self._buf.create_tag("orange_bg", background="orange")

	def delete_window(self, *args):
		self._debugger.stop()
		Gtk.main_quit(*args)


	def run(self, button):
		sent, response = self._debugger.run()
		self._update_codeview(response)

	def step_over(self, button):
		sent, response = self._debugger.step_over()
		self._update_codeview(response)

	def step_into(self, button):
		sent, response = self._debugger.step_into()
		self._update_codeview(response)


	def _update_codeview(self, response):
		(lineno, filename) = self._get_attributes(response)
		self._buf.remove_all_tags(self._buf.get_start_iter(), self._buf.get_end_iter())
		self._load_sourcecode_file(filename[1])

		iter = self._buf.get_iter_at_line_index(int(lineno[1]) - 1, 0)
		mark = self._buf.create_mark(None, iter, True)
		self._codeview.scroll_to_mark(mark, 0.0, True, 0.0, 0.0)

		self._buf.apply_tag(self._tag, iter, self._buf.get_iter_at_line_index(int(lineno[1]), 0))

	def _get_attributes(self, s):
		# neccessary for etree to work
		s = s.replace('\x00', '')

		element = ElementTree.XML(s)
		tag = element.iter()
		tag.next(); # <response></response>

		return tag.next().items()

	def _load_sourcecode_file(self, filename):
		file_to_open = filename.replace('file://', '')
		if (self._open_file != file_to_open):
			f = open(file_to_open, 'r')
			self._open_file = file_to_open
			self._buf.set_text(f.read())
			f.close()

		return file_to_open

