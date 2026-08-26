import bpy
from mathutils import Matrix

# 获取场景中所有空物体（按依赖顺序：从最深到最浅，避免提前删除父级）
empties = [obj for obj in bpy.data.objects if obj.type == 'EMPTY']

if not empties:
    print("ℹ️ 场景中没有空物体")
else:
    # 按深度排序：子级在前，父级在后（防止父级被删后子级 world_matrix 错误）
    def get_depth(obj, depth=0):
        if obj.parent:
            return get_depth(obj.parent, depth + 1)
        return depth

    empties_sorted = sorted(empties, key=get_depth, reverse=True)

    removed_count = 0
    child_count = 0

    for empty in empties_sorted:
        # 保存子物体及其当前世界矩阵
        children = []
        for child in empty.children:
            children.append((child, child.matrix_world.copy()))

        # 解除父子关系并恢复世界位置
        for child, world_matrix in children:
            child.parent = None
            child.matrix_world = world_matrix
            child_count += 1

        # 删除空物体
        bpy.data.objects.remove(empty, do_unlink=True)
        removed_count += 1

    print(f"✅ 已删除 {removed_count} 个空物体，保留并提升 {child_count} 个子物体（世界位置不变）")