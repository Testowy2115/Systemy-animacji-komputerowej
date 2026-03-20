import bpy
import math
import os

from matplotlib.pylab import rand


def clean_scene():
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
        
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_materials():
    # Materiał dla łodygi i korzeni
    mat_stem = bpy.data.materials.new(name="MatLodyga")
    mat_stem.use_nodes = True
    bsdf_stem = mat_stem.node_tree.nodes["Principled BSDF"]
    bsdf_stem.inputs["Base Color"].default_value = (0.3, 0.2, 0.05, 1)
    bsdf_stem.inputs["Metallic"].default_value = 0.0
    bsdf_stem.inputs["Roughness"].default_value = 0.6

    # Materiał dla liści
    mat_leaf = bpy.data.materials.new(name="MatLisc")
    mat_leaf.use_nodes = True
    bsdf_leaf = mat_leaf.node_tree.nodes["Principled BSDF"]
    bsdf_leaf.inputs["Base Color"].default_value = (0.15, 0.55, 0.1, 1.0)
    bsdf_leaf.inputs["Metallic"].default_value = 0.0
    bsdf_leaf.inputs["Roughness"].default_value = 0.4
    
    return mat_stem, mat_leaf

def stworz_lodyge(location, height, material):
    cx, cy, cz = location
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.15,
        depth=height,
        location=(cx, cy, cz + height / 2)
    )
    obj = bpy.context.active_object
    obj.name = "Lodyga"
    if material:
        obj.data.materials.append(material)
    return obj

def stworz_liscie(location, height, num_leaves, radius_leaves, material):
    cx, cy, cz = location
    top_z = cz + height
    
    for i in range(num_leaves):
        angle = (2 * math.pi / num_leaves) * i
        
        dist = 0.3
        
        lx = cx + math.cos(angle) * dist
        ly = cy + math.sin(angle) * dist
        lz = top_z - 0.2
        
        bpy.ops.mesh.primitive_cube_add(
            size=radius_leaves,
            location=(lx, ly, lz),
            rotation=(0.3, 0.2, angle)
        )
        obj = bpy.context.active_object
        obj.name = f"Lisc_{i}"
        obj.scale = (1.2, 0.4, 1.0) 
        if material:
            obj.data.materials.append(material)

def stworz_korzenie(location, num_roots, material):
    cx, cy, cz = location
    
    for i in range(num_roots):
        angle = (2 * math.pi / num_roots) * i
        dist = 0.25
        
        rx = cx + math.cos(angle) * dist
        ry = cy + math.sin(angle) * dist
        rz = cz 
        
        bpy.ops.mesh.primitive_cube_add(
            size=0.15,
            location=(rx, ry, rz),
            rotation=(0, 0, angle)
        )
        obj = bpy.context.active_object
        obj.name = f"Korzen_{i}"
        if material:
            obj.data.materials.append(material)

def stworz_rosline(wysokosc=2.0, liczbalisci=3, promienlisci=0.3, liczbakorzeni=4, x_pos=0.0):
    location = (x_pos, 0, 0)
    mat_stem = bpy.data.materials.get("MatLodyga")
    mat_leaf = bpy.data.materials.get("MatLisc")
    if not mat_stem or not mat_leaf:
         mat_stem, mat_leaf, _ = create_materials()

    
    stworz_lodyge(location, wysokosc, mat_stem)
    stworz_liscie(location, wysokosc, liczbalisci, promienlisci, mat_leaf)
    stworz_korzenie(location, liczbakorzeni, mat_stem)



clean_scene()
mat_stem, mat_leaf = create_materials()

stworz_rosline(wysokosc=1.5, liczbalisci=4, promienlisci=0.35, liczbakorzeni=3, x_pos=-3.5)
stworz_rosline(wysokosc=2.5, liczbalisci=6, promienlisci=0.45, liczbakorzeni=5, x_pos=0.0)
stworz_rosline(wysokosc=3.0, liczbalisci=7, promienlisci=0.55, liczbakorzeni=6, x_pos=3.5)

bpy.ops.object.light_add(type='SUN', location=(5, -8, 5))
sun = bpy.context.active_object
sun.name = "Slonce"
sun.data.energy = 3.0
sun.data.angle = 0.9

bpy.ops.object.light_add(type='POINT', location=(-3, 5, 3))
fill_light = bpy.context.active_object
fill_light.name = "Swiatlo"
fill_light.data.energy = 500

# Kamera
bpy.ops.object.camera_add(location=(0, -12, 5))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(75), 0, 0) 
bpy.context.scene.camera = cam

# Render
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.filepath = os.path.abspath("rosliny_lab04.png")
scene.render.image_settings.file_format = 'PNG'
scene.render.resolution_x = 1200
scene.render.resolution_y = 900
bpy.ops.render.render(write_still=True)
print("Render zakończony.")
