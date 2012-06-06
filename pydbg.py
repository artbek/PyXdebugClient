from engine import Engine
from gi.repository import Gtk

debugger = Engine()
response = debugger.start()
print response


class Handler:
	def delete_window(self, *args):
		debugger.stop()
		Gtk.main_quit(*args)

	def run(self, button):
		sent, response = debugger.run()
		print sent
		print response

	def step_over(self, button):
		sent, response = debugger.step_over()
		print sent
		print response

	def step_into(self, button):
		sent, response = debugger.step_into()
		print sent
		print response


builder = Gtk.Builder()
builder.add_from_file("gui.xml")
builder.connect_signals(Handler())

window = builder.get_object("window_main")
window.show_all()

Gtk.main()

'''
while 1:
	user_command = raw_input()
	if (user_command == "q"):
		break
	else:
		sent, response = debugger.send(user_command)
	print sent
	print response
'''

print 'Closed.'
