from xml.etree import ElementTree
from gi.repository import Gtk

class Handler:
	_codeview = None
	_open_file = None
	_debugger = None

	def __init__(self, builder, debugger):
		self._codeview = builder.get_object("treeview1")
		renderer = Gtk.CellRendererText()
		column_1 = Gtk.TreeViewColumn(None, renderer, text=0)
		column_2 = Gtk.TreeViewColumn(None, renderer, text=1)
		self._codeview.append_column(column_1)
		self._codeview.append_column(column_2)

		self._debugger = debugger

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
		self._load_sourcecode_file(filename[1])
		sel = self._codeview.get_selection()
		sel.select_path(int(lineno[1]) - 1)
		self._codeview.scroll_to_cell((int(lineno[1]) - 1), None, True, 0.0, 0.0)




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
			store = Gtk.ListStore(int, str)
			f = open(file_to_open, 'r')
			self._open_file = file_to_open
			line_number = 1
			for line in f:
				store.append([line_number, line.replace('\n', '')])
				line_number += 1
			f.close()
			self._codeview.set_model(store)

		return file_to_open

