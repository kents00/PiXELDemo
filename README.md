![tumblr_static_tumblr_static_2i5cn6zq5qw4c8ocss0csokkc_focused_v3](https://user-images.githubusercontent.com/69900896/213923000-28298efc-0289-4b0c-9c10-d053cc869bdd.gif)

# PiXEL

“Converts your meshes into pixel art”

## Introduction

Converting 3D meshes into pixel art is a popular technique that allows artists to create retro-style graphics with a modern 3D modeling tool. The process involves taking a 3D model and reducing the resolution adding pixelate node and so on to create a low-resolution, pixelated look. The results can then be used in a variety of applications, such as video games, animations, or digital art.

## Short Terms

**pl** - Panel

**op** - Operator

**pg** - Property Group

## Documentation

**Setup Project -** Setup the main functionalities creating pixel art, Imports custom node group inside the compositor tab.

**Sub** **Panels**

- **Resolution -** Sets resolution of your camera, you can also *disable/transparent* the background of your environment based on your needs.
- **Outline** - Sets outline / ‘*freestyle’* to your meshes like style of the lines using various settings, such as line thickness, color, and visibility criteria.
    - **Materials Properties -** It will assigned a custom outline color into different materials
    - **Main Outline -** Main Freestyle settings

## Tips

- Declaring a custom scene you must register it and assign it into `PointerProperty`

```python
bpy.types.Scene.<'custom_name'> = bpy.props.PointerProperty(type= <'assign class'>)
```

- You can only use **One `Property Group`**
- You can direct using the inbuilt functions example `PiXel_pl_Outline`

```python
layout.prop( <' built-in functions example: bpy.context.view_layer.freestyle_settings.linesets.active '>,<' freestyle section name example: select_silhouette '>, text=<'custom_name'>, icon_value=0, emboss=True)
```

   **Note:** This is not organize and `not reusable`


- Copy the unknown function just simply *right click* and `copy the full data path`.


    ![Screenshot_(910)](https://user-images.githubusercontent.com/69900896/214347044-60c2eb16-c434-4370-b64e-79d740919f3f.png)



## Bugs / Problems

- You cannot register two or more `Property Group` and declare a custom scene at the same time as a result it returns an **error message**
-

## Task

- [x]  Add Sub Panels

![Untitled](https://user-images.githubusercontent.com/69900896/214346954-f0d6928d-b9f0-4583-8eda-621a342a17a7.png)

- [x]  Adding color picker in Outline

![Screenshot_(906)](https://user-images.githubusercontent.com/69900896/214346926-edaa6cdd-1bbc-440f-9cff-4a07a52d7354.png)

- [x]  Add / import the custom node group in compositing tab and connect the nodes

![Untitled 1](https://user-images.githubusercontent.com/69900896/214346835-3ed2b37c-1cc3-42c3-b7c2-cd7a74a21f26.png)

- [x]  Create a decorators to your classes

    [Decorators and Polling - Have I Got This Right?](https://blenderartists.org/t/decorators-and-polling-have-i-got-this-right/565611/2)

- [ ]  Refactor outline section; there are two different `Freestyle Lines`
    - **Materials Properties**
        - Each material you can assign the outlines
    - **View Layer Properties**
        - Main freestyle line


## Road Map

### **Phase 01**

   The creation of the project where I can build without a proper structure to find the best tools and setup what is suitable

### **Phase 02**

   Refactor all the code and make it reusable for the future

### **Phase 03**

   Launch of the addon and making promotional videos/images to attract customers

 ## Update

The default version in this addon is `3.4` but in some customers they want to stay on that specific versions of blender, instead of migrating them to the new versions, I will make a versions of my code that can execute in the same latest versions.

**Note:** This is not a top priority, since certain previous blender versions did not support newer functions; instead, we will make minor changes to support older versions.

**Structure**

![Blank_diagram](https://user-images.githubusercontent.com/69900896/216997048-f29cc6e0-d6fb-4080-a582-e609c40d5ac2.svg)

### References

[https://github.com/int-ua/blender-pixelart](https://github.com/int-ua/blender-pixelart)

[Make Pixel Art EASY w/ Blender 3D](https://youtu.be/X-22q-VdPfs)

[How to Make Animated PIXEL ART Characters Sprites with Blender 2.9 | Quick and Easy TUTORIAL](https://youtu.be/eSqb6II3WMM)
