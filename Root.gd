extends Node2D

onready var player = $World/Player
onready var pipe1 = $World/Pipe
onready var pipe2 = $World/Pipe2
onready var ui = $UI

var score = 0

func _ready() -> void:
	get_tree().paused = true
	OS.window_fullscreen = true

func _on_PlayButton_pressed() -> void:
	ui.visible = false
	player.visible = true
	player.reset()
	pipe1.reset()
	pipe2.reset()
	Input.set_mouse_mode(Input.MOUSE_MODE_HIDDEN)
	get_tree().paused = false

func _on_Player_death_animation_done() -> void:
	ui.visible = true
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
