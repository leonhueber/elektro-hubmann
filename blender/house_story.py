"""Build and animate the Elektro Hubmann architectural scroll-story house.

The scene is intentionally procedural so the source asset stays reproducible.
Run with Blender 5.2+:
    blender --background --python blender/house_story.py -- --render-still
    blender --background --python blender/house_story.py -- --render-animation
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
BLEND_PATH = ROOT / "assets" / "3d" / "elektro-hubmann-house.blend"
QA_DIR = ROOT / "docs" / "version-g-qa" / "blender"
SEQUENCE_DIR = ROOT / "public" / "images" / "version-g" / "sequence"

FRAME_START = 1
FRAME_END = 120
RENDER_WIDTH = int(os.environ.get("HUBMANN_RENDER_WIDTH", "1600"))
RENDER_HEIGHT = int(os.environ.get("HUBMANN_RENDER_HEIGHT", "900"))


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def material(
    name: str,
    color: tuple[float, float, float, float],
    *,
    roughness: float = 0.55,
    metallic: float = 0.0,
    transmission: float = 0.0,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Metallic"].default_value = metallic
    if "Transmission Weight" in principled.inputs:
        principled.inputs["Transmission Weight"].default_value = transmission
    if emission is not None:
        principled.inputs["Emission Color"].default_value = emission
        principled.inputs["Emission Strength"].default_value = emission_strength
    return mat


def concrete_material() -> bpy.types.Material:
    mat = material("Concrete", (0.58, 0.59, 0.58, 1), roughness=0.72)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    principled = nodes.get("Principled BSDF")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 7.0
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Roughness"].default_value = 0.72
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.16
    bump.inputs["Distance"].default_value = 0.08
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    return mat


def wood_material() -> bpy.types.Material:
    mat = material("Natural oak", (0.48, 0.23, 0.08, 1), roughness=0.48)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    principled = nodes.get("Principled BSDF")
    tex = nodes.new("ShaderNodeTexNoise")
    tex.noise_dimensions = "3D"
    tex.inputs["Scale"].default_value = 4.0
    tex.inputs["Detail"].default_value = 6.0
    tex.inputs["Roughness"].default_value = 0.68
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.12, 0.035, 0.008, 1)
    ramp.color_ramp.elements[1].color = (0.62, 0.29, 0.07, 1)
    links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], principled.inputs["Base Color"])
    return mat


def apply_material(obj: bpy.types.Object, mat: bpy.types.Material) -> None:
    obj.data.materials.append(mat)


def add_box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    mat: bpy.types.Material,
    *,
    rotation: tuple[float, float, float] = (0, 0, 0),
    bevel: float = 0.04,
    parent: bpy.types.Object | None = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        modifier = obj.modifiers.new("Soft construction edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
    apply_material(obj, mat)
    if parent:
        obj.parent = parent
    return obj


def add_cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    mat: bpy.types.Material,
    *,
    rotation: tuple[float, float, float] = (0, 0, 0),
    vertices: int = 32,
    parent: bpy.types.Object | None = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    apply_material(obj, mat)
    if parent:
        obj.parent = parent
    return obj


def add_curve(
    name: str,
    points: list[tuple[float, float, float]],
    mat: bpy.types.Material,
    *,
    bevel_depth: float = 0.025,
    parent: bpy.types.Object | None = None,
    smooth: bool = True,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 12
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 5
    if smooth:
        spline = curve.splines.new("BEZIER")
        spline.bezier_points.add(len(points) - 1)
        for point, coordinate in zip(spline.bezier_points, points):
            point.co = coordinate
            point.handle_left_type = "AUTO"
            point.handle_right_type = "AUTO"
    else:
        spline = curve.splines.new("POLY")
        spline.points.add(len(points) - 1)
        for point, coordinate in zip(spline.points, points):
            point.co = (*coordinate, 1.0)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    apply_material(obj, mat)
    if parent:
        obj.parent = parent
    return obj


def add_gable(
    name: str,
    y: float,
    mat: bpy.types.Material,
    *,
    parent: bpy.types.Object | None = None,
) -> bpy.types.Object:
    """Create a solid triangular gable that follows the roof profile."""
    half_width = 4.74
    base_z = 5.80
    ridge_z = 8.35
    thickness = 0.24
    y_front = y - thickness / 2
    y_back = y + thickness / 2
    vertices = [
        (-half_width, y_front, base_z),
        (half_width, y_front, base_z),
        (0, y_front, ridge_z),
        (-half_width, y_back, base_z),
        (half_width, y_back, base_z),
        (0, y_back, ridge_z),
    ]
    faces = [
        (0, 1, 2),
        (5, 4, 3),
        (0, 3, 4, 1),
        (1, 4, 5, 2),
        (2, 5, 3, 0),
    ]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    apply_material(obj, mat)
    bevel = obj.modifiers.new("Gable edge finish", "BEVEL")
    bevel.width = 0.025
    bevel.segments = 2
    if parent:
        obj.parent = parent
    return obj


def empty(name: str) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    return obj


def keyframe_transform(
    obj: bpy.types.Object,
    frame: int,
    *,
    location: tuple[float, float, float] | None = None,
    scale: tuple[float, float, float] | None = None,
    rotation: tuple[float, float, float] | None = None,
) -> None:
    if location is not None:
        obj.location = location
        obj.keyframe_insert(data_path="location", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert(data_path="scale", frame=frame)
    if rotation is not None:
        obj.rotation_euler = rotation
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)


def add_front_window(
    name: str,
    x: float,
    z: float,
    width: float,
    height: float,
    glass: bpy.types.Material,
    frame: bpy.types.Material,
    parent: bpy.types.Object,
) -> None:
    y = -4.06
    add_box(f"{name} glass", (x, y, z), (width, 0.08, height), glass, bevel=0.015, parent=parent)
    bar = 0.11
    for x_pos in (x - width / 2, x + width / 2):
        add_box(f"{name} frame", (x_pos, y - 0.055, z), (bar, 0.13, height + bar), frame, bevel=0.015, parent=parent)
    for z_pos in (z - height / 2, z + height / 2):
        add_box(f"{name} frame", (x, y - 0.055, z_pos), (width + bar, 0.13, bar), frame, bevel=0.015, parent=parent)
    if width > 1.6:
        add_box(f"{name} mullion", (x, y - 0.06, z), (bar, 0.13, height), frame, bevel=0.012, parent=parent)


def add_side_window(
    name: str,
    y: float,
    z: float,
    width: float,
    height: float,
    glass: bpy.types.Material,
    frame: bpy.types.Material,
    parent: bpy.types.Object,
) -> None:
    x = 5.06
    add_box(f"{name} glass", (x, y, z), (0.08, width, height), glass, bevel=0.015, parent=parent)
    bar = 0.11
    for y_pos in (y - width / 2, y + width / 2):
        add_box(f"{name} frame", (x + 0.055, y_pos, z), (0.13, bar, height + bar), frame, bevel=0.015, parent=parent)
    for z_pos in (z - height / 2, z + height / 2):
        add_box(f"{name} frame", (x + 0.055, y, z_pos), (0.13, width + bar, bar), frame, bevel=0.015, parent=parent)


def build_scene() -> None:
    clear_scene()

    white = material("Warm white plaster", (0.89, 0.88, 0.84, 1), roughness=0.58)
    interior_white = material("Interior white", (0.96, 0.95, 0.91, 1), roughness=0.62)
    concrete = concrete_material()
    wood = wood_material()
    dark = material("Charcoal metal", (0.018, 0.022, 0.025, 1), roughness=0.28, metallic=0.72)
    roof_mat = material("Anthracite roof", (0.025, 0.03, 0.035, 1), roughness=0.42, metallic=0.38)
    glass = material("Architectural glass", (0.055, 0.11, 0.14, 1), roughness=0.08, metallic=0.08, transmission=0.46)
    red = material("Hubmann red", (0.78, 0.002, 0.008, 1), roughness=0.35)
    pv = material("Photovoltaic cells", (0.008, 0.055, 0.075, 1), roughness=0.18, metallic=0.62)
    floor_mat = material("Oak floor", (0.34, 0.15, 0.055, 1), roughness=0.52)
    warm_light = material(
        "Warm light surface",
        (0.95, 0.78, 0.48, 1),
        roughness=0.35,
        emission=(1.0, 0.54, 0.20, 1),
        emission_strength=2.0,
    )

    facade_front = empty("ANIM Front facade")
    facade_side = empty("ANIM Right facade")
    roof_group = empty("ANIM Roof")
    pv_group = empty("ANIM Photovoltaic")
    technical_group = empty("ANIM Energy equipment")

    # Foundation, slabs and exposed concrete frame.
    add_box("Foundation", (0, 0, -0.28), (10.9, 8.9, 0.56), concrete, bevel=0.10)
    add_box("Ground floor slab", (0, 0, 0.07), (10.35, 8.35, 0.20), concrete, bevel=0.055)
    add_box("Upper floor slab", (0, -0.12, 3.25), (10.65, 8.6, 0.28), concrete, bevel=0.055)
    add_box("Front balcony", (0, -4.45, 3.25), (10.65, 1.25, 0.28), concrete, bevel=0.055)
    add_box("Terrace", (-0.4, -4.55, 0.12), (9.8, 1.35, 0.22), concrete, bevel=0.055)
    for x in (-4.82, 4.82):
        add_box("Concrete column", (x, -4.45, 1.7), (0.28, 0.28, 3.15), concrete, bevel=0.035)
        add_box("Concrete column upper", (x, -4.45, 4.55), (0.28, 0.28, 2.4), concrete, bevel=0.035)

    # Static left and rear envelope.
    add_box("Left wall ground", (-4.88, 0, 1.67), (0.28, 7.75, 2.92), white)
    add_box("Left wall upper", (-4.88, 0, 4.55), (0.28, 7.75, 2.4), white)
    add_box("Rear wall ground", (0, 3.88, 1.67), (9.55, 0.28, 2.92), white)
    add_box("Rear wall upper", (0, 3.88, 4.55), (9.55, 0.28, 2.4), white)
    add_gable("Rear gable", 3.88, white)

    # Front facade assembled around openings.
    for x, width in ((-4.15, 1.18), (-0.72, 1.16), (3.63, 2.20)):
        add_box("Front wall ground", (x, -3.88, 1.67), (width, 0.28, 2.92), white, parent=facade_front)
    add_box("Front wall ground lintel", (0.25, -3.88, 3.00), (8.0, 0.28, 0.28), white, parent=facade_front)
    add_front_window("Living room", -2.55, 1.64, 2.0, 2.35, glass, dark, facade_front)
    add_front_window("Entrance", 1.52, 1.60, 2.7, 2.42, glass, dark, facade_front)
    for x, width in ((-4.1, 1.3), (-0.8, 1.0), (3.7, 2.0)):
        add_box("Front wall upper", (x, -3.88, 4.55), (width, 0.28, 2.4), white, parent=facade_front)
    add_gable("Front gable", -3.88, white, parent=facade_front)
    add_front_window("Bedroom upper", -2.45, 4.72, 2.05, 2.12, glass, dark, facade_front)
    add_front_window("Gallery upper", 1.55, 4.72, 2.85, 2.12, glass, dark, facade_front)

    # Right facade around openings.
    for y, width in ((-3.35, 1.02), (-0.35, 2.1), (3.18, 1.15)):
        add_box("Right wall ground", (4.88, y, 1.67), (0.28, width, 2.92), white, parent=facade_side)
    add_side_window("Dining side", -1.85, 1.67, 1.75, 2.3, glass, dark, facade_side)
    add_side_window("Service side", 1.92, 1.67, 1.35, 1.55, glass, dark, facade_side)
    for y, width in ((-3.4, 0.9), (-0.45, 2.4), (3.2, 1.05)):
        add_box("Right wall upper", (4.88, y, 4.55), (0.28, width, 2.4), white, parent=facade_side)
    add_side_window("Upper side", -2.02, 4.75, 1.65, 1.9, glass, dark, facade_side)
    add_side_window("Upper rear side", 1.75, 4.75, 1.55, 1.8, glass, dark, facade_side)

    # Timber slats create the same warm vertical rhythm as the mockup.
    for index in range(11):
        x = 2.6 + index * 0.17
        add_box("Upper timber slat", (x, -4.07, 4.75), (0.105, 0.16, 2.28), wood, bevel=0.018, parent=facade_front)
    for index in range(9):
        y = -0.3 + index * 0.19
        add_box("Side timber slat", (5.06, y, 4.75), (0.16, 0.105, 2.28), wood, bevel=0.018, parent=facade_side)

    # Roof as two clean solid planes with timber soffits and gutters.
    roof_angle = math.radians(28)
    add_box("Roof right", (2.62, 0, 7.18), (5.92, 9.3, 0.30), roof_mat, rotation=(0, roof_angle, 0), bevel=0.045, parent=roof_group)
    add_box("Roof left", (-2.62, 0, 7.18), (5.92, 9.3, 0.30), roof_mat, rotation=(0, -roof_angle, 0), bevel=0.045, parent=roof_group)
    add_box("Soffit right", (2.57, 0, 7.00), (5.72, 9.02, 0.10), wood, rotation=(0, roof_angle, 0), bevel=0.025, parent=roof_group)
    add_box("Soffit left", (-2.57, 0, 7.00), (5.72, 9.02, 0.10), wood, rotation=(0, -roof_angle, 0), bevel=0.025, parent=roof_group)
    add_cylinder("Right gutter", (5.25, 0, 5.77), 0.09, 9.1, dark, rotation=(math.pi / 2, 0, 0), parent=roof_group)
    add_cylinder("Downpipe", (5.27, 3.45, 2.82), 0.07, 5.8, dark, parent=facade_side)

    # Interior architecture and furniture, visible after the facade opens.
    add_box("Ground floor finish", (0, 0, 0.24), (9.4, 7.4, 0.10), floor_mat, bevel=0.018)
    add_box("Upper floor finish", (0, 0, 3.43), (9.4, 7.4, 0.10), floor_mat, bevel=0.018)
    add_box("Interior partition ground", (0.15, 1.05, 1.72), (0.16, 5.25, 2.84), interior_white, bevel=0.025)
    add_box("Interior partition upper", (-1.15, 0.8, 4.78), (0.16, 5.65, 2.78), interior_white, bevel=0.025)
    add_box("Kitchen wall", (2.75, 2.25, 1.72), (3.8, 0.14, 2.8), interior_white, bevel=0.025)

    # Staircase.
    for step in range(13):
        add_box(
            "Oak stair",
            (0.9, 1.95 - step * 0.25, 0.38 + step * 0.22),
            (1.65, 0.34, 0.16),
            floor_mat,
            bevel=0.025,
        )
    add_curve("Stair handrail", [(1.78, 2.1, 0.78), (1.78, -1.15, 3.55)], dark, bevel_depth=0.028)

    # Minimal furniture and kitchen for scale.
    add_box("Kitchen base", (2.65, 2.0, 0.78), (3.55, 0.65, 1.02), wood, bevel=0.035)
    add_box("Kitchen worktop", (2.65, 1.98, 1.34), (3.65, 0.72, 0.10), dark, bevel=0.025)
    add_box("Kitchen wall units", (3.25, 2.12, 2.22), (2.35, 0.46, 0.82), wood, bevel=0.035)
    add_box("Sofa seat", (-2.55, 1.25, 0.63), (2.35, 0.92, 0.34), interior_white, bevel=0.14)
    add_box("Sofa back", (-2.55, 1.62, 1.05), (2.35, 0.24, 0.72), interior_white, bevel=0.12)
    add_box("Dining table", (2.65, -0.9, 0.95), (2.15, 0.95, 0.10), wood, bevel=0.035)
    for x in (1.85, 3.45):
        for y in (-1.28, -0.52):
            add_cylinder("Table leg", (x, y, 0.52), 0.045, 0.86, dark)
    add_box("Upper bed", (-2.9, 0.6, 3.83), (2.55, 2.0, 0.38), interior_white, bevel=0.15)
    add_box("Upper headboard", (-2.9, 1.5, 4.38), (2.55, 0.18, 1.0), wood, bevel=0.08)

    # Electrical distribution, KNX/network modules and the red system path.
    # The technical wall faces the open front of the cutaway so that the
    # installation remains legible even at website scale.
    add_box("Distribution cabinet", (2.7, 3.70, 1.72), (1.48, 0.22, 1.95), interior_white, bevel=0.035)
    add_box("Distribution recess", (2.7, 3.56, 1.72), (1.24, 0.08, 1.64), dark, bevel=0.02)
    for row in range(5):
        for module in range(5):
            add_box("Breaker", (2.25 + module * 0.22, 3.48, 1.17 + row * 0.25), (0.16, 0.06, 0.14), interior_white, bevel=0.012)
    add_box("Network cabinet", (4.0, 3.68, 0.9), (1.05, 0.30, 1.28), dark, bevel=0.04)
    for row in range(5):
        add_box("Network patch row", (4.0, 3.48, 0.55 + row * 0.18), (0.78, 0.06, 0.08), red if row == 2 else interior_white, bevel=0.008)
    for x, y, z in ((-3.6, -3.73, 1.45), (0.8, -3.73, 1.45), (3.8, -3.73, 4.65), (4.7, -1.2, 4.6)):
        add_box("KNX control", (x, y, z), (0.16, 0.08, 0.24) if abs(y) > 3 else (0.08, 0.16, 0.24), dark, bevel=0.025)
    add_curve(
        "Hubmann installation path",
        [
            (4.9, -4.75, -0.45),
            (4.1, -3.55, 0.35),
            (-2.7, -3.55, 0.35),
            (-2.7, -3.55, 3.52),
            (0.4, -3.55, 3.52),
            (4.1, -3.55, 3.52),
            (4.1, 2.9, 3.52),
        ],
        red,
        bevel_depth=0.035,
        smooth=False,
    )

    # Lighting fixtures and warm final-state light sources.
    light_objects: list[bpy.types.Object] = []
    for index, location in enumerate(((-2.5, -1.5, 3.08), (2.4, -1.0, 3.08), (-0.2, 1.0, 3.08), (3.0, 1.2, 3.08))):
        add_cylinder(f"Downlight trim {index}", location, 0.12, 0.06, dark)
        light_data = bpy.data.lights.new(f"Warm downlight {index}", type="POINT")
        light_data.color = (1.0, 0.58, 0.28)
        light_data.energy = 0
        light_data.shadow_soft_size = 1.2
        light = bpy.data.objects.new(f"Warm downlight {index}", light_data)
        light.location = (location[0], location[1], location[2] - 0.25)
        bpy.context.collection.objects.link(light)
        light_objects.append(light)

    # Photovoltaic modules sit on the right roof plane and fly in individually.
    pv_final: list[tuple[bpy.types.Object, Vector]] = []
    module_index = 0
    for x in (1.25, 2.55, 3.85):
        for y in (-2.25, -0.15, 1.95):
            z = 8.57 - x * math.tan(roof_angle) + 0.12
            module = empty(f"PV module assembly {module_index + 1}")
            module.parent = pv_group
            module.location = (x, y, z)
            module.rotation_euler = (0, roof_angle, 0)
            add_box(
                f"PV module {module_index + 1}",
                (0, 0, 0),
                (1.10, 1.78, 0.10),
                pv,
                bevel=0.025,
                parent=module,
            )
            # Silver perimeter frame and two subtle cell separators.
            add_box(f"PV frame top {module_index}", (0, -0.86, 0.03), (1.12, 0.035, 0.07), dark, bevel=0.008, parent=module)
            add_box(f"PV frame bottom {module_index}", (0, 0.86, 0.03), (1.12, 0.035, 0.07), dark, bevel=0.008, parent=module)
            add_box(f"PV frame left {module_index}", (-0.54, 0, 0.03), (0.035, 1.72, 0.07), dark, bevel=0.008, parent=module)
            add_box(f"PV frame right {module_index}", (0.54, 0, 0.03), (0.035, 1.72, 0.07), dark, bevel=0.008, parent=module)
            pv_final.append((module, Vector(module.location)))
            module_index += 1

    # Inverter and battery are separated for the energy reveal.
    inverter = add_box("PV inverter", (5.18, 2.6, 2.25), (0.32, 0.92, 1.15), interior_white, bevel=0.07, parent=technical_group)
    add_box("Inverter display", (5.36, 2.6, 2.25), (0.035, 0.22, 0.13), dark, bevel=0.018, parent=technical_group)
    battery = add_box("Battery storage", (5.18, 2.62, 0.92), (0.42, 1.02, 1.36), interior_white, bevel=0.09, parent=technical_group)
    add_curve("PV DC cable", [(5.25, 2.6, 5.9), (5.25, 2.6, 3.0), (5.25, 2.6, 1.1), (5.0, 3.8, 0.0)], red, bevel_depth=0.03, parent=technical_group)

    # Studio floor.
    bpy.ops.mesh.primitive_plane_add(size=70, location=(0, 0, -0.59))
    studio_floor = bpy.context.object
    studio_floor.name = "White studio floor"
    apply_material(studio_floor, material("Studio white", (0.97, 0.97, 0.97, 1), roughness=0.82))

    # Camera and animated focus target.
    target = empty("Camera focus")
    target.location = (0, 0, 3.0)
    bpy.ops.object.camera_add(location=(21.0, -28.5, 15.8))
    camera = bpy.context.object
    camera.name = "Hero camera"
    camera.data.lens = 58
    camera.data.sensor_width = 36
    constraint = camera.constraints.new(type="TRACK_TO")
    constraint.target = target
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"
    bpy.context.scene.camera = camera

    keyframe_transform(camera, 1, location=(21.0, -28.5, 15.8))
    keyframe_transform(camera, 28, location=(20.0, -27.0, 15.0))
    keyframe_transform(camera, 52, location=(15.8, -22.0, 8.8))
    keyframe_transform(camera, 70, location=(15.2, -21.0, 9.4))
    keyframe_transform(camera, 92, location=(18.2, -24.0, 17.8))
    keyframe_transform(camera, 120, location=(21.0, -28.5, 15.8))
    keyframe_transform(target, 1, location=(0, 0, 3.0))
    keyframe_transform(target, 52, location=(0.45, 0.2, 2.65))
    keyframe_transform(target, 72, location=(0.2, 0.1, 3.5))
    keyframe_transform(target, 92, location=(1.7, 0.1, 6.3))
    keyframe_transform(target, 120, location=(0, 0, 3.1))

    # Facade and roof reveal choreography.
    keyframe_transform(facade_front, 1, location=(0, 0, 0), rotation=(0, 0, 0))
    keyframe_transform(facade_front, 27, location=(0, 0, 0), rotation=(0, 0, 0))
    keyframe_transform(facade_front, 49, location=(-14.5, -1.0, 0.4), rotation=(0, 0, math.radians(-7)))
    keyframe_transform(facade_front, 96, location=(-14.5, -1.0, 0.4), rotation=(0, 0, math.radians(-7)))
    keyframe_transform(facade_front, 113, location=(0, 0, 0), rotation=(0, 0, 0))
    keyframe_transform(facade_side, 1, location=(0, 0, 0), rotation=(0, 0, 0))
    keyframe_transform(facade_side, 27, location=(0, 0, 0), rotation=(0, 0, 0))
    keyframe_transform(facade_side, 49, location=(13.0, 0.8, 0.6), rotation=(0, 0, math.radians(7)))
    keyframe_transform(facade_side, 96, location=(13.0, 0.8, 0.6), rotation=(0, 0, math.radians(7)))
    keyframe_transform(facade_side, 113, location=(0, 0, 0), rotation=(0, 0, 0))
    keyframe_transform(roof_group, 1, location=(0, 0, 0), rotation=(0, 0, 0))
    keyframe_transform(roof_group, 27, location=(0, 0, 0), rotation=(0, 0, 0))
    keyframe_transform(roof_group, 49, location=(4.0, 0, 8.5), rotation=(math.radians(-4), 0, math.radians(5)))
    keyframe_transform(roof_group, 68, location=(4.0, 0, 8.5), rotation=(math.radians(-4), 0, math.radians(5)))
    keyframe_transform(roof_group, 82, location=(0, 0, 0), rotation=(0, 0, 0))

    # PV and energy equipment reveal from alternating sides.
    for index, (panel, final_location) in enumerate(pv_final):
        entry = final_location + Vector((8.0 if index % 2 == 0 else -8.0, 0, 4.0 + index * 0.18))
        keyframe_transform(panel, 69, location=entry, scale=(0.01, 0.01, 0.01))
        settle_frame = 82 + index
        keyframe_transform(panel, settle_frame, location=tuple(final_location), scale=(1, 1, 1))
    keyframe_transform(technical_group, 69, location=(7.0, 0, 0), scale=(0.01, 0.01, 0.01))
    keyframe_transform(technical_group, 91, location=(0, 0, 0), scale=(1, 1, 1))
    keyframe_transform(technical_group, 96, location=(0, 0, 0), scale=(1, 1, 1))
    keyframe_transform(technical_group, 112, location=(7.0, 0, 0), scale=(0.01, 0.01, 0.01))

    for light in light_objects:
        light.data.keyframe_insert(data_path="energy", frame=103)
        light.data.energy = 125
        light.data.keyframe_insert(data_path="energy", frame=118)

    # Large soft studio lighting.
    def area_light(name: str, location: tuple[float, float, float], energy: float, size: float, color: tuple[float, float, float]) -> None:
        data = bpy.data.lights.new(name, type="AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        data.color = color
        obj = bpy.data.objects.new(name, data)
        obj.location = location
        bpy.context.collection.objects.link(obj)
        track = obj.constraints.new(type="TRACK_TO")
        track.target = target
        track.track_axis = "TRACK_NEGATIVE_Z"
        track.up_axis = "UP_Y"

    area_light("Key softbox", (-8, -11, 18), 2200, 8.0, (1.0, 0.93, 0.84))
    area_light("Fill softbox", (13, -3, 10), 1500, 7.0, (0.82, 0.90, 1.0))
    area_light("Rear softbox", (-5, 11, 14), 1800, 6.0, (1.0, 0.88, 0.74))

    scene = bpy.context.scene
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = RENDER_WIDTH
    scene.render.resolution_y = RENDER_HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.quality = 90
    scene.render.fps = 30
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.render.filepath = str(SEQUENCE_DIR / "house-")
    scene.world.color = (1.0, 1.0, 1.0)
    if scene.world.use_nodes:
        background = scene.world.node_tree.nodes.get("Background")
        background.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        background.inputs["Strength"].default_value = 0.95
    scene.view_settings.view_transform = "Standard"
    try:
        scene.view_settings.look = "Medium High Contrast"
    except TypeError:
        pass

    BLEND_PATH.parent.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)
    SEQUENCE_DIR.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))


def parse_args() -> set[str]:
    if "--" not in sys.argv:
        return set()
    return set(sys.argv[sys.argv.index("--") + 1 :])


def main() -> None:
    args = parse_args()
    build_scene()
    scene = bpy.context.scene
    if "--render-animation" in args:
        scene.frame_start = int(os.environ.get("HUBMANN_FRAME_START", str(FRAME_START)))
        scene.frame_end = int(os.environ.get("HUBMANN_FRAME_END", str(FRAME_END)))
        scene.render.filepath = str(SEQUENCE_DIR / "house-")
        bpy.ops.render.render(animation=True)
    elif "--render-still" in args:
        frame = int(os.environ.get("HUBMANN_FRAME", "1"))
        scene.frame_set(frame)
        scene.render.filepath = str(QA_DIR / f"house-frame-{frame:03d}.jpg")
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
