from xml.etree import ElementTree
from gi.repository import Gtk
from engine import Engine
import glib, Queue
import base64, time

class Handler:

	def __init__(self, builder):
		self.queue = Queue.Queue()
		self.debugger = Engine(self.queue)
		self.debugger.start()
		self.builder = builder
		self.codeview = self.setup_codeview()
		self.watchesview = self.setup_watchesview()
		self.open_file = None
		glib.timeout_add(200, self.handle_queue)

	def delete_window(self, *args):
		print "Waiting for socket to close..."
		self.debugger.signal = 'kill'
		Gtk.main_quit(*args)

	def handle_queue(self):
		time.sleep(0.1) #doesn't work without it
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
			if 'watchview' in msg:
				self.update_watchesview(msg['watchview'])

		self.update_buttons()
		self.set_status('Status: ' + str(self.debugger.status))
		return True

	def update_buttons(self):
		listen_button = self.builder.get_object("button_listen")
		status = self.debugger.status
		if (status == 'idle'):
			listen_button.set_sensitive(True)
			listen_button.set_label('Listen')
		elif (status == 'listening'):
			listen_button.set_sensitive(False)
			listen_button.set_label('Listening...')
		elif (status == 'running'):
			listen_button.set_sensitive(True)
			listen_button.set_label('Stop')



# BUTTONS ACTIONS

	def run(self, button):
		self.debugger.xrun()

	def step_over(self, button):
		self.debugger.step_over()

	def step_into(self, button):
		self.debugger.step_into()

	def listen(self, button):
		status = self.debugger.status
		if (status == 'idle'):
			self.debugger.signal = "listen"
		elif (status == 'listening'):
			self.debugger.signal = "stop=listening"
		elif (status == 'running'):
			self.debugger.signal = "stop"



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

	def execute_command(self, widget, event):
		if (event.keyval ==	65293):
			r = self.debugger.execute(widget.get_text())
			self.update_console(r)



# WATCHES VIEW

	def add_watch(self, widget, event):
		if (event.keyval ==	65293):
			self.debugger.add_watch(widget.get_text())


	def setup_watchesview(self):
		v = self.builder.get_object("watches")
		renderer = Gtk.CellRendererText()
		v.append_column(Gtk.TreeViewColumn(None, renderer, text=0))
		return v


	def update_watchesview(self, watches):
		XMLNS = "urn:debugger_protocol_v1"
		elements = dict()
		for s in watches:
			xml_data = watches[s].replace('\x00', '')
			response_element = ElementTree.XML(xml_data)
			elements[s] = list(response_element).pop()

		store = Gtk.TreeStore(str)
		self.prepareStore(elements, None, store)
		self.watchesview.set_model(store)


	def prepareStore(self, elements, parent, store):
		for e in elements:
			if (type(elements) == type(dict())):
				tag = elements[e]
			else:
				tag = e

			tag_name = tag.get('name')
			if (tag_name == None):
				tag_name = e

			copy = ''
			if tag.text:
				if tag.get('encoding') == 'base64':
					copy = base64.b64decode(str(tag.text))
				else:
					copy = tag.text

			value_type = tag.get('type')
			new_parent = store.append(parent, [str(tag_name) + " (" + str(value_type) + "): " + str(copy)])
			if len(tag) > 0:
				self.prepareStore(tag, new_parent, store)



# CODEVIEW

	def setup_codeview(self):
		codeview = self.builder.get_object("treeview1")
		renderer = Gtk.CellRendererText()
		codeview.append_column(Gtk.TreeViewColumn(None, renderer, text=0, foreground=4, background=2))
		codeview.append_column(Gtk.TreeViewColumn(None, renderer, text=1, foreground=5, background=3))
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
			store = Gtk.ListStore(int, str, str, str, str, str)
			try:
				f = open(file_to_open, 'r')
			except IOError:
				print "Couldn't open file!"
				return None
			self.open_file = file_to_open
			line_number = 1
			for line in f:
				store.append([
					line_number,
					line.replace('\n', ''),
					"#eeeeee",
					"#ffffff",
					"#bbbbbb",
					"#333333"
				])
				line_number += 1
			f.close()
			self.codeview.set_model(store)

		return file_to_open

