bl_info = {
    "name" : "PiXEL Demo",
    "blender" : (4,1,1),
    "version" : (2,0,0),
    "category" : "3D View",
    "author" : "Kent Edoloverio",
    "location" : "3D View > PiXEL Demo",
    "description" : "Converts your objects into pixel art",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
}

import bpy
import os
from bpy.types import Panel,Operator
class PiXel_op_Setup(Operator):
    bl_label = "Setup Project"
    bl_idname = "pixel.op_setup_operator"

    @classmethod
    def poll(cls, context):
        return True

    def __init__(self):
        self.source_file = os.path.join(os.path.dirname(__file__), "..", "PiXELDemo/data", "PiXELDemo.blend")

    def import_file(self):
        if not os.path.isfile(self.source_file):
            self.report({'ERROR'}, f"File not found: {self.source_file}")
            return {'CANCELLED'}
        return {'FINISHED'}

    def import_node_group(self, node_group_name):
        with bpy.data.libraries.load(self.source_file, link=False) as (data_from, data_to):
            if node_group_name in data_from.node_groups:
                data_to.node_groups = [node_group_name]

        if not data_to.node_groups or not data_to.node_groups[0]:
            self.report({'ERROR'}, f"Failed to load the node group: {node_group_name}")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Successfully appended node group: {node_group_name}")
        return {'FINISHED'}

    def render_settings(self):
        bpy.context.scene.eevee.taa_render_samples = 64
        bpy.context.scene.eevee.taa_samples = 1
        bpy.context.scene.render.filter_size = 0.01
        bpy.context.scene.render.film_transparent = True
        bpy.context.scene.view_settings.view_transform = 'Standard'

    def scene_output(self):
        bpy.context.scene.render.image_settings.color_mode = 'RGB'
        bpy.context.scene.render.image_settings.compression = 0

    def solidify_modifier(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            solidify_modifier = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
            solidify_modifier.thickness = 0.01
            solidify_modifier.use_even_offset = True
            solidify_modifier.use_flip_normals = True
            solidify_modifier.use_quality_normals = True
            solidify_modifier.material_offset = 1
            self.report({'INFO'}, "Solidify Modifier Added")
        else:
            self.report({'WARNING'}, "No mesh object selected")

    def create_emission_shader(self):
        if "Emission" in bpy.data.materials:
            mat = bpy.data.materials["Emission"]
        else:
            mat = bpy.data.materials.new(name="Emission")
            mat.use_nodes = True

            nodes = mat.node_tree.nodes
            links = mat.node_tree.links

            for node in nodes:
                nodes.remove(node)

            emission_node = nodes.new(type='ShaderNodeEmission')
            emission_node.location = (0, 0)
            emission_node.inputs[0].default_value = (0, 0, 0, 1)

            output_node = nodes.new(type='ShaderNodeOutputMaterial')
            output_node.location = (200, 0)

            links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])

        mat.use_backface_culling = True
        self.report({'INFO'}, "Emission Shader Applied")
        return mat

    def import_material(self, material_name):
        with bpy.data.libraries.load(self.source_file, link=False) as (data_from, data_to):
            if material_name in data_from.materials:
                data_to.materials = [material_name]

        if not data_to.materials or not data_to.materials[0]:
            self.report({'ERROR'}, f"Failed to load the material: {material_name}")
            return None

        self.report({'INFO'}, f"Successfully appended material: {material_name}")
        return bpy.data.materials.get(material_name)

    def setup_camera(self):
        cam = bpy.context.scene.camera
        if not cam:
            # Create a new camera
            bpy.ops.object.camera_add()
            cam = bpy.context.object
            bpy.context.scene.camera = cam
        cam.data.type = 'ORTHO'
        self.report({'INFO'}, "Camera set to orthographic")

    def execute(self, context):
        self.render_settings()
        self.scene_output()
        self.solidify_modifier(context)
        self.setup_camera()

        if self.import_file() == {'CANCELLED'}:
            return {'CANCELLED'}

        material = self.import_material("PiXEL Shader")
        if material is None:
            return {'CANCELLED'}

        for obj in context.selected_objects:
            if obj.type == 'MESH':
                obj.data.materials.clear()
                obj.data.materials.append(material)

                emission_mat = self.create_emission_shader()
                obj.data.materials.append(emission_mat)

        return {'FINISHED'}
class PiXel_pl_Base:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'HEADER_LAYOUT_EXPAND'}
    bl_category = "PiXEL Demo"
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'BLENDER_EEVEE'
class PiXel_pl_Setup(PiXel_pl_Base, Panel):
    bl_idname = "PiXel_pl_Setup"
    bl_label = "PiXEL Demo"

    def draw(self, context):
        pcoll = icon_preview["main"]
        gumroad = pcoll["gumroad"]
        layout = self.layout
        

        col = layout.row(align=False)
        col.scale_x = 1.7
        col.scale_y = 1.7
        col.operator("pixel.op_setup_operator")

        box = layout.box()
        box.scale_y = 1.5
        box.scale_x = 1.5
        gumroad = box.operator(
            'wm.url_open',
            text='BUY PIXEL PRO',
            icon_value=gumroad.icon_id,
            emboss=False
        )
        gumroad.url = 'https://kentedoloverio.gumroad.com/l/PiXEL'

icon_preview = {}

classes = (
    PiXel_pl_Setup,
    PiXel_op_Setup,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    pcoll = bpy.utils.previews.new()

    absolute_path = os.path.join(os.path.dirname(__file__), 'data/')
    relative_path = "icons"
    path = os.path.join(absolute_path, relative_path)
    pcoll.load("gumroad", os.path.join(path, "gumroad.png"), 'IMAGE')
    icon_preview["main"] = pcoll

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()