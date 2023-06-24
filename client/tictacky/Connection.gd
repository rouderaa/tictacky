extends Node3D

var _connection = StreamPeerTCP.new()

func _ready():
	pass

func readFromHost():
	var str = ""
	var replies
	var last_reply
	var available_bytes = _connection.get_available_bytes()
	if available_bytes > 0:
		var data: Array = _connection.get_partial_data(available_bytes)
		if data[0] == OK:
			str = data[1].get_string_from_utf8()
			print("from host data:", str)
	return str

func is_status_connected():
	return _connection.get_status() == StreamPeerTCP.STATUS_CONNECTED
	
# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	_connection.poll()
	
	if _connection.get_status() == StreamPeerTCP.STATUS_NONE:
		_connection.connect_to_host("127.0.0.1", 9080)
		
	if _connection.get_status() == StreamPeerTCP.STATUS_CONNECTED:
		readFromHost()
			
func send_coord(x,y):
	if is_status_connected():
		var _str_command = '{ "cmd":"S", "x":"'+str(x)+'", "y":"'+str(y)+'"}'
		var _command = _str_command.to_utf8_buffer()
		_connection.put_data(_command)

func send_get_board():
	if is_status_connected():
		var _str_command = '{ "cmd":"G" }'
		var _command = _str_command.to_utf8_buffer()
		_connection.put_data(_command)

func send_reset():
	if is_status_connected():
		var _str_command = '{ "cmd":"R" }'
		var _command = _str_command.to_utf8_buffer()
		_connection.put_data(_command)

func get_status():
	return _connection.get_status()
