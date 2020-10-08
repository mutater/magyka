extends Node2D


func _input(event):
	if event.is_action_pressed("f11"):
		OS.window_fullscreen = OS.window_fullscreen == false


func _on_AdventureButton_pressed():
	$Menu.visible = false
	$Adventure.visible = true
