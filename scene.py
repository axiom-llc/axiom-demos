import json
import os
import bpy

DEFAULT_CONFIG = {
    "camera": {
        "location": [7.0, -9.0, 6.0],
        "ortho_scale": 7.0,
    },
    "cube": {
        "location": [0.0, 0.0, 2.0],
        "size": 2.0,
        "color": [0.35, 0.45, 0.6, 1.0],
        "metallic": 1.0,
        "roughness": 0.25,
    },
    "world": {
        "color": [0.3, 0.3, 0.3, 1.0],
        "strength": 0.5,
    },
    "lights": [
        {
            "location": [2.0, -4.0, 7.0],
            "energy": 1800.0,
            "size": 5.0,
        },
        {
            "location": [-4.0, 1.0, 5.0],
            "energy": 1200.0,
            "size": 4.0,
        },
    ],
}


def load_config(config_path):
    if os.path.isfile(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_CONFIG


def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def setup_scene(output_dir):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = output_dir + "/render.png"
    return scene


def create_geometry(cube_cfg):
    bpy.ops.mesh.primitive_plane_add(size=200)
    ground = bpy.context.object
    ground.name = "Ground"

    # The two-meter cube's bottom face is one meter above the ground.
    bpy.ops.mesh.primitive_cube_add(
        size=cube_cfg["size"], location=cube_cfg["location"]
    )
    cube = bpy.context.object
    cube.name = "Metal Cube"
    return ground, cube


def create_material(target_object, cube_cfg):
    metal = bpy.data.materials.new("Metal")
    shader = metal.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = cube_cfg["color"]
    shader.inputs["Metallic"].default_value = cube_cfg["metallic"]
    shader.inputs["Roughness"].default_value = cube_cfg["roughness"]
    target_object.data.materials.append(metal)
    return metal


def apply_ground_material(ground, ground_cfg):
    mat = bpy.data.materials.new("GroundMaterial")
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = ground_cfg["color"]
    shader.inputs["Roughness"].default_value = ground_cfg["roughness"]
    ground.data.materials.append(mat)
    return mat


def setup_lighting(target_object, scene, world_cfg, lights_cfg):
    scene.world = bpy.data.worlds.new("World")
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = world_cfg["color"]
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = world_cfg["strength"]

    for item in lights_cfg:
        bpy.ops.object.light_add(type="AREA", location=item["location"])
        light = bpy.context.object
        light.data.energy = item["energy"]
        light.data.shape = "DISK"
        light.data.size = item["size"]
        light.rotation_euler = (target_object.location - light.location).to_track_quat("-Z", "Y").to_euler()


def setup_camera(target_object, scene, camera_cfg):
    bpy.ops.object.camera_add(location=camera_cfg["location"])
    camera = bpy.context.object
    camera.rotation_euler = (target_object.location - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = camera_cfg["ortho_scale"]
    scene.camera = camera
    return camera


def save_and_render(output_dir):
    bpy.ops.wm.save_as_mainfile(filepath=output_dir + "/scene.blend")
    bpy.ops.render.render(write_still=True)


def main():
    output_dir = __file__.rsplit("/", 1)[0]
    config = load_config(output_dir + "/scene.json")

    reset_scene()
    scene = setup_scene(output_dir)
    ground, cube = create_geometry(config["cube"])
    create_material(cube, config["cube"])
    if "ground" in config and config["ground"]:
        apply_ground_material(ground, config["ground"])
    setup_lighting(cube, scene, config["world"], config["lights"])
    setup_camera(cube, scene, config["camera"])
    save_and_render(output_dir)


if __name__ == "__main__":
    main()
