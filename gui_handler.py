from xml.etree import ElementTree
from gi.repository import Gtk
from engine import Engine
import glib, Queue

class Handler:

	def __init__(self, builder):
		self.queue = Queue.Queue()
		self.debugger = Engine(self.queue)
		self.builder = builder
		self.codeview = self.setup_codeview()
		self.open_file = None
		glib.timeout_add(200, self.handle_queue)

	def delete_window(self, *args):
		self.debugger.stop()
		Gtk.main_quit(*args)

	def handle_queue(self):
		try:
			msg = self.queue.get_nowait()
		except Queue.Empty:
			msg = ''
		if (msg):
			if 'console' in msg:
				self.update_console(msg['console'])
			if 'stack' in msg:
				self.update_stack(msg['stack'])
			if 'code' in msg:
				self.update_codeview(msg['code'])
		return True


# BUTTONS ACTIONS

	def run(self, button):
		self.debugger.xrun()

	def step_over(self, button):
		self.debugger.step_over()

	def step_into(self, button):
		self.debugger.step_into()

	def listen(self, button):
		if (self.debugger.status == 'running'):
			button.set_label('Listen')
			self.debugger.stop()
		else:
			button.set_label('Stop')
			self.set_status('Listening...')
			self.debugger.start()


# CONSOLE & STATUS

	def update_console(self, text):
		self.builder.get_object("console").get_buffer().set_text(text)

	def update_stack(self, text):
		s = text.replace('\x00', '')
		stack_iter = list(ElementTree.XML(s).iter())
		stack_str = ''
		for e in stack_iter:
			temp = e.get('filename')
			if temp:
				stack_str += temp + '\n'
		self.builder.get_object("stack").get_buffer().set_text(stack_str)

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
		if self.load_sourcecode_file(filename[1]):
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
			try:
				f = open(file_to_open, 'r')
			except IOError:
				print "Couldn't open file!"
				return None
			self.open_file = file_to_open
			line_number = 1
			for line in f:
				store.append([line_number, line.replace('\n', '')])
				line_number += 1
			f.close()
			self.codeview.set_model(store)

		return file_to_open

