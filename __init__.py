bl_info = {
    "name" : "PiXel",
    "blender" : (3,4,1),
    "version" : (5,3,23),
    "category" : "3D View",
    "author" : "Kent Edoloverio",
    "location" : "3D View > PiXel",
    "description" : "Converts your objects into pixel art",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
}

import bpy

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
        name = "",
        description = "resolution of your pixel art",
        items = [
            ("S1", "16 X 16",""),
            ("S2", "32 X 32", ""),
            ("S3", "64 X 64", ""),
            ("S4", "128 X 128", ""),
            ("S5", "256 X 256", ""),
            ("S6", "CUSTOM", ""),
        ])
    custom_width : StringProperty (
        name = "",
        description = "Custom Width",
        default = "500",
    )
    custom_height : StringProperty (
        name = "",
        description = "Custom Height",
        default = "500",
    )
    check_box_trans : BoolProperty  (
        name = "Transparent Backgroud",
        default = True
    )

class PiXel_op_Resolution(Operator):
    bl_label = "Set Resolution"
    bl_idname = "pixel.op_resolution"

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        scene = context.scene
        custom_res_property = scene.cs_resolution

        if custom_res_property.check_box_trans is True :
            bpy.context.scene.render.film_transparent = True
        elif custom_res_property.check_box_trans is False :
            bpy.context.scene.render.film_transparent = False

        if custom_res_property.pixel_enum == "S1":
            bpy.context.scene.render.resolution_x = 16
            bpy.context.scene.render.resolution_y = 16
        elif custom_res_property.pixel_enum == "S2":
            bpy.context.scene.render.resolution_x = 32
            bpy.context.scene.render.resolution_y = 32
        elif custom_res_property.pixel_enum == "S3":
            bpy.context.scene.render.resolution_x = 64
            bpy.context.scene.render.resolution_y = 64
        elif custom_res_property.pixel_enum == "S4":
            bpy.context.scene.render.resolution_x = 128
            bpy.context.scene.render.resolution_y = 128
        elif custom_res_property.pixel_enum == "S5":
            bpy.context.scene.render.resolution_x = 256
            bpy.context.scene.render.resolution_y = 256
        elif custom_res_property.pixel_enum == "S6":
            bpy.context.scene.render.resolution_x = int(custom_res_property.custom_height)
            bpy.context.scene.render.resolution_y = int(custom_res_property.custom_width)
        return {'FINISHED'}

class PiXel_op_Setup(Operator):
    bl_label = "Setup Project"
    bl_idname = "pixel.op_setup_operator"

    @classmethod
    def poll(cls, context):
        return not False

    def create_group(self,context):
        bpy.context.scene.node_tree.nodes.clear()
        comp = bpy.context.scene.node_tree.nodes.new("CompositorNodeComposite")
        comp.location = (500, 350)

        render_layers =  bpy.context.scene.node_tree.nodes.new("CompositorNodeRLayers")
        render_layers.location = (-100,350)

        # FakeBits NG
        fakebits = bpy.data.node_groups.new("FakeBits", type="CompositorNodeTree")

        # Inputs
        group_inFB = fakebits.nodes.new("NodeGroupInput")
        group_inFB.location = (-700,350)
        fakebits.inputs.new('NodeSocketColor', 'Image')
        fakebits.inputs.new('NodeSocketFloatFactor', 'Color per Channel')

        # Outputs
        group_outFB = fakebits.nodes.new("NodeGroupOutput")
        group_outFB.location = (950, 350)
        fakebits.outputs.new('NodeSocketColor', 'Image')

        gamma_1 = fakebits.nodes.new("CompositorNodeGamma")
        gamma_1.inputs[1].default_value = 0.985
        gamma_1.location = (-400, 350)

        gamma_2 = fakebits.nodes.new("CompositorNodeGamma")
        gamma_2.inputs[1].default_value = 0.985
        gamma_2.location = (750, 350)

        separate_color = fakebits.nodes.new("CompositorNodeSeparateColor")
        separate_color.location = (-200, 350)

        combine_color = fakebits.nodes.new("CompositorNodeCombineColor")
        combine_color.location = (500, 350)

        # CONNECTING NODES FB
        # gamma_1 section
        fakebits.links.new(group_inFB.outputs[0], gamma_1.inputs[0])
        fakebits.links.new(gamma_1.outputs[0], separate_color.inputs[0])

        # combine_color section
        fakebits.links.new(combine_color.outputs[0], gamma_2.inputs[0])

        # gamma_2 section
        fakebits.links.new(gamma_2.outputs[0], group_outFB.inputs[0])

        # separate_color section
        fakebits.links.new(separate_color.outputs[0], comp.inputs[0])

        # Posterize Channel NG
        posterize_channel_1 = bpy.data.node_groups.new("Posterize Channel_1", type="CompositorNodeTree")
        posterize_channel_2 = bpy.data.node_groups.new("Posterize Channel_2", type="CompositorNodeTree")
        posterize_channel_3 = bpy.data.node_groups.new("Posterize Channel_3", type="CompositorNodeTree")
        posterize_channel_4 = bpy.data.node_groups.new("Posterize Channel_4", type="CompositorNodeTree")

        # Inputs
        group_inPC_1 = posterize_channel_1.nodes.new("NodeGroupInput")
        group_inPC_1.location = (-700, 350)
        posterize_channel_1.inputs.new('NodeSocketColor', 'Value')
        posterize_channel_1.inputs.new('NodeSocketFloatFactor', 'Color per Channel')
        group_inPC_2 = posterize_channel_2.nodes.new("NodeGroupInput")
        group_inPC_2.location = (-700, 350)
        posterize_channel_2.inputs.new('NodeSocketColor', 'Value')
        posterize_channel_2.inputs.new('NodeSocketFloatFactor', 'Color per Channel')
        group_inPC_3 = posterize_channel_3.nodes.new("NodeGroupInput")
        group_inPC_3.location = (-700, 350)
        posterize_channel_3.inputs.new('NodeSocketColor', 'Value')
        posterize_channel_3.inputs.new('NodeSocketFloatFactor', 'Color per Channel')
        group_inPC_4 = posterize_channel_4.nodes.new("NodeGroupInput")
        group_inPC_4.location = (-700, 350)
        posterize_channel_4.inputs.new('NodeSocketColor', 'Value')
        posterize_channel_4.inputs.new('NodeSocketFloatFactor', 'Color per Channel')

        # Outputs
        group_outPC_1 = posterize_channel_1.nodes.new("NodeGroupOutput")
        group_outPC_1.location = (300, 350)
        posterize_channel_1.outputs.new ("NodeSocketFloatFactor", "Value")
        group_outPC_2 = posterize_channel_2.nodes.new("NodeGroupOutput")
        group_outPC_2.location = (300, 350)
        posterize_channel_2.outputs.new ("NodeSocketFloatFactor", "Value")
        group_outPC_3 = posterize_channel_3.nodes.new("NodeGroupOutput")
        group_outPC_3.location = (300, 350)
        posterize_channel_3.outputs.new ("NodeSocketFloatFactor", "Value")
        group_outPC_4 = posterize_channel_4.nodes.new("NodeGroupOutput")
        group_outPC_4.location = (300, 350)
        posterize_channel_4.outputs.new ("NodeSocketFloatFactor", "Value")


        multiply_math_1 = posterize_channel_1.nodes.new("CompositorNodeMath")
        multiply_math_1.operation = "MULTIPLY"
        multiply_math_1.location = (-400, 450)
        multiply_math_2 = posterize_channel_2.nodes.new("CompositorNodeMath")
        multiply_math_2.operation = "MULTIPLY"
        multiply_math_2.location = (-400, 450)
        multiply_math_3 = posterize_channel_3.nodes.new("CompositorNodeMath")
        multiply_math_3.operation = "MULTIPLY"
        multiply_math_3.location = (-400, 450)
        multiply_math_4 = posterize_channel_4.nodes.new("CompositorNodeMath")
        multiply_math_4.operation = "MULTIPLY"
        multiply_math_4.location = (-400, 450)

        round_math_1 = posterize_channel_1.nodes.new("CompositorNodeMath")
        round_math_1.operation = "ROUND"
        round_math_1.location = (-200, 450)
        round_math_2 = posterize_channel_2.nodes.new("CompositorNodeMath")
        round_math_2.operation = "ROUND"
        round_math_2.location = (-200, 450)
        round_math_3 = posterize_channel_3.nodes.new("CompositorNodeMath")
        round_math_3.operation = "ROUND"
        round_math_3.location = (-200, 450)
        round_math_4 = posterize_channel_4.nodes.new("CompositorNodeMath")
        round_math_4.operation = "ROUND"
        round_math_4.location = (-200, 450)

        divide_math_1 = posterize_channel_1.nodes.new("CompositorNodeMath")
        divide_math_1.operation = "DIVIDE"
        divide_math_1.location = (100, 400)
        divide_math_2 = posterize_channel_2.nodes.new("CompositorNodeMath")
        divide_math_2.operation = "DIVIDE"
        divide_math_2.location = (100, 400)
        divide_math_3 = posterize_channel_3.nodes.new("CompositorNodeMath")
        divide_math_3.operation = "DIVIDE"
        divide_math_3.location = (100, 400)
        divide_math_4 = posterize_channel_4.nodes.new("CompositorNodeMath")
        divide_math_4.operation = "DIVIDE"
        divide_math_4.location = (100, 400)

        subtract_math_1 = posterize_channel_1.nodes.new("CompositorNodeMath")
        subtract_math_1.operation = "SUBTRACT"
        subtract_math_1.inputs[1].default_value = 1
        subtract_math_1.location = (-400, 250)
        subtract_math_2 = posterize_channel_2.nodes.new("CompositorNodeMath")
        subtract_math_2.operation = "SUBTRACT"
        subtract_math_2.inputs[1].default_value = 1
        subtract_math_2.location = (-400, 250)
        subtract_math_3 = posterize_channel_3.nodes.new("CompositorNodeMath")
        subtract_math_3.inputs[1].default_value = 1
        subtract_math_3.operation = "SUBTRACT"
        subtract_math_3.location = (-400, 250)
        subtract_math_4 = posterize_channel_4.nodes.new("CompositorNodeMath")
        subtract_math_4.inputs[1].default_value = 1
        subtract_math_4.operation = "SUBTRACT"
        subtract_math_4.location = (-400, 250)

        # ADD SECOND NODE GROUP
        fakebits_group_node_1 = fakebits.nodes.new("CompositorNodeGroup")
        fakebits_group_node_1.node_tree = posterize_channel_1
        fakebits_group_node_2 = fakebits.nodes.new("CompositorNodeGroup")
        fakebits_group_node_2.node_tree = posterize_channel_2
        fakebits_group_node_3 = fakebits.nodes.new("CompositorNodeGroup")
        fakebits_group_node_3.node_tree = posterize_channel_3
        fakebits_group_node_4 = fakebits.nodes.new("CompositorNodeGroup")
        fakebits_group_node_4.node_tree = posterize_channel_4


        # CONNECTING NODES PC

        # multiply_math section
        posterize_channel_1.links.new(group_inPC_1.outputs[0], multiply_math_1.inputs[0])
        posterize_channel_1.links.new(subtract_math_1.outputs[0], multiply_math_1.inputs[1])
        posterize_channel_1.links.new(multiply_math_1.outputs[0], round_math_1.inputs[0])
        posterize_channel_2.links.new(group_inPC_2.outputs[0], multiply_math_2.inputs[0])
        posterize_channel_2.links.new(subtract_math_2.outputs[0], multiply_math_2.inputs[1])
        posterize_channel_2.links.new(multiply_math_2.outputs[0], round_math_2.inputs[0])
        posterize_channel_3.links.new(group_inPC_3.outputs[0], multiply_math_3.inputs[0])
        posterize_channel_3.links.new(subtract_math_3.outputs[0], multiply_math_3.inputs[1])
        posterize_channel_3.links.new(multiply_math_3.outputs[0], round_math_3.inputs[0])
        posterize_channel_4.links.new(group_inPC_4.outputs[0], multiply_math_4.inputs[0])
        posterize_channel_4.links.new(subtract_math_4.outputs[0], multiply_math_4.inputs[1])
        posterize_channel_4.links.new(multiply_math_4.outputs[0], round_math_4.inputs[0])

        # round_math section
        posterize_channel_1.links.new(round_math_1.outputs[0], divide_math_1.inputs[0])
        posterize_channel_2.links.new(round_math_2.outputs[0], divide_math_2.inputs[0])
        posterize_channel_3.links.new(round_math_3.outputs[0], divide_math_3.inputs[0])
        posterize_channel_4.links.new(round_math_4.outputs[0], divide_math_4.inputs[0])

        # subtract_math section
        posterize_channel_1.links.new(group_inPC_1.outputs[1], subtract_math_1.inputs[0])
        posterize_channel_1.links.new(subtract_math_1.outputs[0], divide_math_1.inputs[1])
        posterize_channel_2.links.new(group_inPC_2.outputs[1], subtract_math_2.inputs[0])
        posterize_channel_2.links.new(subtract_math_2.outputs[0], divide_math_2.inputs[1])
        posterize_channel_3.links.new(group_inPC_3.outputs[1], subtract_math_3.inputs[0])
        posterize_channel_3.links.new(subtract_math_3.outputs[0], divide_math_3.inputs[1])
        posterize_channel_4.links.new(group_inPC_4.outputs[1], subtract_math_4.inputs[0])
        posterize_channel_4.links.new(subtract_math_4.outputs[0], divide_math_4.inputs[1])

        # divide_math section
        posterize_channel_1.links.new(divide_math_1.outputs[0], group_outPC_1.inputs[0])
        posterize_channel_2.links.new(divide_math_2.outputs[0], group_outPC_2.inputs[0])
        posterize_channel_3.links.new(divide_math_3.outputs[0], group_outPC_3.inputs[0])
        posterize_channel_4.links.new(divide_math_4.outputs[0], group_outPC_4.inputs[0])

        fakebits.links.new(separate_color.outputs[0], fakebits_group_node_1.inputs[0])
        fakebits.links.new(separate_color.outputs[1], fakebits_group_node_2.inputs[0])
        fakebits.links.new(separate_color.outputs[2], fakebits_group_node_3.inputs[0])
        fakebits.links.new(separate_color.outputs[3], fakebits_group_node_4.inputs[0])

        fakebits.links.new(group_inFB.outputs[1], fakebits_group_node_1.inputs[1])
        fakebits.links.new(group_inFB.outputs[1], fakebits_group_node_2.inputs[1])
        fakebits.links.new(group_inFB.outputs[1], fakebits_group_node_3.inputs[1])
        fakebits.links.new(group_inFB.outputs[1], fakebits_group_node_4.inputs[1])

        fakebits.links.new(fakebits_group_node_1.outputs[0], combine_color.inputs[0])
        fakebits.links.new(fakebits_group_node_2.outputs[0], combine_color.inputs[1])
        fakebits.links.new(fakebits_group_node_3.outputs[0], combine_color.inputs[2])
        fakebits.links.new(fakebits_group_node_4.outputs[0], combine_color.inputs[3])



        # Add the node group to the compositor
        FB_group_node = bpy.context.scene.node_tree.nodes.new("CompositorNodeGroup")
        FB_group_node.node_tree = fakebits
        FB_group_node.inputs[1].default_value = 32
        FB_group_node.location = (200,350)

        bpy.context.scene.node_tree.links.new(FB_group_node.outputs[0], comp.inputs[0])
        bpy.context.scene.node_tree.links.new(render_layers.outputs[0], FB_group_node.inputs[0])

        return {'FINISHED'}

    def execute(self, context):
        bpy.context.scene.use_nodes = True
        bpy.context.scene.render.filter_size = 0
        bpy.context.scene.frame_end = 1
        bpy.context.scene.render.image_settings.compression = 0
        bpy.context.scene.view_settings.view_transform = 'Standard'
        bpy.context.scene.render.use_freestyle = True
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        bpy.context.scene.eevee.use_soft_shadows = False
        bpy.context.scene.render.dither_intensity = 0
        bpy.context.scene.eevee.taa_render_samples = 20
        bpy.context.scene.eevee.taa_samples = 20

        self.create_group(context)
        return {'FINISHED'}

class PiXel_pl_Base:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'HEADER_LAYOUT_EXPAND'}
    bl_category = "PiXel"
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'BLENDER_EEVEE'


class PiXel_pl_Setup(PiXel_pl_Base,Panel):
    bl_idname = "PiXel_pl_Setup"
    bl_label = "PiXel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS' if bpy.app.version < (2, 80) else 'UI'
    bl_context = ''
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not False

    def draw(self, context):
        layout = self.layout

        col = layout.row(align=False)
        col.enabled = True
        col.scale_x = 1.7
        col.scale_y = 1.7
        col.operator("pixel.op_setup_operator")

        addon_updater_ops.check_for_update_background()
        if addon_updater_ops.updater.update_ready:
            layout.label(text="PiXel Successfuly Update", icon="INFO")

        # Call built-in function with draw code/checks.
        addon_updater_ops.update_notice_box_ui(self, context)


class PiXel_pl_Resolution(PiXel_pl_Base,Panel):
    bl_parent_id = "PiXel_pl_Setup"
    bl_label = "Resolution"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not False

    def draw(self, context):
        layout = self.layout
        mytool = context.scene.cs_resolution

        col = layout.row(align=False)
        col.enabled = True
        col.scale_x = 1.3
        col.scale_y = 1.3
        col.label(text=r"Resolution Size :")

        col = layout.row(align=False)
        col.enabled = True
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
        col.enabled = True
        col.scale_x = 1.5
        col.scale_y = 1.5
        col.operator("pixel.op_resolution")


class PiXel_pl_Outline(PiXel_pl_Base,Panel):
    bl_parent_id = "PiXel_pl_Setup"
    bl_label = "Outline"
    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'
    bl_options = {'HEADER_LAYOUT_EXPAND', 'DEFAULT_CLOSED'}
    bl_ui_units_x=0
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout

class PiXel_pl_Outline_MP(PiXel_pl_Base,Panel):
    bl_parent_id = "PiXel_pl_Outline"
    bl_label = "Materials Properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def draw_header(self, context):
        layout = self.layout

    def draw(self,context):
        layout = self.layout
        obj = bpy.context.view_layer.objects.active
        if not obj.data.materials:
            layout.label(text="Add New Material", icon="ERROR")
        else:
            layout.prop(bpy.data.materials[bpy.context.object.data.materials[0].name], 'line_color', text="Line Color", icon_value=0, emboss=True)
            layout.prop(bpy.data.materials[bpy.context.object.data.materials[0].name], 'line_priority', text="Priority", icon_value=0, emboss=True)
        return {'FINISHED'}


class PiXel_pl_Outline_VLP(PiXel_pl_Base,Panel):
    bl_parent_id = "PiXel_pl_Outline"
    bl_label = "View Layer Properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not ('EDIT_MESH'==bpy.context.mode)

    def draw_header(self, context):
        layout = self.layout

    def draw(self,context):
        obj = bpy.context.object
        layout = self.layout
        my_tool = context.scene.cs_resolution

        if bpy.context.scene.render.use_freestyle is False:
            layout.label(text="Please Enable Freestyle", icon="ERROR")
        else:
            layout.prop(bpy.data.linestyles[bpy.data.linestyles[0].name], 'color', text='Line Color', icon_value=0, emboss=True)
            layout.prop(bpy.data.linestyles[bpy.data.linestyles[0].name], 'thickness', text='Line Thickness', icon_value=0, emboss=True)
            layout.label(text='Edge Type ', icon_value=0)
            layout.prop(bpy.context.view_layer.freestyle_settings.linesets.active, 'select_silhouette', text='Silhouette', icon_value=0, emboss=True)
            layout.prop(bpy.context.view_layer.freestyle_settings.linesets.active, 'select_crease', text='Crease', icon_value=0, emboss=True)
            layout.prop(bpy.context.view_layer.freestyle_settings.linesets.active, 'select_border', text='Border', icon_value=0, emboss=True)
            layout.prop(bpy.context.view_layer.freestyle_settings.linesets.active, 'select_edge_mark', text='Edge Mark', icon_value=0, emboss=True)
            layout.prop(bpy.context.view_layer.freestyle_settings.linesets.active, 'select_contour', text='Contour', icon_value=0, emboss=True)
            layout.prop(bpy.context.view_layer.freestyle_settings.linesets.active, 'select_external_contour', text='External Contour', icon_value=0, emboss=True)
            layout.prop(bpy.context.view_layer.freestyle_settings.linesets.active, 'select_material_boundary', text='Material Boundary', icon_value=0, emboss=True)
            layout.prop(bpy.context.view_layer.freestyle_settings.linesets.active, 'select_suggestive_contour', text='Suggestive Contour', icon_value=0, emboss=True)
            layout.prop(bpy.context.view_layer.freestyle_settings.linesets.active, 'select_ridge_valley', text='Ridge & Valley', icon_value=0, emboss=True)
        return {'FINISHED'}

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
    PiXel_pl_Outline_MP,
    PiXel_pl_Outline_VLP,
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
