# -*- coding: utf-8 -*-
"""
ЗАДАНИЕ (основа для студента).

Соберите СВОЕГО персонажа из примитивов Blender средствами Python (bpy):
зайчика, кота, мишку, снеговика, робота, гриб — на ваш выбор.

Ниже уже готов «инструментарий» — функции для материалов, примитивов, света,
камеры и рендера. Вам нужно в разделе «СОБЕРИТЕ СВОЕГО ПЕРСОНАЖА» (# TODO)
скомпоновать фигуру из этих функций. Сейчас там для примера собран простой
снеговик — замените его на своего персонажа.

Как запустить (в Blender):
  1) откройте Blender → вкладка Scripting → New;
  2) вставьте этот код и нажмите Run Script (или Alt+P);
  3) персонаж появится в 3D-вьюпорте; картинка сохранится рядом со сценой.
"""
import bpy
import math


# ====================== ИНСТРУМЕНТАРИЙ (менять не нужно) ======================
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials):
        for b in list(coll):
            coll.remove(b)


def make_material(name, color, metallic=0.0, roughness=0.6, emission=None):
    """Создаёт материал. color/emission — кортеж (r, g, b) в диапазоне 0..1."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 5.0
    return mat


def add_sphere(name, location, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(material)
    return obj


def add_cube(name, location, scale, material, bevel=0.06):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    m = obj.modifiers.new("Bevel", 'BEVEL'); m.width = bevel; m.segments = 3
    obj.modifiers.new("Subdiv", 'SUBSURF').levels = 1
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(material)
    return obj


def add_cylinder(name, location, radius, depth, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = rotation
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(material)
    return obj


def add_cone(name, location, radius, depth, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=radius, depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = rotation
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(material)
    return obj


def setup_scene(bg_color=(0.75, 0.85, 0.95), cam_location=(0, -7.5, 2.3), cam_pitch_deg=83):
    """Пол, два источника света, камера, фон, настройки рендера."""
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -0.02))
    bpy.context.active_object.data.materials.append(make_material("Ground", (0.8, 0.84, 0.8), roughness=0.9))
    bpy.ops.object.light_add(type='AREA', location=(4, -4, 6))
    bpy.context.active_object.data.energy = 900; bpy.context.active_object.data.size = 6
    bpy.ops.object.light_add(type='AREA', location=(-5, -3, 3))
    bpy.context.active_object.data.energy = 300; bpy.context.active_object.data.size = 8
    bpy.ops.object.camera_add(location=cam_location)
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(cam_pitch_deg), 0, 0)
    cam.data.lens = 52
    bpy.context.scene.camera = cam
    world = bpy.data.worlds[0]
    bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (*bg_color, 1.0)


def render(filepath):
    scene = bpy.context.scene
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)


# =============================================================================
clear_scene()

# материалы (добавьте свои цвета)
WHITE = make_material("White", (0.95, 0.95, 0.97), roughness=0.8)
ORANGE = make_material("Orange", (0.95, 0.5, 0.1), roughness=0.5)
BLACK = make_material("Black", (0.03, 0.03, 0.03), roughness=0.3)

# ======================= СОБЕРИТЕ СВОЕГО ПЕРСОНАЖА (# TODO) ====================
# Пример-заготовка: простой снеговик из трёх шаров.
# ЗАМЕНИТЕ его на своего персонажа (зайчик, кот, мишка, робот, гриб...).

add_sphere("Snow_Bottom", (0, 0, 0.9), (1.0, 1.0, 1.0), WHITE)
add_sphere("Snow_Middle", (0, 0, 2.1), (0.72, 0.72, 0.72), WHITE)
add_sphere("Snow_Head",   (0, 0, 3.0), (0.5, 0.5, 0.5), WHITE)
add_cone("Nose", (0, -0.5, 3.0), 0.08, 0.4, ORANGE, rotation=(math.radians(-90), 0, 0))
add_sphere("Eye_L", (-0.18, -0.46, 3.12), (0.06, 0.06, 0.06), BLACK)
add_sphere("Eye_R", ( 0.18, -0.46, 3.12), (0.06, 0.06, 0.06), BLACK)

# TODO: добавьте больше деталей — руки, пуговицы, шапку, уши и т.д.

# =============================================================================
setup_scene(bg_color=(0.78, 0.88, 0.96))
render("/home/claude/blender/my_character.png")   # путь можно поменять
print("Готово. Объектов в сцене:", len(bpy.data.objects))
