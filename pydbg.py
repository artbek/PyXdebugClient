from engine import Engine

debugger = Engine()
response = debugger.start()
print response

while 1:
	user_command = raw_input()
	if (user_command == "q"):
		break
	else:
		sent, response = debugger.send(user_command)
	print sent
	print response


debugger.stop()
print 'Closed.'
