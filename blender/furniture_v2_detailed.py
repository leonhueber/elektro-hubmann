"""Build a detailed, append-ready furniture library for house V2.

This module is intentionally isolated from ``house_v2.py`` because the house is
developed in another task.  It opens the current V2 scene only as read-only
context, hides the blockout furniture for preview renders and writes a separate
Blender library containing exactly one collection: ``V2 DETAILED FURNITURE``.

Run with Blender 5.2+:

    blender assets/3d/elektro-hubmann-house-v2.blend --background \
        --python blender/furniture_v2_detailed.py

The library objects use the unscaled V2 design coordinates.  When appended to
the house, parent their top-level objects to ``V2 Rebuild width match``.
"""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
LIBRARY_PATH = ROOT / "assets" / "3d" / "elektro-hubmann-furniture-v2.blend"
QA_DIR = ROOT / "docs" / "version-g-qa" / "blender-v2" / "furniture-detail-v03"
COLLECTION_NAME = "V2 DETAILED FURNITURE"
PREVIEW_COLLECTION = "F2 PREVIEW"
HOUSE_SCALE_X = 1.16


def remove_collection(name: str) -> None:
    collection = bpy.data.collections.get(name)
    if collection is None:
        return
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(collection)


def create_collection(name: str) -> bpy.types.Collection:
    remove_collection(name)
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def move_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    collection.objects.link(obj)


def material(
    name: str,
    color: tuple[float, float, float, float],
    *,
    roughness: float,
    metallic: float = 0.0,
    fabric_bump: bool = False,
    wood_grain: bool = False,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    existing = bpy.data.materials.get(name)
    if existing is not None:
        return existing
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    shader = nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic

    if emission_strength > 0.0:
        emission_color = shader.inputs.get("Emission Color")
        emission = shader.inputs.get("Emission Strength")
        if emission_color is not None:
            emission_color.default_value = color
        if emission is not None:
            emission.default_value = emission_strength

    if fabric_bump:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.name = f"{name} weave"
        noise.inputs["Scale"].default_value = 145.0
        noise.inputs["Detail"].default_value = 2.0
        noise.inputs["Roughness"].default_value = 0.72
        bump = nodes.new("ShaderNodeBump")
        bump.name = f"{name} micro weave"
        bump.inputs["Strength"].default_value = 0.20
        bump.inputs["Distance"].default_value = 0.018
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], shader.inputs["Normal"])

    if wood_grain:
        coordinates = nodes.new("ShaderNodeTexCoord")
        wave = nodes.new("ShaderNodeTexWave")
        wave.wave_type = "BANDS"
        wave.bands_direction = "X"
        wave.inputs["Scale"].default_value = 4.0
        wave.inputs["Distortion"].default_value = 1.8
        wave.inputs["Detail"].default_value = 2.0
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (
            color[0] * 0.89,
            color[1] * 0.88,
            color[2] * 0.86,
            1.0,
        )
        ramp.color_ramp.elements[1].color = (
            min(1.0, color[0] * 1.08),
            min(1.0, color[1] * 1.09),
            min(1.0, color[2] * 1.10),
            1.0,
        )
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.12
        bump.inputs["Distance"].default_value = 0.025
        links.new(coordinates.outputs["Generated"], wave.inputs["Vector"])
        links.new(wave.outputs["Color"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], shader.inputs["Base Color"])
        links.new(wave.outputs["Color"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], shader.inputs["Normal"])

    return mat


def glass_material() -> bpy.types.Material:
    mat = material("F2 clear glass", (0.70, 0.82, 0.84, 0.18), roughness=0.08)
    mat.diffuse_color = (0.70, 0.82, 0.84, 0.18)
    shader = mat.node_tree.nodes.get("Principled BSDF")
    transmission = shader.inputs.get("Transmission Weight")
    if transmission is not None:
        transmission.default_value = 0.94
    alpha = shader.inputs.get("Alpha")
    if alpha is not None:
        alpha.default_value = 0.18
    shader.inputs["IOR"].default_value = 1.45
    try:
        mat.surface_render_method = "DITHERED"
    except (AttributeError, TypeError):
        pass
    return mat


def palette() -> dict[str, bpy.types.Material]:
    return {
        "oak": material(
            "F2 natural oak", (0.57, 0.34, 0.16, 1.0), roughness=0.50, wood_grain=True
        ),
        "oak_light": material(
            "F2 light oak", (0.71, 0.50, 0.29, 1.0), roughness=0.56, wood_grain=True
        ),
        "fabric": material(
            "F2 warm boucle", (0.74, 0.70, 0.63, 1.0), roughness=0.92, fabric_bump=True
        ),
        "fabric_light": material(
            "F2 ivory textile", (0.90, 0.88, 0.83, 1.0), roughness=0.96, fabric_bump=True
        ),
        "fabric_accent": material(
            "F2 greige textile", (0.48, 0.43, 0.37, 1.0), roughness=0.93, fabric_bump=True
        ),
        "charcoal": material(
            "F2 charcoal metal", (0.035, 0.040, 0.044, 1.0), roughness=0.30, metallic=0.68
        ),
        "black": material("F2 satin black", (0.012, 0.014, 0.016, 1.0), roughness=0.38),
        "porcelain": material("F2 porcelain", (0.94, 0.93, 0.89, 1.0), roughness=0.30),
        "stone": material("F2 worktop stone", (0.24, 0.25, 0.24, 1.0), roughness=0.37),
        "ceramic": material("F2 warm ceramic", (0.78, 0.70, 0.58, 1.0), roughness=0.58),
        "plant": material("F2 plant green", (0.055, 0.20, 0.075, 1.0), roughness=0.74),
        "soil": material("F2 soil", (0.055, 0.032, 0.018, 1.0), roughness=0.95),
        "glass": glass_material(),
        "mirror": material("F2 mirror", (0.34, 0.42, 0.44, 1.0), roughness=0.08, metallic=0.76),
        "glow": material(
            "F2 warm light", (1.0, 0.66, 0.31, 1.0), roughness=0.25, emission_strength=5.0
        ),
        "screen": material(
            "F2 screen", (0.018, 0.025, 0.030, 1.0), roughness=0.18, metallic=0.18
        ),
    }


def add_group(
    name: str,
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation_z: float = 0.0,
) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.location = location
    obj.rotation_euler.z = rotation_z
    bpy.data.collections[COLLECTION_NAME].objects.link(obj)
    return obj


def add_box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    mat: bpy.types.Material,
    *,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel: float = 0.02,
    segments: int = 3,
    parent: bpy.types.Object | None = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to_collection(obj, bpy.data.collections[COLLECTION_NAME])
    obj.data.materials.append(mat)
    if bevel > 0.0:
        modifier = obj.modifiers.new("F2 softened edge", "BEVEL")
        modifier.width = bevel
        modifier.segments = segments
    if parent is not None:
        obj.parent = parent
    return obj


def add_cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    mat: bpy.types.Material,
    *,
    vertices: int = 32,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    parent: bpy.types.Object | None = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation
    )
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, bpy.data.collections[COLLECTION_NAME])
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new("F2 cylinder edge", "BEVEL")
    bevel.width = min(radius * 0.14, depth * 0.10)
    bevel.segments = 2
    if parent is not None:
        obj.parent = parent
    return obj


def add_cone(
    name: str,
    location: tuple[float, float, float],
    radius1: float,
    radius2: float,
    depth: float,
    mat: bpy.types.Material,
    *,
    parent: bpy.types.Object | None = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cone_add(
        vertices=40,
        radius1=radius1,
        radius2=radius2,
        depth=depth,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, bpy.data.collections[COLLECTION_NAME])
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new("F2 cone edge", "BEVEL")
    bevel.width = 0.012
    bevel.segments = 2
    if parent is not None:
        obj.parent = parent
    return obj


def add_ellipsoid(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    mat: bpy.types.Material,
    *,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    parent: bpy.types.Object | None = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32, ring_count=18, location=location, rotation=rotation
    )
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to_collection(obj, bpy.data.collections[COLLECTION_NAME])
    obj.data.materials.append(mat)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    if parent is not None:
        obj.parent = parent
    return obj


def add_torus(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    mat: bpy.types.Material,
    *,
    parent: bpy.types.Object | None = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(
        align="WORLD",
        major_segments=48,
        minor_segments=16,
        location=location,
        major_radius=0.30,
        minor_radius=0.055,
    )
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to_collection(obj, bpy.data.collections[COLLECTION_NAME])
    obj.data.materials.append(mat)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    if parent is not None:
        obj.parent = parent
    return obj


def add_pipe(
    name: str,
    points: list[tuple[float, float, float]],
    radius: float,
    mat: bpy.types.Material,
    *,
    parent: bpy.types.Object | None = None,
) -> bpy.types.Object:
    curve_data = bpy.data.curves.new(f"{name} curve", "CURVE")
    curve_data.dimensions = "3D"
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = 3
    curve_data.resolution_u = 12
    spline = curve_data.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, coordinates in zip(spline.bezier_points, points):
        point.co = coordinates
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve_data)
    bpy.data.collections[COLLECTION_NAME].objects.link(obj)
    curve_data.materials.append(mat)
    if parent is not None:
        obj.parent = parent
    return obj


def add_quilt(
    name: str,
    center: tuple[float, float, float],
    size: tuple[float, float],
    mat: bpy.types.Material,
) -> bpy.types.Object:
    columns, rows = 18, 22
    width, depth = size
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    for row in range(rows):
        v = row / (rows - 1)
        y = center[1] + (v - 0.5) * depth
        for column in range(columns):
            u = column / (columns - 1)
            x = center[0] + (u - 0.5) * width
            edge = math.sin(math.pi * u) * math.sin(math.pi * v)
            folds = 0.026 * math.sin(u * math.pi * 7.0 + v * 1.7)
            crown = 0.075 * edge + folds * edge
            vertices.append((x, y, center[2] + crown))
    for row in range(rows - 1):
        for column in range(columns - 1):
            i = row * columns + column
            faces.append((i, i + 1, i + columns + 1, i + columns))
    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    bpy.data.collections[COLLECTION_NAME].objects.link(obj)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    solidify = obj.modifiers.new("F2 quilt thickness", "SOLIDIFY")
    solidify.thickness = 0.10
    solidify.offset = -0.70
    bevel = obj.modifiers.new("F2 quilt hem", "BEVEL")
    bevel.width = 0.035
    bevel.segments = 3
    return obj


def build_sofa_and_living(m: dict[str, bpy.types.Material]) -> None:
    add_box("F2 sofa shadow plinth", (-3.42, 2.32, 0.40), (2.58, 0.92, 0.11), m["charcoal"], bevel=0.025)
    for x in (-4.42, -2.42):
        for y in (2.02, 2.60):
            add_box(f"F2 sofa leg {x:.2f} {y:.2f}", (x, y, 0.43), (0.055, 0.055, 0.22), m["charcoal"], bevel=0.010)
    add_box("F2 sofa body", (-3.42, 2.33, 0.58), (2.58, 0.92, 0.30), m["fabric"], bevel=0.11, segments=5)
    for index, x in enumerate((-3.99, -2.85), 1):
        add_box(f"F2 sofa seat cushion {index}", (x, 2.14, 0.79), (1.06, 0.72, 0.23), m["fabric_light"], bevel=0.105, segments=5)
        add_box(
            f"F2 sofa back cushion {index}",
            (x, 2.51, 1.15),
            (1.04, 0.24, 0.67),
            m["fabric"],
            rotation=(math.radians(-7.0), 0.0, 0.0),
            bevel=0.11,
            segments=5,
        )
    add_box("F2 sofa rear support", (-3.42, 2.66, 1.02), (2.58, 0.17, 0.93), m["fabric"], bevel=0.075, segments=4)
    for side, x in (("left", -4.64), ("right", -2.20)):
        add_box(f"F2 sofa arm {side}", (x, 2.29, 0.82), (0.18, 0.86, 0.67), m["fabric"], bevel=0.075, segments=4)
    add_box("F2 sofa accent pillow", (-4.15, 2.05, 1.13), (0.46, 0.18, 0.48), m["fabric_accent"], rotation=(math.radians(-5.0), math.radians(7.0), math.radians(-7.0)), bevel=0.12, segments=5)
    add_box("F2 sofa ivory pillow", (-2.57, 2.05, 1.12), (0.42, 0.18, 0.44), m["fabric_light"], rotation=(math.radians(-4.0), math.radians(-5.0), math.radians(6.0)), bevel=0.11, segments=5)

    chair = add_group("F2 lounge chair", (-1.78, -0.18, 0.0), math.radians(-16.0))
    for x in (-0.29, 0.29):
        for y in (-0.25, 0.24):
            add_cylinder(f"F2 lounge leg {x:+.2f} {y:+.2f}", (x, y, 0.49), 0.026, 0.34, m["charcoal"], vertices=18, parent=chair)
    add_box("F2 lounge shell seat", (0.0, 0.0, 0.68), (0.88, 0.82, 0.28), m["fabric"], bevel=0.12, segments=5, parent=chair)
    add_box("F2 lounge seat cushion", (0.0, -0.04, 0.82), (0.72, 0.62, 0.16), m["fabric_light"], bevel=0.09, segments=5, parent=chair)
    add_box("F2 lounge back", (0.0, 0.30, 1.13), (0.84, 0.20, 0.80), m["fabric"], rotation=(math.radians(-9.0), 0.0, 0.0), bevel=0.10, segments=5, parent=chair)
    for x in (-0.43, 0.43):
        add_box(f"F2 lounge arm {x:+.2f}", (x, 0.02, 0.91), (0.12, 0.68, 0.40), m["fabric"], bevel=0.06, segments=4, parent=chair)

    add_box("F2 coffee table oak top", (-3.05, 0.55, 0.68), (1.50, 0.78, 0.09), m["oak_light"], bevel=0.045, segments=4)
    for x in (-3.62, -2.48):
        add_pipe(f"F2 coffee sled {x:.2f}", [(x, 0.25, 0.35), (x, 0.25, 0.63), (x, 0.85, 0.63), (x, 0.85, 0.35)], 0.025, m["charcoal"])
    add_box("F2 coffee table book", (-3.28, 0.52, 0.75), (0.42, 0.28, 0.05), m["fabric_accent"], rotation=(0.0, 0.0, math.radians(7.0)), bevel=0.012)
    add_cylinder("F2 coffee cup", (-2.80, 0.52, 0.79), 0.08, 0.11, m["porcelain"], vertices=32)

    add_box("F2 TV console body", (-1.52, 3.30, 0.64), (1.34, 0.42, 0.54), m["oak"], bevel=0.035, segments=3)
    for x in (-1.96, -1.52, -1.08):
        add_box(f"F2 TV console joint {x:.2f}", (x, 3.075, 0.64), (0.018, 0.025, 0.42), m["black"], bevel=0.002)
    add_box("F2 TV screen", (-1.52, 3.51, 1.48), (1.32, 0.065, 0.78), m["screen"], bevel=0.028, segments=3)
    add_box("F2 TV inner panel", (-1.52, 3.47, 1.48), (1.20, 0.018, 0.66), m["black"], bevel=0.015)

    add_cylinder("F2 plant pot", (-4.30, 0.95, 0.55), 0.23, 0.48, m["ceramic"], vertices=40)
    add_cylinder("F2 plant soil", (-4.30, 0.95, 0.80), 0.19, 0.035, m["soil"], vertices=32)
    for index, (dx, dy, height, bend) in enumerate(((-0.08, 0.0, 0.80, -0.20), (0.05, 0.0, 1.02, 0.18), (0.0, 0.04, 0.64, 0.08)), 1):
        add_pipe(f"F2 plant stem {index}", [(-4.30, 0.95, 0.80), (-4.30 + dx, 0.95 + dy, 0.80 + height * 0.58), (-4.30 + dx + bend, 0.95 + dy, 0.80 + height)], 0.018, m["plant"])
    for index, (x, y, z, rz) in enumerate(((-4.50, 0.95, 1.27, -0.45), (-4.18, 0.96, 1.48, 0.50), (-4.37, 0.96, 1.67, -0.18), (-4.12, 0.98, 1.30, 0.35), (-4.46, 0.97, 1.52, -0.42)), 1):
        add_ellipsoid(f"F2 plant leaf {index}", (x, y, z), (0.42, 0.10, 0.20), m["plant"], rotation=(0.0, rz, 0.0))


def add_dining_chair(index: int, location: tuple[float, float, float], facing: int, m: dict[str, bpy.types.Material]) -> None:
    # The chair back must face away from the table.  The previous sign was
    # inverted, so both rows looked as if they were turning their backs to it.
    group = add_group(f"F2 dining chair {index}", location, math.pi if facing > 0 else 0.0)
    add_box(f"F2 chair {index} underframe", (0.0, 0.0, 0.68), (0.48, 0.50, 0.10), m["charcoal"], bevel=0.025, parent=group)
    add_box(f"F2 chair {index} seat", (0.0, 0.0, 0.78), (0.50, 0.52, 0.16), m["fabric_light"], bevel=0.07, segments=4, parent=group)
    add_box(f"F2 chair {index} back", (0.0, 0.25, 1.12), (0.50, 0.14, 0.70), m["fabric"], rotation=(math.radians(-6.0), 0.0, 0.0), bevel=0.07, segments=4, parent=group)
    for x in (-0.18, 0.18):
        for y in (-0.18, 0.18):
            add_cylinder(f"F2 chair {index} leg {x:+.2f} {y:+.2f}", (x, y, 0.51), 0.022, 0.48, m["charcoal"], vertices=16, rotation=(math.radians(y * 7.0), math.radians(-x * 7.0), 0.0), parent=group)


def build_dining_and_kitchen(m: dict[str, bpy.types.Material]) -> None:
    add_box("F2 dining table top", (2.90, -0.72, 1.04), (2.08, 1.06, 0.10), m["oak_light"], bevel=0.045, segments=4)
    add_box("F2 dining table underframe", (2.90, -0.72, 0.94), (1.82, 0.78, 0.10), m["charcoal"], bevel=0.018)
    for x in (2.12, 3.68):
        for y in (-1.06, -0.38):
            add_box(f"F2 dining table leg {x:.2f} {y:.2f}", (x, y, 0.64), (0.07, 0.07, 0.72), m["charcoal"], bevel=0.012)
    chair_positions = ((2.22, -1.53, 1), (2.90, -1.53, 1), (3.58, -1.53, 1), (2.22, 0.09, -1), (2.90, 0.09, -1), (3.58, 0.09, -1))
    for index, (x, y, facing) in enumerate(chair_positions, 1):
        add_dining_chair(index, (x, y, 0.0), facing, m)
    add_cylinder("F2 dining vase", (2.90, -0.72, 1.17), 0.10, 0.23, m["porcelain"], vertices=40)
    for index, dx in enumerate((-0.10, 0.0, 0.11), 1):
        add_pipe(f"F2 dining stem {index}", [(2.90, -0.72, 1.27), (2.90 + dx, -0.72, 1.57)], 0.010, m["plant"])
        add_ellipsoid(f"F2 dining leaf {index}", (2.90 + dx * 1.25, -0.72, 1.55), (0.22, 0.055, 0.10), m["plant"], rotation=(0.0, math.radians(dx * 190.0), 0.0))

    add_box("F2 kitchen toe kick", (3.16, 3.34, 0.42), (2.34, 0.52, 0.18), m["black"], bevel=0.012)
    add_box("F2 kitchen base carcass", (3.16, 3.34, 0.79), (2.34, 0.62, 0.78), m["oak"], bevel=0.028)
    for index, x in enumerate((2.28, 2.86, 3.44, 4.02), 1):
        add_box(f"F2 kitchen base front {index}", (x, 3.015, 0.80), (0.54, 0.035, 0.70), m["oak_light"], bevel=0.018)
        add_box(f"F2 kitchen handle {index}", (x, 2.992, 1.03), (0.26, 0.025, 0.025), m["charcoal"], bevel=0.008)
    add_box("F2 kitchen worktop", (3.16, 3.30, 1.22), (2.44, 0.70, 0.10), m["stone"], bevel=0.028, segments=3)
    add_box("F2 kitchen backsplash", (3.16, 3.58, 1.76), (2.44, 0.035, 0.96), m["porcelain"], bevel=0.010)
    add_box("F2 kitchen wall carcass", (3.10, 3.48, 2.28), (1.76, 0.42, 0.82), m["oak"], bevel=0.025)
    for index, x in enumerate((2.55, 3.10, 3.65), 1):
        add_box(f"F2 kitchen wall front {index}", (x, 3.252, 2.28), (0.51, 0.035, 0.72), m["oak_light"], bevel=0.018)
    add_box("F2 kitchen underlight", (3.10, 3.245, 1.86), (1.62, 0.028, 0.035), m["glow"], bevel=0.005)
    add_box("F2 kitchen tall cabinet", (4.24, 2.66, 1.52), (0.68, 0.72, 2.36), m["oak"], bevel=0.030)
    for z in (0.84, 1.45, 2.18):
        add_box(f"F2 tall cabinet joint {z:.2f}", (4.24, 2.278, z), (0.54, 0.025, 0.018), m["black"], bevel=0.003)
    add_box("F2 kitchen oven frame", (4.24, 2.270, 1.50), (0.54, 0.045, 0.66), m["charcoal"], bevel=0.022)
    add_box("F2 kitchen oven glass", (4.24, 2.242, 1.45), (0.45, 0.018, 0.44), m["screen"], bevel=0.015)
    for x in (4.10, 4.24, 4.38):
        add_cylinder(f"F2 oven knob {x:.2f}", (x, 2.225, 1.73), 0.025, 0.022, m["charcoal"], vertices=24, rotation=(math.pi / 2, 0.0, 0.0))

    add_box("F2 kitchen sink rim", (2.76, 2.96, 1.285), (0.68, 0.35, 0.055), m["charcoal"], bevel=0.045)
    add_box("F2 kitchen sink bowl", (2.76, 2.96, 1.278), (0.56, 0.25, 0.035), m["black"], bevel=0.045)
    add_pipe("F2 kitchen faucet", [(2.98, 3.05, 1.29), (2.98, 3.05, 1.64), (2.98, 2.84, 1.66), (2.90, 2.80, 1.58)], 0.024, m["charcoal"])
    add_box("F2 kitchen cooktop", (3.56, 2.98, 1.285), (0.64, 0.35, 0.024), m["screen"], bevel=0.030)
    for x in (3.40, 3.72):
        for y in (2.91, 3.05):
            add_cylinder(f"F2 cooktop zone {x:.2f} {y:.2f}", (x, y, 1.302), 0.095, 0.008, m["charcoal"], vertices=40)

    for index, x in enumerate((2.24, 2.90, 3.56), 1):
        add_pipe(f"F2 pendant cord {index}", [(x, -0.72, 2.98), (x, -0.72, 2.22)], 0.012, m["charcoal"])
        add_cone(f"F2 pendant shade {index}", (x, -0.72, 2.11), 0.15, 0.09, 0.23, m["black"])
        add_cylinder(f"F2 pendant glow {index}", (x, -0.72, 2.02), 0.065, 0.035, m["glow"], vertices=24)


def build_bedroom(m: dict[str, bpy.types.Material]) -> None:
    # Match the reference plan: headboard on the solid left exterior wall,
    # with the bed extending horizontally toward the central circulation zone.
    bed_x, bed_y = -3.38, -0.72
    add_box("F2 bedroom rug", (-3.31, bed_y, 3.57), (2.72, 2.48, 0.045), m["fabric"], bevel=0.035, segments=3)
    for x in (-4.24, -2.52):
        for y in (-1.46, 0.02):
            add_cylinder(f"F2 bed leg {x:.2f} {y:.2f}", (x, y, 3.67), 0.035, 0.22, m["charcoal"], vertices=20)
    add_box("F2 bed oak plinth", (bed_x, bed_y, 3.75), (2.22, 1.92, 0.24), m["oak"], bevel=0.055, segments=4)
    add_box("F2 bed mattress", (-3.33, bed_y, 3.96), (2.02, 1.82, 0.28), m["fabric_light"], bevel=0.105, segments=5)
    add_box("F2 bed headboard", (-4.50, bed_y, 4.28), (0.16, 2.00, 1.24), m["oak_light"], bevel=0.040, segments=3)
    for y in (-1.30, -0.72, -0.14):
        add_box(f"F2 headboard joint {y:.2f}", (-4.408, y, 4.28), (0.020, 0.020, 1.10), m["black"], bevel=0.002)
    add_quilt("F2 bed duvet", (-3.06, bed_y, 4.14), (1.18, 1.70), m["fabric_light"])
    for index, y in enumerate((-1.18, -0.26), 1):
        add_box(f"F2 bed pillow {index}", (-3.96, y, 4.18), (0.45, 0.72, 0.18), m["fabric_light"], rotation=(0.0, math.radians(-7.0), math.radians((-1) ** index * 2.0)), bevel=0.095, segments=5)
    add_box("F2 bed throw", (-2.72, bed_y, 4.24), (0.48, 1.70, 0.07), m["fabric_accent"], rotation=(0.0, 0.0, math.radians(-2.0)), bevel=0.055, segments=4)
    for side, y in (("front", -1.98), ("rear", 0.54)):
        add_box(f"F2 nightstand body {side}", (-4.36, y, 3.86), (0.50, 0.48, 0.58), m["oak"], bevel=0.035, segments=3)
        add_box(f"F2 nightstand drawer {side}", (-4.085, y, 3.95), (0.025, 0.42, 0.22), m["oak_light"], bevel=0.012)
        add_box(f"F2 nightstand pull {side}", (-4.065, y, 3.95), (0.018, 0.16, 0.018), m["charcoal"], bevel=0.006)
        add_cylinder(f"F2 bedside lamp base {side}", (-4.36, y, 4.18), 0.10, 0.045, m["charcoal"], vertices=32)
        add_cylinder(f"F2 bedside lamp stem {side}", (-4.36, y, 4.38), 0.017, 0.38, m["charcoal"], vertices=18)
        add_cone(f"F2 bedside shade {side}", (-4.36, y, 4.58), 0.16, 0.10, 0.23, m["fabric_light"])
        add_cylinder(f"F2 bedside glow {side}", (-4.36, y, 4.51), 0.055, 0.025, m["glow"], vertices=24)


def build_bathroom(m: dict[str, bpy.types.Material]) -> None:
    # The bathroom is the complete far-right upper bay.  Keep every fixture
    # beyond the gallery/bath partition at x=2.45.
    vanity_x = 3.28
    add_box("F2 bathroom vanity carcass", (vanity_x, 3.28, 4.12), (1.24, 0.50, 0.82), m["oak"], bevel=0.035, segments=3)
    for index, x in enumerate((2.89, 3.28, 3.67), 1):
        add_box(f"F2 vanity drawer {index}", (x, 3.012, 4.12), (0.36, 0.025, 0.68), m["oak_light"], bevel=0.012)
        add_box(f"F2 vanity pull {index}", (x, 2.992, 4.31), (0.18, 0.018, 0.018), m["charcoal"], bevel=0.006)
    add_box("F2 vanity top", (vanity_x, 3.24, 4.56), (1.30, 0.56, 0.08), m["stone"], bevel=0.025)
    add_box("F2 basin", (vanity_x, 3.10, 4.65), (0.74, 0.38, 0.14), m["porcelain"], bevel=0.065, segments=5)
    add_box("F2 basin inset", (vanity_x, 3.045, 4.72), (0.54, 0.24, 0.025), m["stone"], bevel=0.055)
    add_pipe("F2 basin faucet", [(3.60, 3.17, 4.62), (3.60, 3.17, 4.91), (3.48, 3.06, 4.91)], 0.018, m["charcoal"])
    add_box("F2 bathroom mirror", (vanity_x, 3.49, 5.28), (1.02, 0.035, 1.08), m["mirror"], bevel=0.018, segments=3)
    for x in (2.76, 3.80):
        add_box(f"F2 mirror frame side {x:.2f}", (x, 3.465, 5.28), (0.035, 0.04, 1.14), m["charcoal"], bevel=0.006)
    for z in (4.72, 5.84):
        add_box(f"F2 mirror frame horizontal {z:.2f}", (vanity_x, 3.465, z), (1.08, 0.04, 0.035), m["charcoal"], bevel=0.006)
    add_box("F2 mirror backlight", (vanity_x, 3.515, 5.28), (1.10, 0.018, 1.16), m["glow"], bevel=0.025)

    add_box("F2 shower tray", (4.02, 1.68, 3.62), (1.12, 1.14, 0.12), m["porcelain"], bevel=0.045, segments=3)
    add_box("F2 shower glass side", (3.47, 1.68, 4.68), (0.035, 1.12, 2.04), m["glass"], bevel=0.012)
    add_box("F2 shower glass rear", (4.02, 2.23, 4.68), (1.08, 0.035, 2.04), m["glass"], bevel=0.012)
    add_pipe("F2 shower riser", [(4.36, 2.17, 4.05), (4.36, 2.17, 5.44), (4.36, 1.96, 5.44)], 0.022, m["charcoal"])
    add_cylinder("F2 rain shower", (4.36, 1.90, 5.44), 0.14, 0.025, m["charcoal"], vertices=40)
    add_cylinder("F2 shower mixer", (4.36, 2.14, 4.62), 0.075, 0.045, m["charcoal"], vertices=28, rotation=(math.pi / 2, 0.0, 0.0))

    add_box("F2 toilet wall unit", (3.30, 0.00, 4.14), (0.58, 0.22, 0.70), m["porcelain"], bevel=0.085, segments=5)
    add_ellipsoid("F2 toilet bowl body", (3.30, -0.39, 3.91), (0.56, 0.68, 0.30), m["porcelain"])
    add_torus("F2 toilet seat ring", (3.30, -0.43, 4.075), (0.50, 0.60, 0.075), m["porcelain"])
    add_box("F2 toilet seat hinge", (3.30, -0.13, 4.07), (0.34, 0.10, 0.065), m["porcelain"], bevel=0.022)
    add_box("F2 toilet flush plate", (3.30, -0.122, 4.45), (0.28, 0.025, 0.17), m["charcoal"], bevel=0.025)


def build_furniture() -> bpy.types.Collection:
    create_collection(COLLECTION_NAME)
    m = palette()
    build_sofa_and_living(m)
    build_dining_and_kitchen(m)
    build_bedroom(m)
    build_bathroom(m)
    collection = bpy.data.collections[COLLECTION_NAME]
    collection["hubmann_asset_version"] = "furniture-detail-v03"
    collection["hubmann_coordinate_space"] = "V2 pre-scale"
    collection["hubmann_parent_target"] = "V2 Rebuild width match"
    return collection


def hide_blockout_furniture() -> None:
    old = bpy.data.collections.get("V2 FURNITURE")
    if old is not None:
        old.hide_render = True
        old.hide_viewport = True
    for obj in bpy.data.objects:
        if obj.name.startswith(("V2 R4 dining pendant", "V2 R4 bedroom lamp")):
            obj.hide_render = True


def parent_preview_to_house(collection: bpy.types.Collection) -> None:
    root = bpy.data.objects.get("V2 Rebuild width match")
    if root is None:
        return
    for obj in collection.objects:
        if obj.parent is None:
            obj.parent = root


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_preview_camera(
    name: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    lens: float,
) -> bpy.types.Object:
    data = bpy.data.cameras.new(f"{name} data")
    data.lens = lens
    camera = bpy.data.objects.new(name, data)
    bpy.data.collections[PREVIEW_COLLECTION].objects.link(camera)
    camera.location = location
    look_at(camera, target)
    return camera


def add_preview_light(
    name: str,
    location: tuple[float, float, float],
    energy: float,
    size: float,
    target: tuple[float, float, float],
) -> None:
    data = bpy.data.lights.new(f"{name} data", "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    light = bpy.data.objects.new(name, data)
    bpy.data.collections[PREVIEW_COLLECTION].objects.link(light)
    light.location = location
    look_at(light, target)


def setup_preview() -> dict[str, bpy.types.Object]:
    create_collection(PREVIEW_COLLECTION)
    scene = bpy.context.scene
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.world.color = (0.92, 0.92, 0.92)
    world_nodes = scene.world.node_tree.nodes if scene.world and scene.world.use_nodes else None
    if world_nodes:
        background = world_nodes.get("Background")
        if background is not None:
            background.inputs["Color"].default_value = (0.94, 0.94, 0.94, 1.0)
            background.inputs["Strength"].default_value = 0.65

    add_preview_light("F2 key", (3.0, -8.0, 10.5), 1500.0, 7.0, (0.0, 0.5, 3.0))
    add_preview_light("F2 fill", (-8.0, -3.0, 6.0), 1100.0, 6.0, (-1.0, 1.0, 2.4))
    add_preview_light("F2 rim", (7.0, 6.0, 9.0), 1300.0, 5.0, (1.0, 1.5, 3.2))

    # The house development scene contains many point lights. Their shadows
    # are unnecessary for furniture QA and can overflow Eevee's shadow atlas.
    for obj in bpy.data.objects:
        if obj.type == "LIGHT" and obj.data.type == "POINT":
            obj.data.use_shadow = False

    hero = bpy.data.objects.get("V2 Camera Mockup")
    if hero is None:
        hero = add_preview_camera("F2 context camera", (14.5, -31.5, 8.2), (0.0, 0.2, 3.0), 66.0)
    ground = add_preview_camera("F2 ground detail camera", (8.4, -16.2, 3.05), (-0.10, 0.70, 1.22), 70.0)
    upper = add_preview_camera("F2 upper detail camera", (8.5, -16.3, 6.10), (-0.25, 1.18, 4.66), 72.0)
    return {"context": hero, "ground": ground, "upper": upper}


def set_cutaway_visibility() -> None:
    facade = bpy.data.collections.get("V2 FACADE")
    plan = bpy.data.collections.get("V2 PLAN")
    if facade is not None:
        facade.hide_render = True
    if plan is not None:
        plan.hide_render = True
    for obj in bpy.data.objects:
        if obj.name.startswith("V2 Exterior right") and "span 0" in obj.name:
            obj.hide_render = True


def render_previews(cameras: dict[str, bpy.types.Object]) -> None:
    QA_DIR.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    set_cutaway_visibility()
    for key, filename in (
        ("context", "01-house-context.png"),
        ("ground", "02-living-dining-kitchen.png"),
        ("upper", "03-bedroom-bathroom.png"),
    ):
        scene.camera = cameras[key]
        scene.render.filepath = str(QA_DIR / filename)
        bpy.ops.render.render(write_still=True)


def write_library(collection: bpy.types.Collection) -> None:
    LIBRARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if LIBRARY_PATH.exists():
        LIBRARY_PATH.unlink()
    bpy.data.libraries.write(
        str(LIBRARY_PATH),
        {collection},
        path_remap="RELATIVE_ALL",
        fake_user=True,
        compress=True,
    )


def main() -> None:
    collection = build_furniture()
    # Write before preview parenting so the library remains independent and
    # contains no dependency on the house root or house geometry.
    write_library(collection)
    hide_blockout_furniture()
    parent_preview_to_house(collection)
    cameras = setup_preview()
    render_previews(cameras)
    print(f"Furniture library: {LIBRARY_PATH}")
    print(f"Preview directory: {QA_DIR}")
    print(f"Detailed collection objects: {len(collection.objects)}")


if __name__ == "__main__":
    main()
