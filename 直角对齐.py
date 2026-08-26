import bpy
from mathutils import Vector

bpy.ops.object.select_all(action='DESELECT')

for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue

    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # 应用旋转和缩放
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    # 获取世界空间边界框
    bbox_world = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

    # 找最左（最小 X）、最后（最小 Y）
    min_x = min(v.x for v in bbox_world)
    min_y = min(v.y for v in bbox_world)

    # 移动：让最左点到 X=0，最后点到 Y=0
    obj.location.x -= min_x
    obj.location.y -= min_y

    # 应用变换
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.select_set(False)

print("✅ 所有模型已左后角对齐到 (X=0, Y=0)！")