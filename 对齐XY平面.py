import bpy
from mathutils import Vector

# 取消全选
bpy.ops.object.select_all(action='DESELECT')

for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue

    # 选中物体并设为 active
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # 1. 应用缩放和旋转（避免 bbox 计算错误）
    # 注意：先应用非位移变换，再计算边界
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)




    # 2. 获取世界空间下的边界框（8个顶点）
    bbox_world = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    
    # 3. 找出最小 Z 坐标（底边高度）
    min_z = min(v.z for v in bbox_world)

    # 4. 将物体向上移动 -min_z，使底边落在 Z=0
    obj.location.z -= min_z

    # 5. 再次应用全部变换（包括新位置）
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # 取消选中
    obj.select_set(False)

print("✅ 所有 Mesh 物体底边已对齐到 Z=0 并应用变换！")