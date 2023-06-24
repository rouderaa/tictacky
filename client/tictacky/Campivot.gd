extends Node3D

var _right_select = false

# Called when the node enters the scene tree for the first time.
func _ready():
	pass 

func _input(event):
	# enable/disable rotation by using the right mouse button press
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_RIGHT and event.pressed:
		_right_select = !_right_select
		if _right_select:
			Input.set_mouse_mode(Input.MOUSE_MODE_HIDDEN)
		else:
			Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
		
	# get mouse input for camera rotation if right button has been clicked before
	if event is InputEventMouseMotion:
		if _right_select:
			rotate_y(-event.relative.x * 0.005)

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
