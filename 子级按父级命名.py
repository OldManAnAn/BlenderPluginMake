import bpy

def get_type_prefix(obj):
    type_map = {
        'MESH': 'Mesh',
        'LIGHT': 'Light',
        'CAMERA': 'Camera',
        'EMPTY': 'Empty',
        'ARMATURE': 'Armature',
        'CURVE': 'Curve',
        'FONT': 'Text',
        'SURFACE': 'Surface',
        'META': 'Meta',
        'VOLUME': 'Volume',
        'GPENCIL': 'GreasePencil',
        'LATTICE': 'Lattice',
        'SPEAKER': 'Speaker'
    }
    return type_map.get(obj.type, 'Object')

# 获取所有选中的物体作为父级根（不再限制为 Empty）
parent_roots = [obj for obj in bpy.context.selected_objects]

if not parent_roots:
    print("⚠️ 请先选中至少一个物体作为父级根节点")
else:
    renamed_count = 0

    for parent in parent_roots:
        children = list(parent.children_recursive)
        if not children:
            print(f"ℹ️ '{parent.name}' 没有子物体，跳过")
            continue

        # 按子物体类型分组
        type_groups = {}
        for child in children:
            t = child.type
            if t not in type_groups:
                type_groups[t] = []
            type_groups[t].append(child)

        # 对每种类型分别编号重命名
        for obj_type, obj_list in type_groups.items():
            type_name = get_type_prefix(obj_list[0])
            for i, obj in enumerate(obj_list, 1):
                new_name = f"{parent.name}_{type_name}_{i:03d}"
                obj.name = new_name

                # 如果是 Mesh，同步重命名网格数据
                if obj.type == 'MESH' and obj.data:
                    obj.data.name = new_name

                renamed_count += 1

    print(f"✅ 成功重命名 {renamed_count} 个子物体（Mesh 数据已同步）")