extends KinematicBody2D

onready var scoreSound = $Score
onready var jumpSound = $Jump
onready var deathSound = $Death

var GRAVITY = 10
var TERMINAL_VELOCITY = 300
var JUMP_FORCE = -175

var velocity = 0
var dead = true
var score = 0

signal death_animation_done
signal point_increase

func _physics_process(delta):
	velocity += GRAVITY
	if abs(0 - velocity) > abs(TERMINAL_VELOCITY) and not dead: velocity = TERMINAL_VELOCITY
	
	if Input.is_action_just_pressed("up") and not dead:
		velocity = JUMP_FORCE
		jumpSound.play()
	
	if Input.is_action_just_pressed("fullscreen"):
		if OS.window_fullscreen == true: OS.window_fullscreen = false
		else: OS.window_fullscreen = true
	
	move_and_collide(Vector2(0, velocity) * delta)
	
	position = Vector2(position.x, round(position.y))
	
	if position.y < 8: position.y = 8
	if dead and position.y > 212: emit_signal("death_animation_done")

func reset():
	score = 0
	emit_signal("point_increase", score)
	dead = false
	velocity = 0
	position.y = 90

func _on_Area2D_body_entered(body: Node) -> void:
	if dead == false:
		deathSound.play()
		get_tree().paused = true
		dead = true
		velocity = JUMP_FORCE

func _on_PointArea_area_shape_entered(area_id: int, area: Area2D, area_shape: int, self_shape: int) -> void:
	score += 1
	emit_signal("point_increase", score)
	scoreSound.play()
