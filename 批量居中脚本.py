import bpy

# 取消全选
bpy.ops.object.select_all(action='DESELECT')

# 遍历所有 mesh 物体（可按需修改筛选条件）
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        # 选中物体
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # 1. 将原点设置到几何中心
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        
        # 2. 获取当前世界位置（即几何中心的世界坐标）
        world_loc = obj.location.copy()
        
        # 3. 将物体整体移动到世界原点（抵消当前位置）
        obj.location = (0, 0, 0)
        
        # 4. 应用变换（位置、旋转、缩放）
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
        # 取消选中
        obj.select_set(False)

print("✅ 所有 Mesh 物体已居中并应用变换！")