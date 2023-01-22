![tumblr_static_tumblr_static_2i5cn6zq5qw4c8ocss0csokkc_focused_v3](https://user-images.githubusercontent.com/69900896/213923000-28298efc-0289-4b0c-9c10-d053cc869bdd.gif)

# PiXEL

“Converts your meshes into pixel art”

### Introduction

Converting 3D meshes created in Blender into pixel art is a popular technique that allows artists to create retro-style graphics with a modern 3D modeling tool. The process involves taking a 3D model and reducing the polygons to create a low-resolution, pixelated look. The results can then be used in a variety of applications, such as video games, animations, or digital art.

### Documentation

**Setup Project -** Setup the main functionalities making a pixel art.

```python
class PiXel_op_Setup(Operator):
    bl_label = "Setup Project"
    bl_idname = "pixel.setup_operator"

    def execute(self, context):
        bpy.context.scene.use_nodes = True
        bpy.context.scene.render.filter_size = 0
        bpy.context.scene.frame_end = 1
        bpy.context.scene.render.image_settings.compression = 0
        bpy.context.scene.view_settings.view_transform = 'Standard'
        bpy.context.scene.view_layers["ViewLayer"].use_freestyle = True
        bpy.context.scene.eevee.taa_render_samples = 1
        bpy.context.scene.eevee.taa_samples = 1
        return {"FINISHED"}
```

**Sub** **Panels**

- **Resolution -** Sets resolution of your camera, you can also *disable/transparent* the background of your environment based on your needs.

```python
class PiXel_pg_Resolution(PropertyGroup):
    pixel_enum: EnumProperty(
        name = "Resolution",
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
        default = "128",
    )

    custom_height : StringProperty (
        name = "",
        description = "Custom Height",
        default = "128",
    )

    check_box_trans : BoolProperty  (
        name = "Transparent Backgroud",
        default = True
    )

class PiXel_op_Resolution(Operator):
    bl_label = "Set Resolution"
    bl_idname = "pixel.op_resolution"

    def execute(self, context):
        scene = context.scene
        custom_res_property = scene.cs_resolution

        if custom_res_property.check_box_trans == True :
            bpy.context.scene.render.film_transparent = True
        elif custom_res_property.check_box_trans == False :
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
        return {"FINISHED"}
```

- **Outline** - Sets outline / ‘*freestyle’* of your meshes **you cannot disable it

```python
class PiXel_pl_Outline(PiXel_pl_Base,Panel):
    bl_parent_id = "PiXel_pl_Setup"
    bl_label = "Outline"

    def draw(self, context):
        layout = self.layout
        layout.label(text='Outline Thickness', icon_value=0)
        layout.prop(bpy.data.linestyles['LineStyle'], 'thickness', text='', icon_value=0, emboss=True)
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
```

### Tips

- Declaring a custom scene you must register it and assign it into `PointerProperty`

```python
bpy.types.Scene.<'custom_name'> = bpy.props.PointerProperty(type= <'assign class'>)
```

- You can only use **One `Property Group`**

### Bugs / Problems

- You cannot register two or more `Property Group` and declare a custom scene at the same time as a result compiler will confused which one first will register

### Task

- [x]  Add Sub Panels

![Untitled](https://user-images.githubusercontent.com/69900896/213922987-2d1e2f8a-e81a-4f3e-b820-c28ea751bc39.png)


- [ ]  Add / import the custom node group in compositing tab and connect the nodes

![Untitled 1](https://user-images.githubusercontent.com/69900896/213922988-7597c6a2-9d5e-4cb9-913a-be15e96988b7.png)


### References

[https://github.com/int-ua/blender-pixelart](https://github.com/int-ua/blender-pixelart)

[Make Pixel Art EASY w/ Blender 3D](https://youtu.be/X-22q-VdPfs)
