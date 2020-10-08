extends Node

signal health_changed(health)
signal health_depleted()
signal mana_changed(mana)

export var stats : Resource

onready var maxHealth = stats.maxHealth
onready var maxMana = stats.maxMana
onready var maxTech = stats.maxTech
onready var strength = stats.strength
onready var intelligence = stats.intelligence
onready var dexterity = stats.dexterity
onready var armor = stats.armor
onready var wisdom = stats.wisdom
onready var vitality = stats.vitality
onready var critChance = stats.critChance
onready var critDamage = stats.critDamage
onready var resistance = stats.resistance
