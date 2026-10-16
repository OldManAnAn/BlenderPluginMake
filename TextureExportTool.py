# export_used_textures.py

import bpy  # Blender Python API
import os   # 操作系统接口模块
import shutil  # 高级文件操作模块
import re  # 正则表达式模块，用于清理文件名

bl_info = {
    "name": "Export Used Textures",  # 插件名称
    "author": "Hanan",  # 作者名字
    "version": (1, 2),  # 版本号
    "blender": (4, 0, 0),  # 支持的Blender最低版本
    "location": "3D View > Sidebar > My Tools",  # 插件在Blender中的位置
    "description": "导出当前场景中所有材质使用到的贴图（包括嵌入图像）",  # 描述
    "category": "Import-Export",  # 分类
}

def sanitize_filename(name):
    """
    清理文件名，移除或替换不合法字符。
    """
    return re.sub(r'[^\w._-]', '_', name)  # 使用正则表达式保留合法字符

class EXPORT_OT_used_textures(bpy.types.Operator):
    bl_idname = "export_texture.used_textures"  # 操作ID
    bl_label = "导出所有贴图"  # 操作标签
    bl_description = "导出当前 .blend 文件中所有材质用到的贴图到指定文件夹"  # 描述
    bl_options = {'REGISTER', 'UNDO'}  # 注册并允许撤销
    
    directory: bpy.props.StringProperty(
        name="导出目录",
        description="选择导出贴图的目标目录",
        subtype='DIR_PATH'  # 类型为目录路径
    )

    def execute(self, context):
        """
        执行导出操作。
        """
        export_dir = self.directory  # 获取用户选择的导出目录
        if not export_dir:
            self.report({'ERROR'}, "未选择导出目录！")  # 如果没有选择目录，报告错误
            return {'CANCELLED'}

        os.makedirs(export_dir, exist_ok=True)  # 确保导出目录存在
        
        used_images = set()  # 创建一个集合存储使用的图片
        
        # 循环遍历所有材质查找使用的贴图
        for mat in bpy.data.materials:
            if not mat.use_nodes or not mat.node_tree:
                continue
            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    used_images.add(node.image)

        # 同样检查世界环境节点树中的贴图
        for world in bpy.data.worlds:
            if world.use_nodes and world.node_tree:
                for node in world.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        used_images.add(node.image)

        if not used_images:
            self.report({'WARNING'}, "未找到任何贴图！")  # 如果没有找到贴图，报告警告
            return {'CANCELLED'}

        exported_count = 0  # 记录已导出的贴图数量
        for img in used_images:
            if not img.has_data:
                print(f"⚠️ 跳过无像素数据的图像: {img.name}")  # 跳过没有像素数据的图像
                continue
            
            ext = ".png"  # 默认扩展名为PNG
            if img.file_format and img.file_format != 'NONE':
                ext = '.' + img.file_format.lower()  # 根据图像格式设置扩展名
            elif img.filepath_raw:
                _, temp_ext = os.path.splitext(bpy.path.basename(img.filepath_raw))
                if temp_ext.lower() in {".png", ".jpg", ".jpeg", ".tiff", ".exr", ".hdr"}:
                    ext = temp_ext.lower()

            safe_name = sanitize_filename(img.name)  # 清理文件名
            filename = f"{safe_name}{ext}"
            filepath = os.path.join(export_dir, filename)

            try:
                if img.packed_file:
                    with open(filepath, 'wb') as f:
                        f.write(img.packed_file.data)  # 导出打包的数据
                elif img.filepath_raw and os.path.exists(bpy.path.abspath(img.filepath_raw)):
                    shutil.copy2(bpy.path.abspath(img.filepath_raw), filepath)  # 复制外部文件
                else:
                    img.save_render(filepath)  # 强制渲染保存

                exported_count += 1
                print(f"✅ 导出: {filename}")

            except Exception as e:
                print(f"❌ 导出失败: {img.name} → {e}")
                self.report({'ERROR'}, f"导出失败: {img.name} - {str(e)}")

        self.report({'INFO'}, f"成功导出 {exported_count} 张贴图到:\n{export_dir}")
        return {'FINISHED'}

    def invoke(self, context, event):
        """
        当操作被调用时打开文件浏览器让用户选择导出目录。
        """
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class VIEW3D_PT_export_textures_panel(bpy.types.Panel):
    bl_label = "贴图导出工具"  # 面板标题
    bl_space_type = 'VIEW_3D'  # 在3D视图显示
    bl_region_type = 'UI'  # 在UI区域显示
    bl_category = "My Tools"  # 分类名称

    def draw(self, context):
        layout = self.layout
        layout.operator("export_texture.used_textures", text="导出所有贴图")  # 添加按钮

classes = (
    EXPORT_OT_used_textures,
    VIEW3D_PT_export_textures_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # 注册所有类

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  # 取消注册所有类


if __name__ == "__main__":
    register()