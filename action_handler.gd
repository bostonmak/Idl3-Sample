extends Node

class_name ActionHandler

static var action_to_response_map = {
	Actions.ServerActions.GET_PLAYER: Actions.GetPlayerActionResponse,
	Actions.ServerActions.CREATE_PLAYER: Actions.CreatePlayerActionResponse
}

static var callback_map = {
	Actions.GetPlayerActionResponse.get_class_name(): [preload('res://scripts/player.gd'), "receive_get_player_action"],
	Actions.CreatePlayerActionResponse.get_class_name(): [preload('res://scripts/player.gd'), "receive_create_player_action"]
}

static func handle(response):
	if "status" in response and response["status"] != 0:
		printerr("Error during response. See server ResponseStatus for code " + str(response["status"]))
	var action = response["action"]
	if action_to_response_map.get(Actions.ServerActions.get(action)) == null:
		printerr("Invalid action " + action)
		return
	var resp = action_to_response_map.get(Actions.ServerActions.get(action)).new()
	var data = response[resp.get_class_name().to_snake_case()]
	if data == null:
		printerr("Invalid response type. Expected " + resp.get_class_name().to_camel_case() +"\nInstead received " + action_to_response_map.keys().filter(func f(key): key != "action"))
		return
	for field in data:
		print("setting " + field + " to " + str(data[field]))
		var field_snake_case = field.to_snake_case()
		resp[field_snake_case] = set_data(resp[field_snake_case], data[field])
	
	return resp
		

static func set_data(target, data):
	if typeof(data) == TYPE_DICTIONARY:
		var obj = target.class_type().new()
		for field in data:
			var field_snake_case = field.to_snake_case()
			print("setting " + field_snake_case + " to " + str(data[field]))
			if typeof(data[field]) == TYPE_ARRAY:
				obj[field_snake_case] = set_data(target[field_snake_case], data[field])
			else:
				obj[field_snake_case] = set_data(target[field_snake_case], data[field])
		return obj
	elif typeof(data) == TYPE_ARRAY:
		if (target != null and target.size() == 1):
			for d in data:
				var obj = target[0].class_type().new()
				for field in d:
					var field_snake_case = field.to_snake_case()
					obj[field_snake_case] = set_data(obj[field_snake_case], d[field])
				if (typeof(target) == TYPE_DICTIONARY):
					target[int(obj["id"])] = obj
					target.erase(0)
				else:
					target.append(obj)
					target.remove_at(0)
			return target
		else:
			var obj = []
			for d in data:
				obj.append(set_data(target, d))
			return obj
	return data
	
	
# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
