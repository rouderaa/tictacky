extends Node3D

var fieldO = []
var fieldX = []

func make_field(piece):
	var field = []
	for i in 3:
		field.append([]);
		for j in 3:
			var np = piece.duplicate()
			var translation = Vector3(j*3.33, 0, i*3.33)
			np.translate(translation)
			np.visible = false
			add_child(np)
			field[i].append(np);
	return field


# Called when the node enters the scene tree for the first time.
func _ready():
#	DisplayServer.mouse_set_mode(DisplayServer.MOUSE_MODE_HIDDEN)
	fieldO = make_field($pieceO00)
	fieldX = make_field($pieceX00)
	pass

func display_board(board):
	# get rid of double quotes from value U
	var fields = board["U"]
	for x in 3:
		for y in 3:
			if fields[y][x] != '.':
				if fields[y][x] == 'X':
					fieldO[x][y].visible = false
					fieldX[x][y].visible = true
				else:
					fieldO[x][y].visible = true
					fieldX[x][y].visible = false
			else:
				fieldO[x][y].visible = false
				fieldX[x][y].visible = false

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if $Connection.is_status_connected():
		var message_str = $Connection.readFromHost()
		if message_str != "":
			var parts = message_str.split("{")
			for part in parts:
				if part != "":
					part = "{"+part				
					print(part)
					var message = JSON.parse_string(part)
					if message.has("U"):
						display_board(message)
					elif message.has("M"):
						print(message)
						$UILayer/LineLabel.text = message["M"]
	
func _input(event): # All major mouse and button input events
#	if event is InputEventMouseMotion:
#		aim_turn = -event.relative.x * 0.015 # animates player with mouse movement while aiming 

	if event.is_action_pressed("select00"):
		print_debug("7 pressed")
		# $pieceO00.visible = not $pieceO00.visible
		for i in 3:
			var col = fieldO[i]
			for j in 3:
				var e = col[j]
				e.visible=true
	
	if event.is_action_pressed("select01"):
		print_debug("8 pressed")
		# $pieceO00.visible = not $pieceO00.visible
		for i in 3:
			var col = fieldX[i]
			for j in 3:
				var e = col[j]
				e.visible=true

	if event.is_action_pressed("quit"):
			Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
			get_tree().quit()

# Mouse clicked on board check			
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		var from = $Campivot/Camera.project_ray_origin(event.position)
		var to = from + $Campivot/Camera.project_ray_normal(event.position)*100
		var query = PhysicsRayQueryParameters3D.create(from, to)

		var space_state = get_world_3d().direct_space_state
		var result = space_state.intersect_ray(query)
		if result != {}:
			var board_width = $Board.mesh.size[0]
			var board_height = $Board.mesh.size[2]
			
			var px = (result.position[0]+(board_width/2))*2.0;
			var x = round(px)
			var py = (result.position[2]+(board_height/2))*2.0;
			var y = round(py)
			# print ("px, py : ", px, py)
			print("x,y:", x," ",y)
			$Connection.send_coord(x,y)

func _on_start_button_pressed():
	$Connection.send_reset()
	$UILayer/LineLabel.text = ""
