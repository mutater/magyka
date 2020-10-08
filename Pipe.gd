extends RigidBody2D

export var x_pos = 336

func _ready():
	reset()

func _physics_process(delta):
	global_position.x -= 1
	if global_position.x <= -16:
		reset()
		global_position.x = 336

func reset():
	global_position.x = x_pos
	randomize()
	global_position.y = (randi() % 5 + 3) * 16
