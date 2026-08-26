import bpy
import os
import re

def sanitize_filename(name):
    name = ''.join(ch for ch in name if ord(ch) >= 32 and ord(ch) != 127)
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = name.strip().strip('.')
    return name if name else "unnamed"

# 设置导出目录（使用原始字符串避免转义问题）
export_dir = r"E:\BaiduSyncdisk\LiaoHanan_Workspace\Cocos_Project\TengXun\PUBG_Project\Asset\房子2\fbx\lowpoly-buildings_extracted\textures\1212"
os.makedirs(export_dir, exist_ok=True)

# 获取要导出的 Mesh 对象
objects_to_export = [obj for obj in bpy.data.objects if obj.type == 'MESH' and not obj.hide_viewport]

bpy.ops.object.select_all(action='DESELECT')

for obj in objects_to_export:
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    safe_name = sanitize_filename(obj.name)
    filepath = os.path.join(export_dir, f"{safe_name}.glb")

    # Blender 4.4 兼容的导出参数
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        use_selection=True,
        export_format='GLB',
        export_apply=True,
        export_materials='NONE',
        export_draco_mesh_compression_enable=True,
        export_draco_position_quantization=10,   # 默认14
        export_draco_normal_quantization=8,      # 默认10
        export_draco_texcoord_quantization=10,   # 默认12
        export_draco_color_quantization=8,       # 默认8
        export_draco_generic_quantization=8      # 默认12
        # 注意：不再包含 export_colors, export_cameras 等旧参数
    )

    obj.select_set(False)

print(f"✅ 成功导出 {len(objects_to_export)} 个 GLB 文件到: {export_dir}")