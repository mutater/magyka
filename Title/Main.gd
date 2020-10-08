extends Control


onready var continueButton = $ContinueButton
onready var newGameButton = $NewGameButton
onready var optionsButton = $OptionsButton
onready var quitButton = $QuitButton

func _on_ContinueButton_pressed():
	get_tree().change_scene_to(load("res://Main/Main.tscn"))


func _on_NewGameButton_pressed():
	pass


func _on_OptionsButton_pressed():
	pass


func _on_QuitButton_pressed():
	get_tree().quit()

