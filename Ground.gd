extends KinematicBody2D

func _physics_process(delta):
	global_position.x -= 1
	if global_position.x <= -16:
		global_position.x = 0
