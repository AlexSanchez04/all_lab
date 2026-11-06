import bpy
import math
import numpy as np


STEP_X = 4.0         
Z = 0.0               

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials,
                 bpy.data.cameras, bpy.data.lights):
        for b in list(coll):
            if b.users == 0:
                coll.remove(b)

clear_scene()

#
#  КЕЙС 1. Куб VR_Cube на высоте 1 м

X1 = 0.0
bpy.ops.mesh.primitive_cube_add(location=(X1, 0, 1.0))
cube = bpy.context.active_object
cube.name = "VR_Cube"
print(f"[1] Создан объект: {cube.name} | Вершин: {len(cube.data.vertices)}")


#  КЕЙС 2. PBR-материал на VR_Cube

mat = bpy.data.materials.new(name="VR_Material")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.1, 0.3, 0.8, 1.0)
bsdf.inputs["Roughness"].default_value = 0.3
cube.data.materials.append(mat)
print(f"[2] Материал назначен: {mat.name} | Материалов: {len(cube.data.materials)}")


#  КЕЙС 3. Стереокамера

X3 = 1 * STEP_X
bpy.ops.object.camera_add(location=(X3, 0, 1.6))
cam = bpy.context.active_object
cam.name = "VR_Camera"
bpy.context.scene.render.use_multiview = True
bpy.context.scene.render.views_format = 'STEREO_3D'
cam.data.stereo.interocular_distance = 0.065
print(f"[3] Стерео: {bpy.context.scene.render.use_multiview} | IPD: {cam.data.stereo.interocular_distance}")


#  КЕЙС 4. Decimate на иксофере

X4 = 2 * STEP_X
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, location=(X4, 0, 1.0))
ico = bpy.context.active_object
ico.name = "VR_Ico_Decimated"
before = len(ico.data.polygons)
target = int(before * 0.25)
mod = ico.modifiers.new(name="Decimate", type='DECIMATE')
mod.ratio = 0.25
bpy.ops.object.modifier_apply(modifier=mod.name)
print(f"[4] Было: {before} | Цель: {target} | Стало: {len(ico.data.polygons)}")


#  КЕЙС 5. Сетка 5×5

X5, Y5 = 3 * STEP_X, -6.0
SPACING = 1.5
count = 0
for row in range(5):
    for col in range(5):
        bpy.ops.mesh.primitive_cube_add(
            location=(X5 + col * SPACING, Y5 + row * SPACING, 0.5))
        bpy.context.active_object.name = f"Tile_{row}_{col}"
        count += 1
print(f"[5] Создано объектов: {count}")


#  КЕЙС 6. Sun

X6 = 4 * STEP_X
bpy.ops.object.light_add(type='SUN', location=(X6, 0, 5.0))
sun = bpy.context.active_object
sun.name = "VR_Sun"
sun.data.energy = 4.0
print(f"[6] Источник: {sun.name} | Тип: {sun.data.type} | Мощность: {sun.data.energy}")


#  КЕЙС 7. Анимация вращения

X7 = 5 * STEP_X
bpy.ops.mesh.primitive_cube_add(location=(X7, 0, 1.0))
anim = bpy.context.active_object
anim.name = "VR_Anim_Cube"
scene = bpy.context.scene
scene.frame_start, scene.frame_end = 1, 60
anim.rotation_euler = (0, 0, 0)
anim.keyframe_insert(data_path="rotation_euler", frame=1)
anim.rotation_euler = (0, 0, 2 * math.pi)
anim.keyframe_insert(data_path="rotation_euler", frame=60)
print(f"[7] Анимация: кадры {scene.frame_start}-{scene.frame_end} | Ключей: 2")


#  КЕЙС 8. Экспорт сцены в GLB

path = "/tmp/vr_scene.glb"
bpy.ops.export_scene.gltf(filepath=path, export_format='GLB')
print(f"[8] Экспортировано в: {path}")


#  КЕЙС 9. Позиции глаз по IPD

head = np.array([0.0, -2.0, 1.6])
ipd = 0.065
left  = head + np.array([-ipd/2, 0, 0])
right = head + np.array([ ipd/2, 0, 0])
print(f"[9] Левый: {left} | Правый: {right} | Расстояние: {np.linalg.norm(right-left):.3f} м")


#  КЕЙС 10. Ширина видимой области по FOV

fov, dist, obj_w = 100.0, 5.0, 2.0
width = 2 * dist * math.tan(math.radians(fov) / 2)
print(f"[10] Ширина: {width:.2f} м | Доля кадра: {obj_w/width*100:.1f}%")


#  КЕЙС 11. Кватернион поворота на 90° вокруг Z

angle = math.radians(90)
w = math.cos(angle / 2)
xyz = np.array([0, 0, 1]) * math.sin(angle / 2)
q = np.array([w, *xyz])
fwd = np.array([0, 1, 0])

def q_rotate(q, v):
    w, x, y, z = q
    R = np.array([
        [1-2*(y*y+z*z), 2*(x*y-z*w),   2*(x*z+y*w)],
        [2*(x*y+z*w),   1-2*(x*x+z*z), 2*(y*z-x*w)],
        [2*(x*z-y*w),   2*(y*z+x*w),   1-2*(x*x+y*y)],
    ])
    return R @ v

print(f"[11] Кватернион: {q} | Взгляд после 90° по Z: {q_rotate(q, fwd)}")


#  КЕЙС 12. Бюджет кадра

for hz in (72, 90, 120):
    print(f"[12] {hz} Гц -> бюджет {1000/hz:.2f} мс")
render = 9.5
print(f"[12] Рендер {render} мс при 90 Гц: {'успеваем' if render <= 1000/90 else 'не успеваем'}")


#  КЕЙС 13. LOD по расстоянию

def lod(d):
    if d < 5:  return "LOD0 (высокая)"
    if d < 20: return "LOD1 (средняя)"
    if d < 50: return "LOD2 (низкая)"
    return "culled (не рендерится)"

for d in (2, 10, 35, 80):
    print(f"[13] {d} м -> {lod(d)}")


#  КЕЙС 14. Полигональный бюджет

budget, per = 1_000_000, 8_000
max_objs = budget // per
load = 150 * per
print(f"[14] Бюджет: {budget:,} | На объект: {per:,} | Макс объектов: {max_objs}")
print(f"[14] 150 объектов = {load:,} -> {'ПРЕВЫШЕН' if load > budget else 'OK'}")


#  КЕЙС 15. Motion-to-photon

stages = {"Трекинг": 2.0, "Обработка": 3.0, "Рендер": 11.0, "Вывод": 4.0}
total = sum(stages.values())
print(f"[15] Сумма задержки: {total} мс | Комфортно (<20 мс)? {total < 20}")