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
PBR_DIR = ROOT / "assets" / "third-party" / "polyhaven"

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


def pbr_material(
    name: str,
    asset_name: str,
    *,
    mapping_scale: tuple[float, float, float],
    normal_strength: float,
    saturation: float = 1.0,
    value: float = 1.0,
) -> bpy.types.Material | None:
    """Load a compact, local CC0 Poly Haven material with box projection."""
    asset_dir = PBR_DIR / asset_name
    diffuse_path = asset_dir / f"{asset_name}_diff_1k.jpg"
    roughness_path = asset_dir / f"{asset_name}_rough_1k.jpg"
    normal_path = asset_dir / f"{asset_name}_nor_gl_1k.jpg"
    if not all(path.exists() for path in (diffuse_path, roughness_path, normal_path)):
        return None

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    for node in list(nodes):
        nodes.remove(node)

    output = nodes.new("ShaderNodeOutputMaterial")
    principled = nodes.new("ShaderNodeBsdfPrincipled")
    principled.inputs["Metallic"].default_value = 0.0
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])

    texcoord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = mapping_scale
    links.new(texcoord.outputs["Generated"], mapping.inputs["Vector"])

    def image_node(path: Path, *, non_color: bool) -> bpy.types.Node:
        node = nodes.new("ShaderNodeTexImage")
        node.image = bpy.data.images.load(str(path), check_existing=True)
        if non_color:
            node.image.colorspace_settings.name = "Non-Color"
        node.projection = "BOX"
        node.projection_blend = 0.22
        node.extension = "REPEAT"
        links.new(mapping.outputs["Vector"], node.inputs["Vector"])
        return node

    diffuse = image_node(diffuse_path, non_color=False)
    roughness = image_node(roughness_path, non_color=True)
    normal = image_node(normal_path, non_color=True)
    normal_map = nodes.new("ShaderNodeNormalMap")
    normal_map.inputs["Strength"].default_value = normal_strength
    grade = nodes.new("ShaderNodeHueSaturation")
    grade.inputs["Saturation"].default_value = saturation
    grade.inputs["Value"].default_value = value
    links.new(diffuse.outputs["Color"], grade.inputs["Color"])
    links.new(grade.outputs["Color"], principled.inputs["Base Color"])
    links.new(roughness.outputs["Color"], principled.inputs["Roughness"])
    links.new(normal.outputs["Color"], normal_map.inputs["Color"])
    links.new(normal_map.outputs["Normal"], principled.inputs["Normal"])
    return mat


def concrete_material() -> bpy.types.Material:
    mat = material("Architectural concrete", (0.43, 0.42, 0.40, 1), roughness=0.82)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    principled = nodes.get("Principled BSDF")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 13.0
    noise.inputs["Detail"].default_value = 8.0
    noise.inputs["Roughness"].default_value = 0.72
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.16
    bump.inputs["Distance"].default_value = 0.045
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.22
    ramp.color_ramp.elements[0].color = (0.20, 0.195, 0.185, 1)
    ramp.color_ramp.elements[1].position = 0.82
    ramp.color_ramp.elements[1].color = (0.49, 0.475, 0.445, 1)
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], principled.inputs["Base Color"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    return mat


def wood_material() -> bpy.types.Material:
    mat = material("Natural oak", (0.34, 0.16, 0.055, 1), roughness=0.55)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    principled = nodes.get("Principled BSDF")
    tex = nodes.new("ShaderNodeTexWave")
    tex.wave_type = "BANDS"
    tex.bands_direction = "X"
    tex.inputs["Scale"].default_value = 7.0
    tex.inputs["Distortion"].default_value = 7.5
    tex.inputs["Detail"].default_value = 5.0
    tex.inputs["Detail Scale"].default_value = 1.8
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.075, 0.024, 0.006, 1)
    ramp.color_ramp.elements[1].color = (0.45, 0.19, 0.045, 1)
    links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], principled.inputs["Base Color"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.10
    bump.inputs["Distance"].default_value = 0.018
    links.new(tex.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    return mat


def plaster_material() -> bpy.types.Material:
    mat = material("Fine mineral plaster", (0.93, 0.92, 0.89, 1), roughness=0.72)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    principled = nodes.get("Principled BSDF")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 110.0
    noise.inputs["Detail"].default_value = 3.0
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.035
    bump.inputs["Distance"].default_value = 0.008
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    return mat


def textile_material(
    name: str,
    color: tuple[float, float, float, float],
    *,
    roughness: float = 0.94,
) -> bpy.types.Material:
    """Fine woven material that stays subtle at full-house render scale."""
    mat = material(name, color, roughness=roughness)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    principled = nodes.get("Principled BSDF")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 165.0
    noise.inputs["Detail"].default_value = 2.2
    noise.inputs["Roughness"].default_value = 0.55
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.075
    bump.inputs["Distance"].default_value = 0.006
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    return mat


def roof_tile_material() -> bpy.types.Material:
    mat = material("Anthracite clay tiles", (0.018, 0.021, 0.024, 1), roughness=0.64)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    principled = nodes.get("Principled BSDF")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 42.0
    noise.inputs["Detail"].default_value = 4.0
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.08
    bump.inputs["Distance"].default_value = 0.012
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
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


def add_cone(
    name: str,
    location: tuple[float, float, float],
    radius_top: float,
    radius_bottom: float,
    depth: float,
    mat: bpy.types.Material,
    *,
    vertices: int = 32,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius_bottom,
        radius2=radius_top,
        depth=depth,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    apply_material(obj, mat)
    bevel = obj.modifiers.new("Finished shade edges", "BEVEL")
    bevel.width = 0.018
    bevel.segments = 2
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
    half_width = 4.56
    base_z = 6.05
    ridge_z = 7.85
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


def add_roof_tile_source(
    name: str,
    location: tuple[float, float, float],
    rotation: tuple[float, float, float],
    mat: bpy.types.Material,
    parent: bpy.types.Object,
) -> bpy.types.Object:
    """Create one interlocking clay tile with a curved cross-section.

    The roof slope runs along local X, while local Y follows the ridge.  The
    previous source crowned the tile in the slope direction and produced long
    corrugated strips.  This profile exposes individual overlapping units.
    """
    run = 0.36
    width = 0.29
    thickness = 0.026
    x_positions = (-run / 2, -run / 6, run / 6, run / 2)
    y_positions = (-width / 2, -width / 4, 0.0, width / 4, width / 2)
    vertices: list[tuple[float, float, float]] = []
    for z_offset in (0.0, -thickness):
        for x in x_positions:
            # A slightly heavier downhill nose creates the overlapping course
            # shadow that is visible on real anthracite interlocking tiles.
            nose = 0.012 * max(0.0, (x_positions[1] - x) / run)
            for y in y_positions:
                crown = 0.026 * (1.0 - (y / (width / 2)) ** 2)
                vertices.append((x, y, crown + nose + z_offset))

    columns = len(y_positions)
    top_count = len(x_positions) * columns
    faces: list[tuple[int, int, int, int]] = []
    for x_index in range(len(x_positions) - 1):
        for y_index in range(columns - 1):
            a = x_index * columns + y_index
            faces.append((a, a + columns, a + columns + 1, a + 1))
            b = top_count + a
            faces.append((b + 1, b + columns + 1, b + columns, b))
    for x_index in range(len(x_positions) - 1):
        a = x_index * columns
        b = top_count + a
        faces.append((a, b, b + columns, a + columns))
        a += columns - 1
        b += columns - 1
        faces.append((a + columns, b + columns, b, a))
    for y_index in range(columns - 1):
        a = y_index
        b = top_count + a
        faces.append((a + 1, b + 1, b, a))
        a = (len(x_positions) - 1) * columns + y_index
        b = top_count + a
        faces.append((a, b, b + 1, a + 1))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation
    obj.parent = parent
    apply_material(obj, mat)
    bevel = obj.modifiers.new("Tile edge radius", "BEVEL")
    bevel.width = 0.008
    bevel.segments = 2
    return obj


def add_roof_system(
    parent: bpy.types.Object,
    tile_mat: bpy.types.Material,
    underlay_mat: bpy.types.Material,
    timber_mat: bpy.types.Material,
    metal_mat: bpy.types.Material,
) -> None:
    """Build a physically legible roof instead of two featureless slabs."""
    angle = math.radians(21.5)
    ridge_z = 7.85
    slope_length = 4.98
    roof_depth = 8.45
    tile_source: bpy.types.Object | None = None
    seam_vertices: list[tuple[float, float, float]] = []
    seam_faces: list[tuple[int, int, int, int]] = []

    for side in (-1, 1):
        x_center = side * 2.62
        rotation_y = side * angle
        add_box(
            f"Roof membrane {side}",
            (x_center * 0.91, 0.16, 7.02),
            (slope_length, roof_depth, 0.10),
            underlay_mat,
            rotation=(0, rotation_y, 0),
            bevel=0.018,
            parent=parent,
        )
        add_box(
            f"Timber soffit {side}",
            (side * 2.31, 0.16, 6.91),
            (5.05, 8.46, 0.10),
            timber_mat,
            rotation=(0, rotation_y, 0),
            bevel=0.018,
            parent=parent,
        )

        # Exposed rafters are visible under the eaves and in the lifted state.
        for y in [(-3.98 + index * 0.61) for index in range(14)]:
            add_box(
                f"Exposed rafter {side} {y:.2f}",
                (side * 2.31, y, 6.82),
                (4.86, 0.13, 0.22),
                timber_mat,
                rotation=(0, rotation_y, 0),
                bevel=0.018,
                parent=parent,
            )

        # Individual overlapping tiles create the crisp scale/detail of the mockup.
        for slope_index in range(16):
            x = side * (0.20 + slope_index * 0.295)
            z = ridge_z - abs(x) * math.tan(angle) + 0.135 + slope_index * 0.004
            for depth_index in range(28):
                y = -4.08 + depth_index * 0.300 + (0.145 if slope_index % 2 else 0)
                if tile_source is None:
                    tile_source = add_roof_tile_source(
                        "Roof tile source",
                        (x, y, z),
                        (0, rotation_y, 0),
                        tile_mat,
                        parent,
                    )
                else:
                    tile = tile_source.copy()
                    tile.data = tile_source.data
                    tile.name = f"Roof tile {side} {slope_index} {depth_index}"
                    tile.location = (x, y, z)
                    tile.rotation_euler = (0, rotation_y, 0)
                    tile.parent = parent
                    bpy.context.collection.objects.link(tile)

        # Continuous course shadows plus staggered short joints give the roof
        # the two-directional tile rhythm visible in the architectural reference.
        for course_index in range(1, 16):
            course_x = side * (0.20 + (course_index - 0.5) * 0.295)
            course_z = ridge_z - abs(course_x) * math.tan(angle) + 0.178 + course_index * 0.004
            add_box(
                f"Roof course shadow {side} {course_index}",
                (course_x, 0.02, course_z),
                (0.024, 8.20, 0.012),
                underlay_mat,
                rotation=(0, rotation_y, 0),
                bevel=0.003,
                parent=parent,
            )

        # Short staggered joints break the remaining long-strip appearance.
        # They are combined into one mesh so this detail does not multiply the
        # object count or materially slow the render.
        for slope_index in range(1, 16):
            boundary_x = side * (0.20 + (slope_index - 0.5) * 0.295)
            for depth_index in range(28):
                if (slope_index + depth_index) % 2:
                    continue
                y = -4.05 + depth_index * 0.295
                half_x = 0.010
                half_y = 0.092
                start = len(seam_vertices)
                for x_pos, y_pos in (
                    (boundary_x - half_x, y - half_y),
                    (boundary_x + half_x, y - half_y),
                    (boundary_x + half_x, y + half_y),
                    (boundary_x - half_x, y + half_y),
                ):
                    seam_z = ridge_z - abs(x_pos) * math.tan(angle) + 0.172
                    seam_vertices.append((x_pos, y_pos, seam_z))
                seam_faces.append((start, start + 1, start + 2, start + 3))

        eave_x = side * 4.72
        add_box(
            f"Timber fascia {side}",
            (eave_x, 0.16, 6.08),
            (0.14, 8.38, 0.23),
            timber_mat,
            bevel=0.025,
            parent=parent,
        )
        add_cylinder(
            f"Gutter {side}",
            (side * 4.82, 0.16, 5.98),
            0.105,
            8.58,
            metal_mat,
            rotation=(math.pi / 2, 0, 0),
            parent=parent,
        )

    # Rounded ridge tiles visually finish the roof silhouette.
    for depth_index in range(25):
        y = -4.13 + depth_index * 0.345
        add_cylinder(
            f"Ridge cap {depth_index}",
            (0, y, 7.92),
            0.145,
            0.36,
            tile_mat,
            rotation=(math.pi / 2, 0, 0),
            vertices=24,
            parent=parent,
        )

    seam_mesh = bpy.data.meshes.new("Roof tile staggered joints")
    seam_mesh.from_pydata(seam_vertices, [], seam_faces)
    seam_mesh.update()
    seam_object = bpy.data.objects.new("Roof tile staggered joints", seam_mesh)
    bpy.context.collection.objects.link(seam_object)
    seam_object.parent = parent
    apply_material(seam_object, underlay_mat)


def add_floorboards(
    name: str,
    z: float,
    mat: bpy.types.Material,
) -> None:
    for index in range(22):
        y = -3.55 + index * 0.33
        add_box(
            f"{name} board {index}",
            (0, y, z),
            (9.30, 0.315, 0.055),
            mat,
            bevel=0.008,
        )


def add_dining_chair(
    name: str,
    location: tuple[float, float, float],
    wood: bpy.types.Material,
    dark: bpy.types.Material,
) -> None:
    x, y, z = location
    add_box(f"{name} seat", (x, y, z + 0.43), (0.42, 0.42, 0.075), wood, bevel=0.038)
    for dx in (-0.165, 0.165):
        add_cylinder(f"{name} back post", (x + dx, y + 0.18, z + 0.73), 0.016, 0.62, dark, vertices=16)
    add_box(
        f"{name} back shell",
        (x, y + 0.19, z + 0.80),
        (0.35, 0.055, 0.34),
        wood,
        rotation=(math.radians(-4), 0, 0),
        bevel=0.055,
    )
    for dx in (-0.155, 0.155):
        for dy in (-0.15, 0.15):
            add_cylinder(f"{name} leg", (x + dx, y + dy, z + 0.215), 0.018, 0.43, dark, vertices=16)


def add_uv_sphere(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    mat: bpy.types.Material,
    *,
    segments: int = 24,
    rings: int = 16,
    rotation: tuple[float, float, float] = (0, 0, 0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=rings,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    apply_material(obj, mat)
    return obj


def add_soft_quilt(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float],
    mat: bpy.types.Material,
) -> bpy.types.Object:
    """Create a lightly folded textile surface instead of a rounded box."""
    width, depth = dimensions
    x_segments = 14
    y_segments = 18
    vertices: list[tuple[float, float, float]] = []
    for y_index in range(y_segments + 1):
        y_ratio = y_index / y_segments
        y = -depth / 2 + depth * y_ratio
        for x_index in range(x_segments + 1):
            x_ratio = x_index / x_segments
            x = -width / 2 + width * x_ratio
            # The folds stay deliberately shallow.  Large procedural waves read
            # like foam at architectural scale; a thin drape with pronounced
            # edge falloff catches the light much more like real bed linen.
            fold = 0.014 * math.sin(x_ratio * math.pi * 5.0 + y_ratio * 1.4)
            fold += 0.006 * math.cos(y_ratio * math.pi * 4.0)
            edge_amount = max(0.0, (abs(x_ratio - 0.5) - 0.44) / 0.06)
            edge_drop = 0.08 * edge_amount * edge_amount * (3.0 - 2.0 * edge_amount)
            foot_amount = max(0.0, (0.25 - y_ratio) / 0.25)
            foot_drop = 0.18 * foot_amount * foot_amount * (3.0 - 2.0 * foot_amount)
            vertices.append((x, y, fold - max(edge_drop, foot_drop)))
    faces: list[tuple[int, int, int, int]] = []
    row = x_segments + 1
    for y_index in range(y_segments):
        for x_index in range(x_segments):
            a = y_index * row + x_index
            faces.append((a, a + 1, a + row + 1, a + row))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    apply_material(obj, mat)
    solidify = obj.modifiers.new("Textile thickness", "SOLIDIFY")
    solidify.thickness = 0.026
    subdivision = obj.modifiers.new("Textile softness", "SUBSURF")
    subdivision.levels = 1
    subdivision.render_levels = 2
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()
    obj.select_set(False)
    return obj


def add_plant(
    name: str,
    location: tuple[float, float, float],
    ceramic: bpy.types.Material,
    leaf: bpy.types.Material,
    stem: bpy.types.Material,
    *,
    scale: float = 1.0,
) -> None:
    x, y, z = location
    add_cone(f"{name} planter", (x, y, z + 0.23 * scale), 0.20 * scale, 0.28 * scale, 0.46 * scale, ceramic, vertices=32)
    for index, angle in enumerate((-1.15, -0.72, -0.3, 0.15, 0.55, 0.95, 1.35)):
        height = (0.62 + (index % 3) * 0.14) * scale
        dx = math.cos(angle) * 0.17 * scale
        dy = math.sin(angle) * 0.17 * scale
        add_curve(
            f"{name} stem {index}",
            [(x, y, z + 0.42 * scale), (x + dx * 0.45, y + dy * 0.45, z + height * 0.72), (x + dx, y + dy, z + height)],
            stem,
            bevel_depth=0.012 * scale,
        )
        add_uv_sphere(
            f"{name} leaf {index}",
            (x + dx, y + dy, z + height),
            (0.08 * scale, 0.23 * scale, 0.055 * scale),
            leaf,
            segments=18,
            rings=12,
            rotation=(angle * 0.15, angle, angle),
        )


def add_recessed_light(
    name: str,
    location: tuple[float, float, float],
    trim: bpy.types.Material,
    glow: bpy.types.Material,
) -> None:
    add_cylinder(f"{name} trim", location, 0.105, 0.055, trim, vertices=24)
    add_cylinder(f"{name} lens", (location[0], location[1], location[2] - 0.031), 0.072, 0.018, glow, vertices=24)


def build_scene() -> None:
    clear_scene()

    white = plaster_material()
    interior_white = material("Interior warm white", (0.86, 0.84, 0.79, 1), roughness=0.72)
    warm_greige = material("Warm greige wall", (0.43, 0.40, 0.36, 1), roughness=0.82)
    concrete = pbr_material(
        "Architectural concrete PBR",
        "concrete_wall_009",
        mapping_scale=(1.6, 1.6, 1.6),
        normal_strength=0.38,
        saturation=0.12,
        value=1.10,
    ) or concrete_material()
    wood = pbr_material(
        "Natural oak PBR",
        "oak_veneer_01",
        mapping_scale=(1.25, 2.8, 1.25),
        normal_strength=0.24,
        saturation=0.58,
        value=1.08,
    ) or wood_material()
    dark = material("Charcoal powder coat", (0.018, 0.022, 0.025, 1), roughness=0.34, metallic=0.10)
    cable_blue = material("Installation cable blue", (0.015, 0.10, 0.30, 1), roughness=0.42)
    cable_green = material("Installation cable green yellow", (0.32, 0.48, 0.045, 1), roughness=0.44)
    roof_mat = pbr_material(
        "Anthracite roof PBR",
        "grey_roof_01",
        mapping_scale=(1.8, 2.6, 1.8),
        normal_strength=0.30,
        saturation=0.45,
        value=0.92,
    ) or roof_tile_material()
    roof_underlay = material("Roof underlay", (0.012, 0.015, 0.018, 1), roughness=0.72)
    glass = material("Architectural glass", (0.95, 0.98, 1.0, 1), roughness=0.03, metallic=0.0, transmission=1.0)
    glass_principled = glass.node_tree.nodes.get("Principled BSDF")
    if "IOR" in glass_principled.inputs:
        glass_principled.inputs["IOR"].default_value = 1.45
    red = material("Hubmann red", (0.78, 0.002, 0.008, 1), roughness=0.35)
    pv = material("Photovoltaic cells", (0.006, 0.007, 0.009, 1), roughness=0.46, metallic=0.46)
    floor_mat = wood
    construction_wood = wood
    warm_light = material(
        "Warm light surface",
        (0.95, 0.78, 0.48, 1),
        roughness=0.35,
        emission=(1.0, 0.54, 0.20, 1),
        emission_strength=3.0,
    )
    fabric = textile_material("Warm woven fabric", (0.49, 0.46, 0.41, 1))
    linen = textile_material("Natural linen", (0.77, 0.72, 0.64, 1), roughness=0.96)
    bedding = textile_material("Soft white bedding", (0.88, 0.86, 0.82, 1), roughness=0.98)
    ceramic = material("Warm ceramic", (0.89, 0.86, 0.80, 1), roughness=0.32)
    mirror = material("Mirror", (0.12, 0.13, 0.14, 1), roughness=0.08, metallic=1.0)
    stone_tile = pbr_material(
        "Bathroom stone PBR",
        "concrete_wall_009",
        mapping_scale=(3.2, 3.2, 3.2),
        normal_strength=0.10,
        saturation=0.08,
        value=0.58,
    ) or material("Bathroom stone", (0.20, 0.19, 0.175, 1), roughness=0.72)
    concrete_recess = material("Concrete formwork recess", (0.18, 0.18, 0.17, 1), roughness=0.88)
    leaf = material("Muted foliage", (0.055, 0.16, 0.07, 1), roughness=0.82)
    earth = material("Dark plant stems", (0.05, 0.025, 0.012, 1), roughness=0.85)
    landscape = material("Soft exterior foliage", (0.22, 0.31, 0.18, 1), roughness=0.95)
    landscape_nodes = landscape.node_tree.nodes
    landscape_links = landscape.node_tree.links
    landscape_noise = landscape_nodes.new("ShaderNodeTexNoise")
    landscape_noise.inputs["Scale"].default_value = 11.0
    landscape_noise.inputs["Detail"].default_value = 8.0
    landscape_noise.inputs["Roughness"].default_value = 0.78
    landscape_ramp = landscape_nodes.new("ShaderNodeValToRGB")
    landscape_ramp.color_ramp.elements[0].position = 0.32
    landscape_ramp.color_ramp.elements[0].color = (0.012, 0.038, 0.010, 1)
    landscape_ramp.color_ramp.elements[1].position = 0.64
    landscape_ramp.color_ramp.elements[1].color = (0.19, 0.27, 0.12, 1)
    landscape_links.new(landscape_noise.outputs["Fac"], landscape_ramp.inputs["Fac"])
    landscape_principled = landscape_nodes.get("Principled BSDF")
    landscape_links.new(landscape_ramp.outputs["Color"], landscape_principled.inputs["Base Color"])
    landscape_principled.inputs["Emission Color"].default_value = (0.10, 0.22, 0.07, 1)
    landscape_principled.inputs["Emission Strength"].default_value = 0.025

    facade_front = empty("ANIM Front facade")
    facade_side = empty("ANIM Right facade")
    static_cutaway_shell = empty("STATIC Cutaway shell")
    roof_group = empty("ANIM Roof")
    pv_group = empty("ANIM Photovoltaic")
    technical_group = empty("ANIM Energy equipment")
    exploded_panels = empty("STATIC Exploded facade panels")
    bathroom_group = empty("STATIC Bathroom fit-out")
    bathroom_group.location = (-0.60, -0.40, 0.0)
    cutaway_window_group = empty("STATIC Cutaway windows")

    add_box("Exploded left wall panel", (-6.35, -3.10, 6.35), (0.24, 1.28, 2.05), concrete, bevel=0.025, parent=exploded_panels)
    add_box("Exploded right wall panel", (6.55, 1.15, 6.20), (0.24, 1.55, 2.12), white, bevel=0.025, parent=exploded_panels)

    # Foundation, slabs and exposed concrete frame.
    add_box("Foundation", (0, 0, -0.22), (10.9, 8.9, 0.44), concrete, bevel=0.030)
    add_box("Ground floor slab", (0, 0, 0.09), (10.35, 8.35, 0.18), concrete, bevel=0.020)
    add_box("Upper floor slab", (0, -0.12, 3.25), (10.65, 8.6, 0.26), concrete, bevel=0.022)
    add_box("Upper ceiling slab", (0, 0.02, 5.92), (10.25, 8.20, 0.24), concrete, bevel=0.024)
    add_box("Front balcony", (0, -4.45, 3.25), (10.65, 1.25, 0.22), concrete, bevel=0.022)
    add_box("Terrace", (-0.4, -4.55, 0.12), (9.8, 1.35, 0.18), concrete, bevel=0.020)
    add_box("Entrance step lower", (-0.75, -5.38, -0.34), (4.15, 0.58, 0.18), concrete, bevel=0.022)
    add_box("Entrance step middle", (-0.75, -5.16, -0.17), (3.97, 0.58, 0.18), concrete, bevel=0.022)
    add_box("Entrance step upper", (-0.75, -4.94, 0.00), (3.79, 0.58, 0.18), concrete, bevel=0.022)
    for x in (-4.82, 4.82):
        add_box("Concrete column", (x, -4.45, 1.7), (0.38, 0.38, 3.15), concrete, bevel=0.030)
        add_box("Concrete column upper", (x, -4.45, 4.55), (0.36, 0.36, 2.4), concrete, bevel=0.030)
    # The service cabinet has its own structural reveals below.  A second pier
    # in front of it made the installation look pasted behind a column.  The
    # upper storey instead gets a slim service chase at the bathroom edge.
    add_box("Upper service chase", (1.72, -3.05, 4.58), (0.22, 0.38, 2.36), interior_white, bevel=0.022)

    # Subtle formwork joints and tie holes keep the exposed concrete legible at
    # the final website resolution without turning it into a noisy texture.
    for x in (-3.55, -1.78, 0.0, 1.78, 3.55):
        add_box("Upper slab formwork joint", (x, -4.435, 3.25), (0.018, 0.018, 0.25), concrete_recess, bevel=0.003)
        add_box("Ceiling slab formwork joint", (x, -4.095, 5.92), (0.018, 0.018, 0.20), concrete_recess, bevel=0.003)
    for column_x in (-4.82, 4.82):
        for z in (0.95, 1.72, 2.49, 4.15, 4.92):
            y = -4.69 if abs(column_x) > 1 else -3.91
            add_cylinder(
                "Concrete tie hole",
                (column_x, y, z),
                0.032,
                0.018,
                concrete_recess,
                rotation=(math.pi / 2, 0, 0),
                vertices=20,
            )

    # Static left and rear envelope.
    add_box("Left wall ground", (-4.88, 0, 1.67), (0.28, 7.75, 2.92), white, parent=static_cutaway_shell)
    add_box("Left wall upper", (-4.88, 0, 4.55), (0.28, 7.75, 2.4), white, parent=static_cutaway_shell)
    add_box("Rear wall ground", (0, 3.88, 1.67), (9.55, 0.28, 2.92), white)
    add_box("Rear wall upper", (0, 3.88, 4.55), (9.55, 0.28, 2.4), white)
    add_gable("Rear gable", 3.88, white, parent=facade_side)

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

    # Detailed tile roof, rafters, ridge and gutters.
    roof_angle = math.radians(21.5)
    add_roof_system(roof_group, roof_mat, roof_underlay, construction_wood, dark)
    add_cylinder("Downpipe", (5.27, 3.45, 2.82), 0.07, 5.8, dark, parent=facade_side)

    # Interior architecture and furniture, visible after the facade opens.
    add_box("Ground floor finish", (0, 0, 0.24), (9.4, 7.4, 0.10), floor_mat, bevel=0.018)
    add_box("Upper floor finish", (0, 0, 3.43), (9.4, 7.4, 0.10), floor_mat, bevel=0.018)
    add_floorboards("Ground floor", 0.315, floor_mat)
    add_floorboards("Upper floor", 3.505, floor_mat)
    add_box("Kitchen wall", (2.75, 3.05, 1.72), (3.8, 0.16, 2.8), interior_white, bevel=0.025)
    add_box("Ground corridor wall left", (-1.58, 2.72, 1.72), (0.48, 0.16, 2.82), interior_white, bevel=0.018)
    add_box("Ground corridor wall right", (0.10, 2.72, 1.72), (0.64, 0.16, 2.82), interior_white, bevel=0.018)
    add_box("Ground corridor lintel", (-0.65, 2.72, 2.94), (1.30, 0.16, 0.32), interior_white, bevel=0.018)
    # Camera-facing room shells are deliberately deeper than decorative wall
    # planes.  They keep the cutaway readable as architecture instead of a
    # collection of furniture floating on two slabs.
    add_box("Bedroom rear lining", (-3.40, 1.72, 4.69), (2.65, 0.12, 2.38), warm_greige, bevel=0.018)
    add_box("Bedroom partition", (-2.05, 2.62, 4.69), (0.18, 2.05, 2.40), interior_white, bevel=0.022)
    add_box("Bedroom partition cut face", (-2.05, 1.53, 4.69), (0.24, 0.20, 2.40), interior_white, bevel=0.022)
    add_box("Upper corridor wall left", (-1.99, 2.74, 4.69), (0.36, 0.16, 2.40), interior_white, bevel=0.018)
    add_box("Upper corridor wall right", (-0.71, 2.74, 4.69), (0.48, 0.16, 2.40), interior_white, bevel=0.018)
    add_box("Upper corridor lintel", (-1.35, 2.74, 5.74), (0.92, 0.16, 0.30), interior_white, bevel=0.018)
    add_box("Bathroom side partition", (1.70, 3.08, 4.69), (0.18, 0.62, 2.40), interior_white, bevel=0.022)
    add_box("Bathroom side cut face", (1.70, 2.72, 4.69), (0.22, 0.16, 2.40), interior_white, bevel=0.022)
    add_box("Bathroom feature wall", (1.02, 2.50, 4.69), (2.18, 0.12, 2.38), stone_tile, bevel=0.018, parent=bathroom_group)
    for x in (0.30, 1.02, 1.74):
        add_box("Bathroom vertical tile joint", (x, 2.435, 4.69), (0.005, 0.006, 2.24), ceramic, bevel=0.001, parent=bathroom_group)
    for z in (4.10, 4.69, 5.28):
        add_box("Bathroom horizontal tile joint", (1.02, 2.435, z), (2.06, 0.006, 0.005), ceramic, bevel=0.001, parent=bathroom_group)
    add_box("Gallery rear lining", (3.62, 3.68, 4.69), (2.18, 0.10, 2.38), interior_white, bevel=0.018)
    add_box("Gallery return wall", (3.12, 2.30, 4.69), (0.15, 2.38, 2.40), interior_white, bevel=0.025)
    for index in range(10):
        add_box(
            "Gallery interior timber slat",
            (3.45 + index * 0.15, 3.57, 4.70),
            (0.075, 0.10, 2.16),
            wood,
            bevel=0.012,
        )
    add_side_window("Gallery cutaway", 0.35, 4.72, 1.35, 1.86, glass, dark, cutaway_window_group)

    # Recesses, shadow gaps and service penetrations are small details in
    # geometry, but they create the high-frequency edge information visible in
    # the reference render.
    for x in (-4.35, -3.65, -2.95, -2.25):
        add_box("Bedroom ceiling shadow gap", (x, 3.57, 5.93), (0.50, 0.025, 0.025), dark, bevel=0.003)
    for x in (0.28, 0.77, 1.26, 1.75):
        add_box("Bathroom ceiling shadow gap", (x, 2.57, 5.93), (0.38, 0.025, 0.025), dark, bevel=0.003)
    add_cylinder("Upper service junction", (1.62, 0.78, 5.50), 0.14, 0.08, dark, rotation=(math.pi / 2, 0, 0), vertices=32)
    add_cylinder("Upper service indicator", (1.62, 0.73, 5.50), 0.055, 0.025, red, rotation=(math.pi / 2, 0, 0), vertices=24)

    # A muted exterior glimpse gives the living room depth without competing
    # with the white architectural presentation.
    add_box("Living rear window view", (-3.72, 3.70, 1.72), (1.62, 0.035, 2.28), landscape, bevel=0.012)
    for x in (-4.56, -2.88):
        add_box("Living rear window jamb", (x, 3.64, 1.72), (0.11, 0.10, 2.42), dark, bevel=0.010)
    for z in (0.53, 2.91):
        add_box("Living rear window frame", (-3.72, 3.64, z), (1.78, 0.10, 0.11), dark, bevel=0.010)
    add_box("Living side window view", (-4.72, -0.45, 1.72), (0.035, 1.72, 2.28), landscape, bevel=0.012)
    for y in (-1.36, 0.46):
        add_box("Living side window jamb", (-4.66, y, 1.72), (0.10, 0.11, 2.42), dark, bevel=0.010)
    for z in (0.53, 2.91):
        add_box("Living side window frame", (-4.66, -0.45, z), (0.10, 1.88, 0.11), dark, bevel=0.010)

    # A restrained glass gallery edge replaces the toy-like fully open upper floor.
    add_box("Gallery glass", (3.88, 0.05, 4.34), (1.62, 0.025, 0.78), glass, bevel=0.008)
    add_box("Gallery rail", (3.88, 0.01, 4.75), (1.68, 0.035, 0.035), dark, bevel=0.008)
    for x in (3.10, 3.62, 4.14, 4.66):
        add_box("Gallery post", (x, 0.01, 4.36), (0.028, 0.045, 0.82), dark, bevel=0.005)
    add_box("Gallery console", (4.05, 2.42, 3.94), (1.30, 0.38, 0.42), wood, bevel=0.035)
    add_box("Gallery console shadow", (4.05, 2.20, 3.94), (1.12, 0.018, 0.025), dark, bevel=0.004)
    add_plant("Gallery plant", (4.46, 2.32, 3.56), ceramic, leaf, earth, scale=0.40)

    # The wall build-up is visible in the cut edges, as in the reference render.
    for x in (-4.70, 4.70):
        add_box("Cut edge insulation", (x, -3.72, 1.70), (0.16, 0.24, 2.86), linen, bevel=0.008)
        add_box("Cut edge insulation upper", (x, -3.72, 4.62), (0.16, 0.24, 2.30), linen, bevel=0.008)

    # Fine shadow gaps and skirting make the rooms read as built architecture.
    for z in (0.43, 3.62):
        add_box("Front floor shadow gap", (0, -3.53, z), (9.25, 0.025, 0.024), interior_white, bevel=0.004)
        add_box("Rear skirting", (0, 3.55, z), (9.25, 0.045, 0.10), interior_white, bevel=0.008)
    for x in (-4.55, 4.55):
        add_box("Side skirting", (x, 0, 0.43), (0.045, 7.1, 0.10), interior_white, bevel=0.008)

    # Staircase.
    for step in range(13):
        add_box(
            "Oak stair",
            (-0.20, 1.95 - step * 0.25, 0.38 + step * 0.22),
            (1.65, 0.34, 0.16),
            floor_mat,
            bevel=0.025,
        )
    add_curve("Stair handrail", [(0.68, 2.1, 0.78), (0.68, -1.15, 3.55)], dark, bevel_depth=0.028)
    add_curve("Stair oak stringer left", [(-1.02, 2.12, 0.25), (-1.02, -1.18, 3.18)], wood, bevel_depth=0.075, smooth=False)
    add_curve("Stair oak stringer right", [(0.62, 2.12, 0.25), (0.62, -1.18, 3.18)], wood, bevel_depth=0.075, smooth=False)
    add_box("Stair glass balustrade", (0.64, 0.42, 2.02), (0.045, 3.18, 1.08), glass, rotation=(math.radians(-42), 0, 0), bevel=0.012)
    add_box("Stair upper landing", (-0.20, -1.37, 3.10), (1.76, 0.82, 0.16), floor_mat, bevel=0.025)
    add_plant("Stair plant", (-1.25, 1.70, 0.36), ceramic, leaf, earth, scale=0.80)

    # Minimal furniture and kitchen for scale.
    add_box("Kitchen base", (2.65, 2.62, 0.78), (3.55, 0.65, 1.02), wood, bevel=0.035)
    add_box("Kitchen worktop", (2.65, 2.54, 1.34), (3.65, 0.78, 0.10), dark, bevel=0.025)
    add_box("Kitchen wall units", (3.25, 2.82, 2.22), (2.35, 0.46, 0.82), wood, bevel=0.035)
    add_box("Tall kitchen unit", (4.05, 2.70, 1.72), (0.82, 0.58, 2.70), wood, bevel=0.035)
    add_box("Built-in oven", (4.05, 2.37, 1.65), (0.62, 0.045, 0.72), dark, bevel=0.025)
    add_box("Sofa seat", (-2.55, -1.50, 0.63), (2.65, 0.98, 0.34), fabric, bevel=0.14)
    add_box("Sofa back", (-2.55, -1.10, 1.05), (2.65, 0.24, 0.72), fabric, bevel=0.12)
    for x in (-3.18, -2.55, -1.92):
        add_box("Sofa cushion", (x, -1.60, 0.84), (0.56, 0.68, 0.20), fabric, bevel=0.13)
    for x in (-3.77, -1.33):
        add_box("Sofa arm", (x, -1.50, 0.82), (0.22, 0.98, 0.56), fabric, bevel=0.12)
    add_box("Sofa cushion linen", (-3.12, -1.18, 1.20), (0.48, 0.15, 0.46), linen, rotation=(math.radians(4), 0, math.radians(-7)), bevel=0.11)
    add_box("Sofa cushion accent", (-2.28, -1.18, 1.17), (0.42, 0.15, 0.42), fabric, rotation=(math.radians(4), 0, math.radians(6)), bevel=0.10)
    add_box("Living rug", (-2.55, -2.25, 0.39), (3.45, 2.30, 0.035), linen, bevel=0.03)
    add_box("Lounge chair seat", (-4.05, -2.70, 0.70), (0.88, 0.76, 0.22), linen, rotation=(0, 0, math.radians(-12)), bevel=0.12)
    add_box("Lounge chair back", (-4.05, -2.45, 1.08), (0.88, 0.20, 0.72), linen, rotation=(math.radians(-10), 0, math.radians(-12)), bevel=0.12)
    add_box("Coffee table top", (-2.55, -2.85, 0.62), (1.7, 0.74, 0.08), wood, bevel=0.035)
    for x in (-3.22, -1.88):
        for y in (-0.30, 0.20):
            add_cylinder("Coffee table leg", (x, y - 2.80, 0.42), 0.025, 0.40, dark, vertices=16)
    add_box("Media cabinet", (-1.75, 3.46, 0.76), (2.15, 0.40, 0.50), wood, bevel=0.04)
    add_box("Television", (-1.75, 3.22, 1.66), (1.72, 0.055, 1.02), dark, bevel=0.025)
    add_box("Living media pier", (-1.10, 1.55, 1.68), (0.15, 1.18, 2.72), interior_white, bevel=0.018)
    add_box("Living side television", (-1.00, 1.55, 1.76), (0.055, 0.92, 1.05), dark, bevel=0.025)
    add_box("Living side lowboard", (-0.96, 1.55, 0.72), (0.42, 1.30, 0.46), wood, bevel=0.035)
    add_plant("Living plant", (-4.12, 2.40, 0.36), ceramic, leaf, earth, scale=0.92)
    add_box("Dining table", (2.65, -0.75, 0.95), (2.15, 0.95, 0.10), wood, bevel=0.035)
    for x in (1.85, 3.45):
        for y in (-1.28, -0.52):
            add_cylinder("Table leg", (x, y, 0.52), 0.045, 0.86, dark)
    for index, (x, y) in enumerate(((1.80, -1.35), (2.65, -1.35), (3.50, -1.35), (1.80, -0.15), (2.65, -0.15), (3.50, -0.15))):
        add_dining_chair(f"Dining chair {index}", (x, y, 0.30), wood, dark)
    add_box("Upper bed base", (-3.55, 0.58, 3.66), (1.78, 1.98, 0.14), wood, bevel=0.055)
    add_box("Upper mattress", (-3.55, 0.56, 3.82), (1.70, 1.90, 0.18), fabric, bevel=0.070)
    add_soft_quilt("Upper duvet", (-3.55, 0.22, 3.99), (1.72, 1.48), bedding)
    for index, x in enumerate((-3.88, -3.22)):
        add_box(
            "Bed pillow",
            (x, 1.05, 4.01),
            (0.62, 0.34, 0.11),
            bedding,
            rotation=(math.radians(2), 0, math.radians(-4 if index == 0 else 4)),
            bevel=0.085,
        )
    add_box("Upper headboard", (-3.55, 1.57, 4.10), (1.78, 0.12, 0.56), wood, bevel=0.045)
    add_box("Bedroom rug", (-3.55, -0.02, 3.57), (2.36, 2.22, 0.035), linen, bevel=0.025)
    for x in (-4.56, -2.55):
        add_box("Bedroom nightstand", (x, 1.30, 3.80), (0.42, 0.38, 0.46), wood, bevel=0.045)
        add_box("Nightstand drawer gap", (x, 1.095, 3.86), (0.34, 0.014, 0.018), dark, bevel=0.003)
        add_cylinder("Bedroom lamp stem", (x, 1.30, 4.23), 0.018, 0.38, dark, vertices=16)
        add_cone("Bedroom lamp shade", (x, 1.30, 4.45), 0.09, 0.19, 0.23, linen, vertices=32)
    add_box("Bedroom rear art frame", (-3.55, 1.64, 5.08), (1.08, 0.055, 0.78), dark, bevel=0.018)
    add_box("Bedroom rear art", (-3.55, 1.605, 5.08), (0.94, 0.028, 0.64), ceramic, bevel=0.008)

    # Bathroom and kitchen fixtures add believable scale and material contrast.
    add_box("Bathroom floor", (1.02, 1.25, 3.54), (2.42, 2.36, 0.06), stone_tile, bevel=0.012, parent=bathroom_group)
    for x in (0.42, 1.02, 1.62):
        add_box("Bathroom floor joint", (x, 1.25, 3.575), (0.005, 2.22, 0.004), ceramic, bevel=0, parent=bathroom_group)
    for y in (0.52, 1.25, 1.98):
        add_box("Bathroom floor cross joint", (1.02, y, 3.577), (2.28, 0.005, 0.004), ceramic, bevel=0, parent=bathroom_group)
    add_box("Bathroom vanity", (1.02, 2.12, 4.02), (1.08, 0.52, 0.54), wood, bevel=0.035, parent=bathroom_group)
    add_box("Bathroom drawer shadow", (1.02, 1.848, 4.02), (0.94, 0.018, 0.018), dark, bevel=0.003, parent=bathroom_group)
    for x in (0.76, 1.28):
        add_box("Bathroom drawer split", (x, 1.837, 4.02), (0.010, 0.012, 0.45), dark, bevel=0.002, parent=bathroom_group)
    add_box("Bathroom basin", (1.02, 1.98, 4.34), (0.68, 0.40, 0.13), ceramic, bevel=0.055, parent=bathroom_group)
    add_box("Bathroom mirror backing", (1.02, 2.418, 5.04), (0.96, 0.025, 0.88), dark, bevel=0.018, parent=bathroom_group)
    for x in (0.53, 1.51):
        add_box("Bathroom mirror vertical glow", (x, 2.395, 5.04), (0.032, 0.014, 0.92), warm_light, bevel=0.010, parent=bathroom_group)
    for z in (4.59, 5.49):
        add_box("Bathroom mirror horizontal glow", (1.02, 2.395, z), (0.98, 0.014, 0.032), warm_light, bevel=0.010, parent=bathroom_group)
    add_box("Bathroom mirror face", (1.02, 2.382, 5.04), (0.86, 0.018, 0.78), mirror, bevel=0.016, parent=bathroom_group)
    add_cylinder("Bathroom tap", (1.02, 1.78, 4.53), 0.026, 0.28, dark, rotation=(math.pi / 2, 0, 0), vertices=24, parent=bathroom_group)
    add_box("Shower glass", (2.02, 1.18, 4.58), (0.035, 1.42, 1.92), glass, bevel=0.012, parent=bathroom_group)
    add_cylinder("Shower rail", (1.96, 2.38, 4.83), 0.022, 1.26, dark, vertices=24, parent=bathroom_group)
    add_cylinder("Shower head", (1.96, 2.38, 5.50), 0.12, 0.025, dark, vertices=32, parent=bathroom_group)
    add_box("Shower drain", (1.76, 0.60, 3.59), (0.42, 0.035, 0.018), dark, bevel=0.005, parent=bathroom_group)
    for rail in range(7):
        add_cylinder("Towel radiator rail", (0.35, 2.24, 4.25 + rail * 0.18), 0.018, 0.58, ceramic, rotation=(0, math.pi / 2, 0), vertices=16, parent=bathroom_group)
    for x in (0.09, 0.61):
        add_cylinder("Towel radiator upright", (x, 2.24, 4.79), 0.018, 1.32, ceramic, vertices=16, parent=bathroom_group)
    for index in range(7):
        add_box("Kitchen handle", (1.28 + index * 0.46, 2.19, 0.98), (0.28, 0.025, 0.025), dark, bevel=0.01)
    add_box("Kitchen backsplash", (2.65, 2.20, 1.78), (3.55, 0.035, 0.62), ceramic, bevel=0.01)
    add_box("Kitchen undercabinet light", (2.55, 2.17, 1.97), (2.35, 0.025, 0.035), warm_light, bevel=0.008)
    add_box("Kitchen sink", (2.22, 2.08, 1.39), (0.76, 0.43, 0.065), dark, bevel=0.045)
    add_curve("Kitchen faucet", [(2.22, 1.98, 1.43), (2.22, 1.98, 1.78), (2.22, 1.78, 1.72)], dark, bevel_depth=0.027)
    for index in range(8):
        x = 1.12 + index * 0.44
        add_box("Kitchen front gap", (x, 2.185, 0.83), (0.018, 0.026, 0.82), dark, bevel=0.003)
    add_box("Refrigerator", (4.18, 2.30, 1.68), (0.78, 0.72, 2.66), ceramic, bevel=0.035)
    add_box("Refrigerator divide", (4.18, 1.91, 1.57), (0.62, 0.022, 0.025), dark, bevel=0.004)
    add_plant("Dining plant", (2.65, -0.75, 1.02), ceramic, leaf, earth, scale=0.42)

    # Doors, art and pendant fixtures give every visible room a finished focal point.
    for index, (x, y, z) in enumerate(((-0.65, 2.61, 1.68), (-1.35, 2.62, 4.70), (3.78, 2.75, 4.70))):
        add_box(f"Oak interior door {index}", (x, y, z), (1.00, 0.10, 2.36), wood, bevel=0.035)
        add_box(f"Door leaf reveal {index}", (x, y - 0.062, z), (0.82, 0.018, 2.14), dark, bevel=0.008)
        add_box(f"Door leaf face {index}", (x, y - 0.076, z), (0.76, 0.014, 2.08), wood, bevel=0.012)
        add_box(f"Door frame left {index}", (x - 0.55, y - 0.025, z), (0.075, 0.14, 2.48), wood, bevel=0.012)
        add_box(f"Door frame right {index}", (x + 0.55, y - 0.025, z), (0.075, 0.14, 2.48), wood, bevel=0.012)
        add_box(f"Door frame top {index}", (x, y - 0.025, z + 1.22), (1.18, 0.14, 0.075), wood, bevel=0.012)
        add_cylinder(f"Door handle {index}", (x + 0.34, y - 0.08, z), 0.025, 0.18, dark, rotation=(math.pi / 2, 0, 0), vertices=16)
    for index, x in enumerate((2.0, 2.65, 3.3)):
        add_cylinder(f"Pendant cable {index}", (x, -0.75, 2.72), 0.014, 0.64, dark, vertices=12)
        add_cone(f"Pendant shade {index}", (x, -0.75, 2.35), 0.06, 0.18, 0.22, dark, vertices=24)
        add_cylinder(f"Pendant glow {index}", (x, -0.75, 2.24), 0.055, 0.05, warm_light, vertices=20)

    # Electrical distribution, KNX/network modules and the red system path.
    # The technical wall faces the open front of the cutaway so that the
    # installation remains legible even at website scale.
    add_box("Technical service wall", (1.15, -2.82, 1.72), (1.52, 0.42, 2.84), interior_white, bevel=0.018)
    add_box("Service core left reveal", (0.47, -3.07, 1.72), (0.22, 0.32, 2.84), concrete, bevel=0.018)
    add_box("Service core right reveal", (1.83, -3.07, 1.72), (0.22, 0.32, 2.84), concrete, bevel=0.018)
    add_box("Service core head", (1.15, -3.07, 2.98), (1.52, 0.32, 0.28), concrete, bevel=0.018)
    add_box("Service core sill", (1.15, -3.07, 0.47), (1.52, 0.32, 0.22), concrete, bevel=0.018)
    add_box("Distribution cabinet", (1.15, -3.08, 1.70), (1.02, 0.25, 2.10), interior_white, bevel=0.022)
    add_box("Distribution recess", (1.15, -3.23, 1.70), (0.84, 0.075, 1.82), dark, bevel=0.012)
    for row in range(7):
        rail_z = 1.02 + row * 0.225
        add_box("DIN rail", (1.15, -3.285, rail_z), (0.72, 0.035, 0.025), ceramic, bevel=0.006)
        for module in range(6):
            module_mat = red if (row, module) in ((1, 4), (4, 1)) else interior_white
            add_box(
                "DIN module",
                (0.88 + module * 0.108, -3.32, rail_z + 0.018),
                (0.085, 0.075, 0.135),
                module_mat,
                bevel=0.010,
            )
            add_box(
                "DIN toggle",
                (0.88 + module * 0.108, -3.365, rail_z + 0.035),
                (0.035, 0.018, 0.045),
                dark,
                bevel=0.006,
            )
    # A few controlled wire loops make the open board read as installed
    # equipment.  They stay behind the DIN modules and avoid schematic clutter.
    for index, x in enumerate((0.90, 1.03, 1.16, 1.29, 1.42)):
        cable_mat = cable_green if index in (0, 4) else cable_blue
        add_curve(
            f"Distribution cable {index}",
            [
                (x, -3.34, 2.58),
                (x + 0.08 * (-1 if index % 2 else 1), -3.36, 2.40),
                (x - 0.05, -3.36, 2.18),
            ],
            cable_mat,
            bevel_depth=0.012,
            smooth=True,
        )
    add_box("Cabinet open door", (1.75, -3.02, 1.70), (0.055, 0.82, 2.04), glass, rotation=(0, 0, math.radians(-6)), bevel=0.018)
    for device_index, device_x in enumerate((0.54, 1.72)):
        add_box(
            f"Service automation enclosure {device_index}",
            (device_x, -3.31, 2.77),
            (0.32, 0.10, 0.36),
            ceramic,
            bevel=0.045,
        )
        add_box(
            f"Service automation indicator {device_index}",
            (device_x, -3.368, 2.77),
            (0.055, 0.012, 0.022),
            red if device_index == 0 else dark,
            bevel=0.005,
        )

    # Hollow inspection pit: separate concrete shell parts create readable depth
    # instead of a solid block with a black rectangle pasted onto its face.
    add_box("Network pit floor", (2.15, -4.72, -1.00), (1.58, 1.18, 0.12), concrete, bevel=0.020)
    add_box("Network pit left wall", (1.42, -4.72, -0.49), (0.12, 1.18, 1.10), concrete, bevel=0.020)
    add_box("Network pit right wall", (2.88, -4.72, -0.49), (0.12, 1.18, 1.10), concrete, bevel=0.020)
    add_box("Network pit back wall", (2.15, -4.19, -0.49), (1.58, 0.12, 1.10), concrete, bevel=0.020)
    add_box("Network pit inner back", (2.15, -4.26, -0.46), (1.28, 0.035, 0.82), interior_white, bevel=0.010)
    add_box("Network cabinet", (2.15, -4.31, -0.42), (0.78, 0.16, 0.76), dark, bevel=0.025)
    for x in (1.78, 2.52):
        add_box("Network rack upright", (x, -4.40, -0.42), (0.035, 0.035, 0.68), ceramic, bevel=0.005)
    for row in range(7):
        add_box("Network patch row", (2.15, -4.43, -0.70 + row * 0.09), (0.64, 0.028, 0.042), red if row in (2, 5) else interior_white, bevel=0.006)
        for port in range(8):
            add_box("Network port", (1.89 + port * 0.075, -4.46, -0.70 + row * 0.09), (0.035, 0.012, 0.018), dark, bevel=0.003)
    add_box("Network gateway", (2.52, -4.45, -0.24), (0.17, 0.035, 0.22), ceramic, bevel=0.025)
    for x, y, z in ((-3.6, -3.73, 1.45), (0.8, -3.73, 1.45), (3.8, -3.73, 4.65), (4.7, -1.2, 4.6)):
        add_box("KNX control", (x, y, z), (0.16, 0.08, 0.24) if abs(y) > 3 else (0.08, 0.16, 0.24), dark, bevel=0.025)
    add_curve(
        "Hubmann exterior feed",
        [
            (3.30, -7.82, -1.66),
            (4.15, -7.05, -1.42),
            (4.00, -6.25, -1.05),
            (2.75, -5.55, -0.62),
            (2.15, -5.30, -0.42),
        ],
        red,
        bevel_depth=0.027,
        smooth=True,
    )
    add_curve(
        "Hubmann installation path",
        [
            (2.15, -5.30, -0.42),
            (1.15, -5.05, -0.48),
            (1.15, -3.42, 0.32),
            (1.15, -3.42, 3.42),
            (1.15, -3.42, 5.78),
            (4.10, -3.42, 5.78),
            (4.10, 2.80, 5.78),
        ],
        red,
        bevel_depth=0.019,
        smooth=False,
    )
    add_curve(
        "Lighting branch ground",
        [(1.15, -3.42, 2.96), (1.15, -1.10, 2.96), (-2.55, -1.10, 2.96)],
        red,
        bevel_depth=0.011,
        smooth=False,
    )
    add_curve(
        "Kitchen branch ground",
        [(1.15, -3.42, 2.92), (3.15, -3.42, 2.92), (3.15, 2.55, 2.92)],
        red,
        bevel_depth=0.011,
        smooth=False,
    )
    add_curve(
        "Bedroom branch upper",
        [(1.15, -3.42, 5.64), (-2.75, -3.42, 5.64), (-2.75, 1.52, 5.64), (-2.75, 1.52, 5.18)],
        red,
        bevel_depth=0.011,
        smooth=False,
    )
    add_curve(
        "Bathroom branch upper",
        [(1.15, -3.42, 5.62), (1.15, 2.36, 5.62), (1.78, 2.36, 5.62)],
        red,
        bevel_depth=0.011,
        smooth=False,
    )

    # Lighting fixtures and warm final-state light sources.
    light_objects: list[bpy.types.Object] = []
    downlight_locations = (
        (-3.45, -1.45, 3.08), (-1.75, -1.45, 3.08), (-3.45, 1.30, 3.08),
        (-0.10, 0.85, 3.08), (2.10, 1.25, 3.08), (3.75, 1.25, 3.08),
        (-3.55, -1.25, 5.78), (-1.75, -1.25, 5.78), (-3.55, 1.25, 5.78),
        (0.65, 1.10, 5.78), (1.65, 1.10, 5.78), (3.95, 0.80, 5.78),
    )
    for index, location in enumerate(downlight_locations):
        add_recessed_light(f"Downlight {index}", location, dark, warm_light)
        light_data = bpy.data.lights.new(f"Warm downlight {index}", type="POINT")
        light_data.color = (1.0, 0.66, 0.39)
        light_data.energy = 95
        light_data.shadow_soft_size = 0.72
        light = bpy.data.objects.new(f"Warm downlight {index}", light_data)
        light.location = (location[0], location[1], location[2] - 0.25)
        bpy.context.collection.objects.link(light)
        light_objects.append(light)

    # Photovoltaic modules sit on the right roof plane and fly in individually.
    pv_final: list[tuple[bpy.types.Object, Vector]] = []
    rail_z = 8.57 - 2.55 * math.tan(roof_angle) + 0.035
    for rail_y in (-3.10, -1.40, -1.00, 0.70, 1.10, 2.80):
        add_box(
            "PV mounting rail",
            (2.55, rail_y, rail_z),
            (4.30, 0.065, 0.075),
            dark,
            rotation=(0, roof_angle, 0),
            bevel=0.012,
            parent=pv_group,
        )
    module_index = 0
    for x in (1.45, 3.15):
        for y in (-2.25, -0.15, 1.95):
            z = 8.57 - x * math.tan(roof_angle) + 0.12
            module = empty(f"PV module assembly {module_index + 1}")
            module.parent = pv_group
            module.location = (x, y, z)
            module.rotation_euler = (0, roof_angle, 0)
            add_box(
                f"PV module {module_index + 1}",
                (0, 0, 0),
                (1.52, 1.78, 0.10),
                pv,
                bevel=0.025,
                parent=module,
            )
            # Silver perimeter frame and two subtle cell separators.
            add_box(f"PV frame top {module_index}", (0, -0.86, 0.03), (1.54, 0.035, 0.07), dark, bevel=0.008, parent=module)
            add_box(f"PV frame bottom {module_index}", (0, 0.86, 0.03), (1.54, 0.035, 0.07), dark, bevel=0.008, parent=module)
            add_box(f"PV frame left {module_index}", (-0.75, 0, 0.03), (0.035, 1.72, 0.07), dark, bevel=0.008, parent=module)
            add_box(f"PV frame right {module_index}", (0.75, 0, 0.03), (0.035, 1.72, 0.07), dark, bevel=0.008, parent=module)
            for separator in (-0.50, -0.25, 0, 0.25, 0.50):
                add_box(
                    f"PV cell column {module_index} {separator}",
                    (separator, 0, -0.058),
                    (0.009, 1.64, 0.008),
                    dark,
                    bevel=0,
                    parent=module,
                )
            for separator in (-0.56, -0.28, 0, 0.28, 0.56):
                add_box(
                    f"PV cell row {module_index} {separator}",
                    (0, separator, -0.057),
                    (1.42, 0.009, 0.008),
                    dark,
                    bevel=0,
                    parent=module,
                )
            pv_final.append((module, Vector(module.location)))
            module_index += 1

    # Inverter and battery are separated for the energy reveal.
    inverter = add_box("PV inverter", (5.18, -0.85, 2.25), (0.32, 0.92, 1.15), interior_white, bevel=0.07, parent=technical_group)
    add_box("Inverter display", (5.36, -0.85, 2.25), (0.035, 0.22, 0.13), dark, bevel=0.018, parent=technical_group)
    battery = add_box("Battery storage", (5.18, -0.83, 0.92), (0.42, 1.02, 1.36), interior_white, bevel=0.09, parent=technical_group)
    add_curve("PV DC cable", [(5.25, -0.85, 5.9), (5.25, -0.85, 3.0), (5.25, -0.85, 1.1), (5.0, -3.8, 0.0)], red, bevel_depth=0.03, parent=technical_group)

    # Warm planes sit behind selected glazing and create the occupied-house depth
    # visible in the approved energy mockup.
    add_box("Warm living window depth", (-2.55, -3.70, 1.64), (1.72, 0.025, 2.08), warm_light, bevel=0.01, parent=facade_front)
    add_box("Warm bedroom window depth", (1.55, -3.70, 4.72), (2.58, 0.025, 1.88), warm_light, bevel=0.01, parent=facade_front)

    # Studio floor.
    bpy.ops.mesh.primitive_plane_add(size=70, location=(0, 0, -1.92))
    studio_floor = bpy.context.object
    studio_floor.name = "White studio floor"
    apply_material(studio_floor, material("Studio white", (0.97, 0.97, 0.97, 1), roughness=0.82))

    # Camera and animated focus target.
    target = empty("Camera focus")
    target.location = (0, -0.15, 3.55)
    bpy.ops.object.camera_add(location=(27.5, -43.0, 13.0))
    camera = bpy.context.object
    camera.name = "Hero camera"
    camera.data.lens = 84
    camera.data.sensor_width = 36
    camera.data.shift_x = -0.06
    camera.data.shift_y = 0.0
    constraint = camera.constraints.new(type="TRACK_TO")
    constraint.target = target
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"
    bpy.context.scene.camera = camera

    keyframe_transform(camera, 1, location=(21.5, -29.5, 11.8))
    keyframe_transform(camera, 28, location=(20.5, -28.0, 11.2))
    keyframe_transform(camera, 52, location=(20.2, -43.2, 9.8))
    keyframe_transform(camera, 70, location=(21.0, -29.5, 12.0))
    keyframe_transform(camera, 92, location=(21.5, -30.5, 11.4))
    keyframe_transform(camera, 120, location=(21.5, -29.5, 11.8))
    keyframe_transform(target, 1, location=(0, 0, 3.0))
    keyframe_transform(target, 52, location=(0.0, -0.15, 3.30))
    keyframe_transform(target, 72, location=(0.2, 0.1, 3.5))
    keyframe_transform(target, 92, location=(0.25, 0.0, 3.95))
    keyframe_transform(target, 120, location=(0, 0, 3.1))

    # Facade and roof reveal choreography.
    keyframe_transform(facade_front, 1, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1))
    keyframe_transform(facade_front, 27, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1))
    keyframe_transform(facade_front, 49, scale=(0.001, 0.001, 0.001))
    keyframe_transform(facade_front, 72, scale=(0.001, 0.001, 0.001))
    keyframe_transform(facade_front, 82, scale=(1, 1, 1))
    keyframe_transform(facade_front, 113, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1))
    keyframe_transform(facade_side, 1, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1))
    keyframe_transform(facade_side, 27, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1))
    keyframe_transform(facade_side, 49, scale=(0.001, 0.001, 0.001))
    keyframe_transform(facade_side, 72, scale=(0.001, 0.001, 0.001))
    keyframe_transform(facade_side, 82, scale=(1, 1, 1))
    keyframe_transform(facade_side, 113, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1))
    keyframe_transform(roof_group, 1, location=(0, 0, 0), rotation=(0, 0, 0))
    keyframe_transform(roof_group, 27, location=(0, 0, 0), rotation=(0, 0, 0))
    keyframe_transform(roof_group, 49, location=(0.12, 0.03, 0.65), rotation=(math.radians(-0.2), 0, math.radians(0.3)))
    keyframe_transform(roof_group, 68, location=(0.12, 0.03, 0.65), rotation=(math.radians(-0.2), 0, math.radians(0.3)))
    keyframe_transform(roof_group, 82, location=(0, 0, 0), rotation=(0, 0, 0))
    keyframe_transform(exploded_panels, 1, scale=(0.001, 0.001, 0.001))
    keyframe_transform(exploded_panels, 40, scale=(0.001, 0.001, 0.001))
    keyframe_transform(exploded_panels, 49, scale=(1, 1, 1))
    keyframe_transform(exploded_panels, 68, scale=(1, 1, 1))
    keyframe_transform(exploded_panels, 82, scale=(0.001, 0.001, 0.001))

    # PV and energy equipment reveal from alternating sides.
    keyframe_transform(pv_group, 1, scale=(0.001, 0.001, 0.001))
    keyframe_transform(pv_group, 68, scale=(0.001, 0.001, 0.001))
    keyframe_transform(pv_group, 80, scale=(1, 1, 1))
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

    roof_bounce_data = bpy.data.lights.new("Roof cavity bounce", type="POINT")
    roof_bounce_data.color = (1.0, 0.88, 0.74)
    roof_bounce_data.energy = 230
    roof_bounce_data.shadow_soft_size = 3.2
    roof_bounce = bpy.data.objects.new("Roof cavity bounce", roof_bounce_data)
    roof_bounce.location = (0.0, -0.6, 7.15)
    bpy.context.collection.objects.link(roof_bounce)

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

    area_light("Key softbox", (-8, -11, 18), 980, 8.0, (1.0, 0.93, 0.84))
    area_light("Fill softbox", (13, -3, 10), 190, 9.0, (0.82, 0.90, 1.0))
    area_light("Rear softbox", (-5, 11, 14), 320, 7.0, (1.0, 0.88, 0.74))

    scene = bpy.context.scene
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.render.engine = os.environ.get("HUBMANN_RENDER_ENGINE", "BLENDER_EEVEE")
    if scene.render.engine == "CYCLES":
        scene.cycles.samples = int(os.environ.get("HUBMANN_CYCLES_SAMPLES", "48"))
        scene.cycles.use_denoising = True
        scene.cycles.use_adaptive_sampling = True
        studio_floor.is_shadow_catcher = True
        scene.render.film_transparent = True

    scene.render.resolution_x = RENDER_WIDTH
    scene.render.resolution_y = RENDER_HEIGHT
    scene.render.resolution_percentage = 100
    output_format = os.environ.get("HUBMANN_RENDER_FORMAT", "JPEG").upper()
    scene.render.image_settings.file_format = output_format
    scene.render.image_settings.color_mode = "RGBA" if output_format == "PNG" else "RGB"
    scene.render.image_settings.quality = 96
    scene.render.fps = 30
    scene.render.film_transparent = scene.render.engine == "CYCLES"
    scene.render.use_file_extension = True
    scene.render.filepath = str(SEQUENCE_DIR / "house-")
    scene.world.color = (1.0, 1.0, 1.0)
    if scene.world.use_nodes:
        background = scene.world.node_tree.nodes.get("Background")
        background.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        background.inputs["Strength"].default_value = 0.27
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.exposure = 0.68 if scene.render.engine == "CYCLES" else 0.0
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass

    BLEND_PATH.parent.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)
    SEQUENCE_DIR.mkdir(parents=True, exist_ok=True)
    bpy.ops.file.pack_all()
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
        suffix = ".png" if scene.render.image_settings.file_format == "PNG" else ".jpg"
        default_output = QA_DIR / f"house-frame-{frame:03d}{suffix}"
        scene.render.filepath = os.environ.get("HUBMANN_RENDER_OUTPUT", str(default_output))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
