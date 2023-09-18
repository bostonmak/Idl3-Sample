extends Unit

class_name Hero

## Combat rules in order
## 1. Attack front to back
## 2. Attack lowest hp first
## 3. Pick lowest index in list

## How much per cleared block to multiply next attack 
const ATTACK_BONUS_MULTIPLIER = 0.1

@export_group("Special Properties")
@export var special_cost = 0
@export var special_attack_name = "Special Attack"
@export var special_attack_power = 0
@export var special_attack_type: AttackType

@onready var remaining_special_cost = special_cost
@onready var special_bar = $special_bar

## Number of cleared matching blocks before next attack
var next_attack_bonus = 0
var weapon

@onready var combat_window = get_parent() 

## Begin basic attack
func begin_attack():
	$sprite.animation = "attack"
	var damage = calculate_attack_damage(false)
	attack_enemy(damage)
	next_attack_bonus = 0
			
## Use special attack
func begin_special_attack():
	# TODO change to special animation when we have one
	$sprite.animation = "attack"
	var damage = calculate_attack_damage(true)
	attack_enemy(damage)
	remaining_special_cost = special_cost
	special_bar.value = 0	
	
## Target enemy and deal damage
### PARAMS
### damage: int -- Amount of damage to deal to enemy
func attack_enemy(damage):
	var enemies = combat_window.enemies
	if enemies.size() == 0:
		return
	if attack_type == AttackType.AOE:
		for enemy in enemies:
			enemy.receive_damage(damage)
	elif attack_type == AttackType.SINGLE:
		var front_enemies = combat_window.get_front_enemies()
		if front_enemies.size() == 1:
			front_enemies[0].receive_damage(damage)
		else:
			var lowest = front_enemies[0]
			for enemy in front_enemies:
				if enemy.hp < lowest.hp:
					lowest = enemy
			lowest.receive_damage(damage)
			
## Apply number of cleared blocks to hero stats like dmg and special cost
### PARAMS
### blocks: Dictionary -- map of PieceColor enum value : num blocks cleared
func add_cleared_blocks(blocks):
	for block_color in blocks.keys():
		var num_blocks = blocks[block_color]
		if remaining_special_cost > 0:
			remaining_special_cost -= num_blocks
			special_bar.value += num_blocks
		if color == block_color:
			next_attack_bonus += num_blocks
		
## Calculate amount of damage to deal to enemies
### PARAMS
### is_special_attack: bool -- Whether to use auto attack or special attack formula
func calculate_attack_damage(is_special_attack):
	var damage = 0
	if is_special_attack:
		damage = special_attack_power
		if damage < 0:
			printerr("Negative damage for hero " + unit_name + ". Special Attack = " + str(special_attack_power))
			damage = 0
		#print("Hero " + hero_name + " dealing " + str(damage) + " damage. Special Attack = " + str(special_attack_power))
	else:
		damage = attack + (attack * next_attack_bonus * ATTACK_BONUS_MULTIPLIER)
		if damage < 0:
			printerr("Negative damage for hero " + unit_name + ". Attack = " + str(attack) + ", Next Attack Bonus = " + str(next_attack_bonus))
			damage = 0
		#print("Hero " + hero_name + " dealing " + str(damage) + " damage. Attack = " + str(attack) + ", Next Attack Bonus = " + str(next_attack_bonus))
	return damage
	
# Called when the node enters the scene tree for the first time.
func _ready():
	super._ready()
	$sprite.animation = "default"
	$sprite.play()
	special_bar.max_value = special_cost

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
	

func _on_sprite_animation_finished():
	$sprite.animation = "default"


func _on_sprite_animation_changed():
	$sprite.play()


func _on_special_bar_gui_input(event):
	if event.is_action("ui_touch") and special_bar.value >= special_bar.max_value:
		begin_special_attack()
