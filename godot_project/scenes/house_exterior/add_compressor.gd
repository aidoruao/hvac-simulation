extends Node
func _ready():
    var gen = load("res://assets/models/compressor_mesh_gen.gd")
    if gen:
        var compressor = gen.new().generate()
        compressor.name = "ProceduralCompressor"
        compressor.position = Vector3(0, 0.5, 0)
        add_child(compressor)
        print("PROCEDURAL_COMPRESSOR_ADDED: ", compressor.get_child_count(), " children")
    else:
        print("GENERATOR_NOT_FOUND")
