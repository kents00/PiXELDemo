bl_info = {
    "name" : "PiXel",
    "blender" : (4,1,1),
    "version" : (2,0,0),
    "category" : "3D View",
    "author" : "Kent Edoloverio",
    "location" : "3D View > PiXel",
    "description" : "Converts your objects into pixel art",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
}

import bpy
import os
from . import addon_updater_ops
from bpy.props import (
        StringProperty,
        EnumProperty,
        BoolProperty
)
from bpy.types import (
        PropertyGroup,
        Panel,
        Operator,
        AddonPreferences,
)

class PiXel_pg_Resolution(PropertyGroup):
    pixel_enum: EnumProperty(
        name="",
        description="Resolution of your pixel art",
        items=[
            ("S1", "16 X 16", ""),
            ("S2", "32 X 32", ""),
            ("S3", "64 X 64", ""),
            ("S4", "128 X 128", ""),
            ("S5", "256 X 256", ""),
            ("S6", "CUSTOM", ""),
        ],
    )
    custom_width: StringProperty(
        name="",
        description="Custom Width",
        default="500",
    )
    custom_height: StringProperty(
        name="",
        description="Custom Height",
        default="500",
    )
    check_box_trans: BoolProperty(
        name="Transparent Background",
        default=True,
    )

class PiXel_op_Resolution(Operator):
    bl_label = "Set Resolution"
    bl_idname = "pixel.op_resolution"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        custom_res_property = scene.cs_resolution

        bpy.context.scene.render.film_transparent = custom_res_property.check_box_trans

        resolutions = {
            "S1": (16, 16),
            "S2": (32, 32),
            "S3": (64, 64),
            "S4": (128, 128),
            "S5": (256, 256),
            "S6": (int(custom_res_property.custom_width), int(custom_res_property.custom_height)),
        }

        res_x, res_y = resolutions.get(custom_res_property.pixel_enum, (16, 16))
        bpy.context.scene.render.resolution_x = res_x
        bpy.context.scene.render.resolution_y = res_y

        return {'FINISHED'}

class PiXel_op_Setup(Operator):
    bl_label = "Setup Project"
    bl_idname = "pixel.op_setup_operator"

    @classmethod
    def poll(cls, context):
        return True

    def __init__(self):
        self.source_file = os.path.join(os.path.dirname(__file__), "..", "PiXEL/data", "PiXEL.blend")

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
    bl_category = "PiXEL"
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'BLENDER_EEVEE'
class PiXel_pl_Setup(PiXel_pl_Base, Panel):
    bl_idname = "PiXel_pl_Setup"
    bl_label = "PiXel"

    def draw(self, context):
        layout = self.layout

        col = layout.row(align=False)
        col.scale_x = 1.7
        col.scale_y = 1.7
        col.operator("pixel.op_setup_operator")

        addon_updater_ops.check_for_update_background()
        if addon_updater_ops.updater.update_ready:
            layout.label(text="PiXel Successfully Updated", icon="INFO")

        addon_updater_ops.update_notice_box_ui(self, context)
class PiXel_pl_Resolution(PiXel_pl_Base, Panel):
    bl_parent_id = "PiXel_pl_Setup"
    bl_label = "Resolution"

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, 'cs_resolution')

    def draw(self, context):
        layout = self.layout
        mytool = context.scene.cs_resolution

        col = layout.row(align=False)
        col.scale_x = 1.3
        col.scale_y = 1.3
        col.label(text="Resolution Size:")

        col = layout.row(align=False)
        col.scale_x = 1.5
        col.scale_y = 1.5
        col.prop(mytool, "pixel_enum")

        if mytool.pixel_enum == "S6":
            box = layout.box()
            row = box.row(align=True)
            row.label(text="Width:")
            row.prop(mytool, "custom_height")
            row.label(text="px")

            row = box.row(align=True)
            row.label(text="Height:")
            row.prop(mytool, "custom_width")
            row.label(text="px")

        layout.prop(mytool, "check_box_trans")

        col = layout.row(align=False)
        col.scale_x = 1.5
        col.scale_y = 1.5
        col.operator("pixel.op_resolution")

class PiXel_pl_Outline(PiXel_pl_Base, Panel):
    bl_parent_id = "PiXel_pl_Setup"
    bl_label = "Outline"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if obj and obj.type == 'MESH':
            has_emission = False
            has_solidify = False

            for mat in obj.data.materials:
                if mat and mat.name == "Emission" and mat.use_nodes:
                    nodes = mat.node_tree.nodes
                    if "Emission" in nodes:
                        layout.prop(nodes["Emission"].inputs[0], "default_value", text="Color")
                        has_emission = True
                        break

            solidify_mod = obj.modifiers.get("Solidify")
            if solidify_mod:
                layout.prop(solidify_mod, "thickness")
                layout.prop(solidify_mod, "offset")
                layout.prop(solidify_mod, "use_even_offset")
                layout.prop(solidify_mod, "use_rim")
                layout.prop(solidify_mod, "use_flip_normals")
                layout.prop(solidify_mod, "use_quality_normals")
                layout.prop(solidify_mod, "material_offset")
                has_solidify = True

            if not has_emission or not has_solidify:
                layout.label(text="Please setup the project", icon='INFO')
        else:
            self.report({'WARNING'}, "Please select a mesh object")

@addon_updater_ops.make_annotations
class PiXel_pdtr_Preferences(AddonPreferences):
	bl_idname = __package__

	# Addon updater preferences.

	auto_check_update = bpy.props.BoolProperty(
		name="Auto-check for Update",
		description="If enabled, auto-check for updates using an interval",
		default=False)

	updater_interval_months = bpy.props.IntProperty(
		name='Months',
		description="Number of months between checking for updates",
		default=0,
		min=0)

	updater_interval_days = bpy.props.IntProperty(
		name='Days',
		description="Number of days between checking for updates",
		default=7,
		min=0,
		max=31)

	updater_interval_hours = bpy.props.IntProperty(
		name='Hours',
		description="Number of hours between checking for updates",
		default=0,
		min=0,
		max=23)

	updater_interval_minutes = bpy.props.IntProperty(
		name='Minutes',
		description="Number of minutes between checking for updates",
		default=0,
		min=0,
		max=59)

	def draw(self, context):
		layout = self.layout

		mainrow = layout.row()
		col = mainrow.column()

		addon_updater_ops.update_settings_ui(self, context)

classes = (
    PiXel_pg_Resolution,
    PiXel_pl_Setup,
    PiXel_pl_Resolution,
    PiXel_pl_Outline,
    PiXel_op_Setup,
    PiXel_op_Resolution,
    PiXel_pdtr_Preferences,
)

def register():
    addon_updater_ops.register(bl_info)

    for cls in classes:
        bpy.utils.register_class(cls)
        bpy.types.Scene.cs_resolution = bpy.props.PointerProperty(type= PiXel_pg_Resolution)

def unregister():
    addon_updater_ops.unregister()

    for cls in classes:
        bpy.utils.unregister_class(cls)
        del bpy.types.Scene.cs_resolution

if __name__ == "__main__":
    register()