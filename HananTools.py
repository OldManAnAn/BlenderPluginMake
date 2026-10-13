# batch_tools_for_scene.py
# 批量场景处理工具集 —— 可安装的 Blender 插件

import bpy
from mathutils import Matrix, Vector
import re

bl_info = {
    "name": "Batch Scene Tools",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "3D View > Sidebar > Batch Tools",
    "description": "批量处理空物体、重命名、对齐原点、应用变换等常用操作",
    "category": "Object",
}


# ────────────────────────────────
# 工具函数
# ────────────────────────────────

def get_type_prefix(obj):
    """根据物体类型返回前缀名称"""
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


# ────────────────────────────────
# 操作类：删除空物体
# ────────────────────────────────

class OBJECT_OT_delete_empties(bpy.types.Operator):
    bl_idname = "object.delete_empties_keep_children"
    bl_label = "删除所有空物体（保留子级位置）"
    bl_description = "删除场景中所有空物体，但保留其子物体的世界位置不变"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        empties = [obj for obj in bpy.data.objects if obj.type == 'EMPTY']
        if not empties:
            self.report({'INFO'}, "ℹ️ 场景中没有空物体")
            return {'CANCELLED'}

        # 按深度排序：子级在前，父级在后
        def get_depth(obj, depth=0):
            return get_depth(obj.parent, depth + 1) if obj.parent else depth

        empties_sorted = sorted(empties, key=get_depth, reverse=True)

        removed_count = 0
        child_count = 0

        for empty in empties_sorted:
            children = [(child, child.matrix_world.copy()) for child in empty.children]
            for child, world_matrix in children:
                child.parent = None
                child.matrix_world = world_matrix
                child_count += 1
            bpy.data.objects.remove(empty, do_unlink=True)
            removed_count += 1

        self.report({'INFO'}, f"✅ 已删除 {removed_count} 个空物体，提升 {child_count} 个子物体")
        return {'FINISHED'}


# ────────────────────────────────
# 操作类：按父级重命名子物体
# ────────────────────────────────

class OBJECT_OT_rename_object_data_to_object_name(bpy.types.Operator):
    bl_idname = "object.rename_object_data_to_object_name"
    bl_label = "重命名绿色数据为物体名"
    bl_description = "将选中物体的 Object Data（绿色节点）重命名为与物体名一致"
    bl_options = {'REGISTER', 'UNDO'}

    prefix: bpy.props.StringProperty(name="前缀", default="")
    suffix: bpy.props.StringProperty(name="后缀", default="")
    only_mesh: bpy.props.BoolProperty(
        name="仅处理 Mesh",
        default=False,
    )
    make_single_user: bpy.props.BoolProperty(
        name="单用户化后再改名",
        default=False,
        description="当多个物体共享同一份 data 时，先复制为单用户再改名，避免影响其他物体",
    )

    def execute(self, context):
        targets = list(context.selected_objects)
        if not targets and context.active_object:
            targets = [context.active_object]

        if not targets:
            self.report({'WARNING'}, "未选择任何物体")
            return {'CANCELLED'}

        renamed = 0
        skipped = 0

        for obj in targets:
            if self.only_mesh and obj.type != 'MESH':
                skipped += 1
                continue

            data = getattr(obj, "data", None)
            if data is None:
                skipped += 1
                continue

            if self.make_single_user and getattr(data, "users", 1) > 1 and hasattr(data, "copy"):
                obj.data = data.copy()
                data = obj.data

            data.name = f"{self.prefix}{obj.name}{self.suffix}"
            renamed += 1

        self.report({'INFO'}, f"已重命名 {renamed} 个数据块，跳过 {skipped} 个")
        return {'FINISHED'}

# ────────────────────────────────
# 操作类：Mesh 原点居中 + 应用变换
# ────────────────────────────────

class OBJECT_OT_origin_to_center_and_apply(bpy.types.Operator):
    bl_idname = "object.origin_to_center_and_apply"
    bl_label = "原点居中并应用变换"
    bl_description = "将所有 Mesh 物体的原点设为几何中心，并应用全部变换"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
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
        return {'FINISHED'}


# ────────────────────────────────
# 操作类：底面对齐 Z=0
# ────────────────────────────────

class OBJECT_OT_align_bottom_to_z0(bpy.types.Operator):
    bl_idname = "object.align_bottom_to_z0"
    bl_label = "底面对齐 Z=0"
    bl_description = "将所有 Mesh 物体底部对齐到世界 Z=0 平面，并应用变换"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        count = 0
        for obj in bpy.data.objects:
            if obj.type != 'MESH':
                continue
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            bbox_world = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            min_z = min(v.z for v in bbox_world)
            obj.location.z -= min_z
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            obj.select_set(False)
            count += 1
        self.report({'INFO'}, f"✅ 已对齐 {count} 个 Mesh 物体到底部 Z=0")
        return {'FINISHED'}


# ────────────────────────────────
# 操作类：左后角对齐 X=0, Y=0
# ────────────────────────────────

class OBJECT_OT_align_corner_to_xy0(bpy.types.Operator):
    bl_idname = "object.align_corner_to_xy0"
    bl_label = "左后角对齐 (X=0, Y=0)"
    bl_description = "将所有 Mesh 物体最左（最小 X）、最后（最小 Y）点对齐到 (0,0)，并应用变换"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        count = 0
        for obj in bpy.data.objects:
            if obj.type != 'MESH':
                continue
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            bbox_world = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            min_x = min(v.x for v in bbox_world)
            min_y = min(v.y for v in bbox_world)
            obj.location.x -= min_x
            obj.location.y -= min_y
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            obj.select_set(False)
            count += 1
        self.report({'INFO'}, f"✅ 已对齐 {count} 个 Mesh 物体到左后角 (X=0, Y=0)")
        return {'FINISHED'}


# ────────────────────────────────
# 面板类：UI 界面
# ────────────────────────────────

class VIEW3D_PT_batch_scene_tools(bpy.types.Panel):
    bl_label = "批量场景工具"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Batch Tools"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        col.label(text="空物体处理:")
        col.operator("object.delete_empties_keep_children", icon='TRASH')

        col.separator()
        col.label(text="重命名工具:")
        col.operator("object.rename_children_by_parent", icon='SORTALPHA')
        col.operator("object.rename_object_data_to_object_name", icon='SORTALPHA')

        col.separator()
        col.label(text="原点与对齐:")
        col.operator("object.origin_to_center_and_apply", icon='PIVOT_BOUNDBOX')
        col.operator("object.align_bottom_to_z0", icon='ALIGN_BOTTOM')
        col.operator("object.align_corner_to_xy0", icon='ALIGN_LEFT')


# ────────────────────────────────
# 注册/注销
# ────────────────────────────────

classes = (
    OBJECT_OT_delete_empties,
    OBJECT_OT_rename_object_data_to_object_name,
    OBJECT_OT_origin_to_center_and_apply,
    OBJECT_OT_align_bottom_to_z0,
    OBJECT_OT_align_corner_to_xy0,
    VIEW3D_PT_batch_scene_tools,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


# ────────────────────────────────
# 本地测试（可选）
# ────────────────────────────────

if __name__ == "__main__":
    register()