from xml.etree import ElementTree
from gi.repository import Gtk
from engine import Engine

class Handler:

	def __init__(self, builder):
		self.debugger = Engine()
		self.builder = builder
		self.codeview = self.setup_codeview()
		self.open_file = None

	def delete_window(self, *args):
		self.debugger.stop()
		Gtk.main_quit(*args)


# BUTTONS ACTIONS

	def run(self, button):
		[sent, response] = self.debugger.run()
		self.update_codeview(response)

	def step_over(self, button):
		[sent, response] = self.debugger.step_over()
		self.update_codeview(response)

	def step_into(self, button):
		[sent, response] = self.debugger.step_into()
		self.update_codeview(response)

	def listen(self, button):
		if (self.debugger.status == 'running'):
			button.set_label('Listen')
			self.debugger.stop()
			self.set_status('Stopped.')
		else:
			button.set_label('Stop')
			self.set_status('Listening...')
			[addr, response] = self.debugger.start()
			self.set_status(addr)
			self.update_console(response)


# CONSOLE & STATUS

	def update_console(self, text):
		self.builder.get_object("console").get_buffer().set_text(text)

	def set_status(self, text):
		context_id = Gtk.Statusbar().get_context_id("Connection");
		self.builder.get_object("statusbar_main").push(context_id, text)


# CODEVIEW

	def setup_codeview(self):
		codeview = self.builder.get_object("treeview1")
		renderer = Gtk.CellRendererText()
		codeview.append_column(Gtk.TreeViewColumn(None, renderer, text=0))
		codeview.append_column(Gtk.TreeViewColumn(None, renderer, text=1))
		return codeview


	def update_codeview(self, response):
		(lineno, filename) = self.get_attributes(response)
		self.load_sourcecode_file(filename[1])

		self.codeview.get_selection().select_path(int(lineno[1]) - 1)
		self.codeview.scroll_to_cell((int(lineno[1]) - 1), None, False, 0.0, 0.0)

		self.update_console(response)


	def get_attributes(self, s):
		# neccessary for etree to work
		s = s.replace('\x00', '')

		element = ElementTree.XML(s)
		tag = element.iter()
		tag.next(); # <response></response>

		return tag.next().items()


	def load_sourcecode_file(self, filename):
		file_to_open = filename.replace('file://', '')
		if (self.open_file != file_to_open):
			store = Gtk.ListStore(int, str)
			f = open(file_to_open, 'r')
			self.open_file = file_to_open
			line_number = 1
			for line in f:
				store.append([line_number, line.replace('\n', '')])
				line_number += 1
			f.close()
			self.codeview.set_model(store)

		return file_to_open

