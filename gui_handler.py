from xml.etree import ElementTree
from gi.repository import Gtk
from engine import Engine
import glib, Queue
import base64

class Handler:

	def __init__(self, builder):
		self.queue = Queue.Queue()
		self.debugger = Engine(self.queue)
		self.builder = builder
		self.codeview = self.setup_codeview()
		self.watchesview = self.setup_watchesview()
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
		self.update_watchesview("test")
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
		codeview.append_column(Gtk.TreeViewColumn(None, renderer, text=0, foreground=4, background=2))
		codeview.append_column(Gtk.TreeViewColumn(None, renderer, text=1, foreground=5, background=3))
		return codeview


	def update_codeview(self, response):
		(lineno, filename) = self.get_attributes(response)
		if self.load_sourcecode_file(filename[1]):
			self.codeview.get_selection().select_path(int(lineno[1]) - 1)
			self.codeview.scroll_to_cell((int(lineno[1]) - 1), None, False, 0.0, 0.0)

		self.update_console(response)


	def setup_watchesview(self):
		v = self.builder.get_object("watches")
		renderer = Gtk.CellRendererText()
		v.append_column(Gtk.TreeViewColumn(None, renderer, text=0))
		return v


	def update_watchesview(self, data):
		s = '<response xmlns="urn:debugger_protocol_v1" xmlns:xdebug="http://xdebug.org/dbgp/xdebug" command="eval" transaction_id="70"><property address="140736914105248" type="object" classname="Fuel\Core\Request" children="1" numchildren="14" page="0" pagesize="32"><property name="response" facet="public" address="264918112" type="null"></property><property name="uri" facet="public" address="264917504" type="object" classname="Fuel\Core\Uri" children="1" numchildren="2" page="0" pagesize="32"><property name="uri" facet="protected" address="264982928" type="string" size="16" encoding="base64"><![CDATA[cHJvZHVjdC92aWV3LzM3Mg==]]></property><property name="segments" facet="protected" address="264942232" type="array" children="1" numchildren="3"></property></property><property name="route" facet="public" address="265048112" type="object" classname="Fuel\Core\Route" children="1" numchildren="12" page="0" pagesize="32"><property name="segments" facet="public" address="265474552" type="array" children="1" numchildren="3"></property><property name="named_params" facet="public" address="265054584" type="array" children="0" numchildren="0"></property><property name="method_params" facet="public" address="265009968" type="array" children="1" numchildren="1"></property><property name="path" facet="public" address="264926608" type="string" size="16" encoding="base64"><![CDATA[cHJvZHVjdC92aWV3LzM3Mg==]]></property><property name="case_sensitive" facet="public" address="265048256" type="bool"><![CDATA[1]]></property><property name="module" facet="public" address="265008360" type="string" size="7" encoding="base64"><![CDATA[cHJvZHVjdA==]]></property><property name="directory" facet="public" address="264577008" type="null"></property><property name="controller" facet="public" address="265010048" type="string" size="26" encoding="base64"><![CDATA[UHJvZHVjdFxDb250cm9sbGVyX1Byb2R1Y3Q=]]></property><property name="action" facet="public" address="265009168" type="string" size="4" encoding="base64"><![CDATA[dmlldw==]]></property><property name="translation" facet="public" address="264982928" type="string" size="16" encoding="base64"><![CDATA[cHJvZHVjdC92aWV3LzM3Mg==]]></property><property name="callable" facet="public" address="264821760" type="null"></property><property name="search" facet="protected" address="264926608" type="string" size="16" encoding="base64"><![CDATA[cHJvZHVjdC92aWV3LzM3Mg==]]></property></property><property name="method" facet="protected" address="47392883727792" type="string" size="3" encoding="base64"><![CDATA[R0VU]]></property><property name="module" facet="public" address="265008360" type="string" size="7" encoding="base64"><![CDATA[cHJvZHVjdA==]]></property><property name="directory" facet="public" address="264917904" type="string" size="0" encoding="base64"><![CDATA[]]></property><property name="controller" facet="public" address="265010048" type="string" size="26" encoding="base64"><![CDATA[UHJvZHVjdFxDb250cm9sbGVyX1Byb2R1Y3Q=]]></property><property name="action" facet="public" address="265009168" type="string" size="4" encoding="base64"><![CDATA[dmlldw==]]></property><property name="method_params" facet="public" address="265009968" type="array" children="1" numchildren="1" page="0" pagesize="32"><property name="0" address="265009216" type="string" size="3" encoding="base64"><![CDATA[Mzcy]]></property></property><property name="named_params" facet="public" address="265054584" type="array" children="0" numchildren="0" page="0" pagesize="32"></property><property name="controller_instance" facet="public" address="264937984" type="null"></property><property name="paths" facet="public" address="265038704" type="array" children="1" numchildren="1" page="0" pagesize="32"><property name="0" address="265038304" type="string" size="114" encoding="base64"><![CDATA[L21udC9wZHJpdmUvQ2xpZW50cy9qb3NlcGhqb3NlcGguY29tLW5ldy92ZXJzaW9ucy9iYXJ0L2luY2x1ZGVzL2Z1ZWwvcGFja2FnZXMvcHJvcHNob3AvY2xhc3Nlcy8uLi9tb2R1bGVzL3Byb2R1Y3Qv]]></property></property><property name="parent" facet="protected" address="264938440" type="null"></property><property name="children" facet="protected" address="264938664" type="array" children="0" numchildren="0" page="0" pagesize="32"></property></property></response>'

		XMLNS = "urn:debugger_protocol_v1"
		element = ElementTree.XML(s)
		iterator = element.iter()
		iterator.next() # get <response> out of the way
		#for tag in i: print str(tag.get("name")) + ": " + str(base64.b64decode(tag.text))
		parent_map = dict((c, p) for p in iterator for c in p)
		print parent_map
		store = Gtk.TreeStore(str)

		parents = [None]
		current_parent = None
		for tag in iterator:
			s = str(tag.get("name")) + ": " + str(tag.text)
			new_parent = store.append(current_parent, [s])


			if (len(tag) > 0):
				print len(tag)



		#p = store.append(None, ['abc'])
		#store.append(p, ['123'])
		self.watchesview.set_model(store)





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
				store.append([line_number, line.replace('\n', ''), "#eeeeee", "#ffffff", "#bbbbbb", "#333333"])
				line_number += 1
			f.close()
			self.codeview.set_model(store)

		return file_to_open

