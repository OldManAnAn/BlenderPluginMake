import bpy

# 取消全选（可选，避免干扰）
bpy.ops.object.select_all(action='DESELECT')

processed = 0

for obj in bpy.data.objects:
    # 仅处理类型为 MESH 且在视图中可见的物体
    if obj.type == 'MESH' and not obj.hide_viewport and not obj.hide_get():
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # 1. 将原点设为几何中心
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        
        # 2. 移动物体到世界原点（此时 location 就是几何中心的世界坐标）
        obj.location = (0, 0, 0)
        
        # 3. 应用变换
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
        obj.select_set(False)
        processed += 1

print(f"✅ 已处理 {processed} 个可见的 Mesh 物体：居中并应用变换。")