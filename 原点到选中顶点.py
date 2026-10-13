import bpy
import bmesh
from mathutils import Vector

obj = bpy.context.edit_object
if obj is None or obj.type != 'MESH':
    raise RuntimeError("请先在网格物体的编辑模式中选中顶点")

bm = bmesh.from_edit_mesh(obj.data)
verts = [v for v in bm.verts if v.select]
if not verts:
    raise RuntimeError("没有选中的顶点")

center_local = sum((v.co for v in verts), Vector()) / len(verts)
center_world = obj.matrix_world @ center_local
cursor = bpy.context.scene.cursor
old_cursor = cursor.location.copy()

try:
    bpy.ops.object.mode_set(mode='OBJECT')
    cursor.location = center_world
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
finally:
    cursor.location = old_cursor
    bpy.ops.object.mode_set(mode='EDIT')

print(f"原点已移动到 {center_world}")