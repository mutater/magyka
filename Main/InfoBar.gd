extends ColorRect

onready var player = get_node("../../Player")


func _ready():
	$InfoBars/Bars/HpBarFull.rect_size.x = round(player.stats.health / player.stats.maxHealth * 62)
	$InfoBars/Labels/HpLabel.text = "HP " + str(player.stats.health) + "/" + str(player.stats.maxHealth)
	$InfoBars/Bars/MpBarFull.rect_size.x = round(player.stats.mana / player.stats.maxMana * 62)
	$InfoBars/Labels/MpLabel.text = "MP " + str(player.stats.mana) + "/" + str(player.stats.maxMana)
	$GoldLabel.text = str(player.gold)
	$StonesLabel.text = str(player.stones)


func _on_InfoBars_mouse_entered():
	$InfoBars/Bars.visible = false
	$InfoBars/Labels.visible = true


func _on_InfoBars_mouse_exited():
	$InfoBars/Bars.visible = true
	$InfoBars/Labels.visible = false
