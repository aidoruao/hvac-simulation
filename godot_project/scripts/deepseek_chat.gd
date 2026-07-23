class_name DeepSeekChat
extends RefCounted

var api_key: String = ""
var _on_complete: Callable
var _deferred_done: bool = false

func _init(p_key: String):
	api_key = p_key

func chat(prompt: String, on_complete: Callable) -> Error:
	_on_complete = on_complete
	var http = HTTPRequest.new()
	http.set_meta("_owner", self)
	http.request_completed.connect(_on_response)
	
	var headers = [
		"Authorization: Bearer " + api_key,
		"Content-Type: application/json"
	]
	var body = JSON.stringify({
		"model": "deepseek-chat",
		"messages": [{"role": "user", "content": prompt}]
	})
	
	http.set_meta("_url", "https://api.deepseek.com/v1/chat/completions")
	http.set_meta("_headers", headers)
	http.set_meta("_body", body)
	
	var tree = Engine.get_main_loop()
	if tree and tree is SceneTree:
		tree.process_frame.connect(_deferred_add.bind(http, tree))
	else:
		tree.root.add_child(http)
	return OK

func _deferred_add(http: HTTPRequest, tree: SceneTree):
	if _deferred_done:
		return
	_deferred_done = true
	tree.root.add_child(http)
	http.request(
		http.get_meta("_url"),
		http.get_meta("_headers"),
		HTTPClient.METHOD_POST,
		http.get_meta("_body")
	)

func _on_response(result: int, code: int, _headers: PackedStringArray, body: PackedByteArray):
	var text = body.get_string_from_utf8()
	var json = JSON.parse_string(text)
	var response = ""
	if json and json.has("choices") and json.choices.size() > 0:
		response = json.choices[0].message.content
	else:
		response = "ERROR: " + text.substr(0, 200)
	
	_on_complete.call(response)
