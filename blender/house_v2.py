"""Build the independent Elektro Hubmann house V2 scene.

V2 is intentionally isolated from ``house_story.py``.  It is developed in
small approval stages against ``house-mockups-v2/02-technical-axonometric.png``
and never renders the production 120-frame sequence by default.

Blender 5.2+:
    blender --background --python blender/house_v2.py
"""

from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
BLEND_PATH = ROOT / "assets" / "3d" / "elektro-hubmann-house-v2.blend"
QA_DIR = ROOT / "docs" / "version-g-qa" / "blender-v2"
SEQUENCE_DIR = ROOT / "public" / "images" / "version-g" / "sequence"
REFERENCE_PATH = (
    ROOT
    / "docs"
    / "reference"
    / "house-mockups-v2"
    / "02-technical-axonometric.png"
)

FRAME_START = 1
FRAME_END = 120
BUILD_STAGE = os.environ.get("HUBMANN_V2_STAGE", "phase0").lower()
VALID_STAGES = (
    "phase0",
    "phase1a",
    "phase1b",
    "phase2a",
    "phase2b",
    "phase3a",
    "phase3b",
    "phase4",
)


@dataclass(frozen=True)
class HouseDimensions:
    """Single architectural datum shared by every future V2 build stage."""

    width: float = 9.40
    depth: float = 7.40
    ground_front_y: float = -3.55
    ground_rear_y: float = 3.85
    ground_finish_z: float = 0.30
    upper_finish_z: float = 3.52
    upper_ceiling_z: float = 6.35
    roof_ridge_z: float = 8.90
    roof_eave_z: float = 6.62
    roof_overhang_x: float = 0.72
    roof_overhang_y: float = 0.56
    service_x: float = 1.72
    server_center_y: float = -4.68
    server_width: float = 2.70
    server_depth: float = 2.05
    server_floor_z: float = -1.62
    server_ceiling_z: float = 0.08


DIMS = HouseDimensions()

COLLECTION_NAMES = (
    "V2 STRUCTURE",
    "V2 EXTERIOR",
    "V2 FACADE",
    "V2 INTERIOR",
    "V2 FURNITURE",
    "V2 TECHNICAL",
    "V2 LIGHTING",
    "V2 ANIMATION",
    "V2 PLAN",
    "V2 QA",
)


def reset_scene() -> None:
    """Remove all scene data so every V2 build starts deterministically."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for datablock in list(datablocks):
            datablocks.remove(datablock)


def create_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def create_material(
    name: str,
    color: tuple[float, float, float, float],
    *,
    roughness: float,
    metallic: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Metallic"].default_value = metallic
    return material


def create_glass_material() -> bpy.types.Material:
    material = create_material(
        "V2 Glass", (0.075, 0.115, 0.135, 1.0), roughness=0.10, metallic=0.06
    )
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled is not None:
        transmission = principled.inputs.get("Transmission Weight")
        coat = principled.inputs.get("Coat Weight")
        ior = principled.inputs.get("IOR")
        if transmission is not None:
            transmission.default_value = 0.18
        if coat is not None:
            coat.default_value = 0.32
        if ior is not None:
            ior.default_value = 1.45
    return material


def create_emission_material(
    name: str,
    color: tuple[float, float, float, float],
    *,
    strength: float,
) -> bpy.types.Material:
    """Create a compact emissive material that remains readable in Eevee."""
    material = create_material(name, color, roughness=0.28)
    principled = material.node_tree.nodes.get("Principled BSDF")
    emission_color = principled.inputs.get("Emission Color")
    emission_strength = principled.inputs.get("Emission Strength")
    if emission_color is not None:
        emission_color.default_value = color
    if emission_strength is not None:
        emission_strength.default_value = strength
    return material


def create_contact_shadow_material() -> bpy.types.Material:
    """Create a feathered fake shadow for the otherwise seamless white studio."""
    material = bpy.data.materials.new("V2 soft contact shadow")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = 3.0
    vertex_color = nodes.new("ShaderNodeAttribute")
    vertex_color.attribute_name = "V2 Shadow Alpha"
    links.new(vertex_color.outputs["Color"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def add_surface_bump(
    material: bpy.types.Material,
    *,
    scale: float,
    detail: float,
    strength: float,
    distance: float,
) -> None:
    """Add subtle procedural relief without changing the approved palette."""
    if material.node_tree is None:
        return
    nodes = material.node_tree.nodes
    if nodes.get(f"{material.name} finish") is not None:
        return
    links = material.node_tree.links
    principled = nodes.get("Principled BSDF")
    if principled is None:
        return
    noise = nodes.new("ShaderNodeTexNoise")
    noise.name = f"{material.name} finish"
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = detail
    noise.inputs["Roughness"].default_value = 0.72
    bump = nodes.new("ShaderNodeBump")
    bump.name = f"{material.name} relief"
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = distance
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])


def create_v2_materials() -> dict[str, bpy.types.Material]:
    """Create only the stable palette needed by the planned build phases."""
    return {
        "concrete": create_material(
            "V2 Concrete", (0.62, 0.60, 0.56, 1.0), roughness=0.82
        ),
        "plaster": create_material(
            "V2 Warm plaster", (0.91, 0.89, 0.84, 1.0), roughness=0.86
        ),
        "oak": create_material(
            "V2 Pale oak", (0.36, 0.19, 0.070, 1.0), roughness=0.62
        ),
        "charcoal": create_material(
            "V2 Charcoal", (0.004, 0.005, 0.006, 1.0), roughness=0.48
        ),
        "glass": create_glass_material(),
        "service_red": create_material(
            "V2 Service red", (0.88, 0.025, 0.018, 1.0), roughness=0.38
        ),
        "qa_floor": create_material(
            # The web canvas sits on pure white.  A white matte receiver keeps
            # the soft contact shadow without baking a grey rectangle into the
            # JPG sequence.
            "V2 QA floor", (1.0, 1.0, 1.0, 1.0), roughness=1.0
        ),
        "floor_oak": create_material(
            "V2 Floor oak", (0.48, 0.28, 0.11, 1.0), roughness=0.72
        ),
        "upholstery": create_material(
            "V2 Upholstery", (0.60, 0.58, 0.54, 1.0), roughness=0.92
        ),
        "tile": create_material(
            "V2 Bathroom tile", (0.28, 0.31, 0.31, 1.0), roughness=0.76
        ),
        "porcelain": create_material(
            "V2 Porcelain", (0.90, 0.89, 0.85, 1.0), roughness=0.42
        ),
        "tech_blue": create_material(
            "V2 Technical blue", (0.025, 0.14, 0.24, 1.0), roughness=0.34
        ),
        "pv_blue": create_material(
            "V2 PV blue", (0.018, 0.050, 0.075, 1.0), roughness=0.38, metallic=0.08
        ),
        "plant": create_material(
            "V2 Plant green", (0.055, 0.23, 0.075, 1.0), roughness=0.80
        ),
        "plan_living": create_material(
            "V2 Plan living", (0.34, 0.50, 0.61, 1.0), roughness=0.92
        ),
        "plan_circulation": create_material(
            "V2 Plan circulation", (0.69, 0.56, 0.31, 1.0), roughness=0.92
        ),
        "plan_service": create_material(
            "V2 Plan service", (0.69, 0.30, 0.25, 1.0), roughness=0.92
        ),
        "plan_kitchen": create_material(
            "V2 Plan kitchen", (0.33, 0.55, 0.37, 1.0), roughness=0.92
        ),
        "plan_bed": create_material(
            "V2 Plan bedroom", (0.48, 0.39, 0.62, 1.0), roughness=0.92
        ),
        "plan_bath": create_material(
            "V2 Plan bathroom", (0.27, 0.54, 0.62, 1.0), roughness=0.92
        ),
        "plan_gallery": create_material(
            "V2 Plan gallery", (0.62, 0.47, 0.31, 1.0), roughness=0.92
        ),
        "plan_text": create_material(
            "V2 Plan text", (0.025, 0.028, 0.030, 1.0), roughness=0.55
        ),
    }


def add_box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    *,
    collection: str,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel: float = 0.0,
) -> bpy.types.Object:
    """Add one clean blockout primitive to an explicit V2 collection."""
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for source_collection in list(obj.users_collection):
        source_collection.objects.unlink(obj)
    bpy.data.collections[collection].objects.link(obj)
    obj.data.materials.append(material)
    if bevel > 0.0:
        modifier = obj.modifiers.new("V2 edge finish", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
    return obj


def add_triangular_prism(
    name: str,
    *,
    center_x: float,
    y: float,
    base_z: float,
    width: float,
    height: float,
    thickness: float,
    material: bpy.types.Material,
    collection: str,
) -> bpy.types.Object:
    """Add a clean gable infill as a shallow triangular wall prism."""
    half_width = width / 2
    half_thickness = thickness / 2
    vertices = (
        (center_x - half_width, y - half_thickness, base_z),
        (center_x + half_width, y - half_thickness, base_z),
        (center_x, y - half_thickness, base_z + height),
        (center_x - half_width, y + half_thickness, base_z),
        (center_x + half_width, y + half_thickness, base_z),
        (center_x, y + half_thickness, base_z + height),
    )
    faces = (
        (0, 2, 1),
        (3, 4, 5),
        (0, 1, 4, 3),
        (1, 2, 5, 4),
        (2, 0, 3, 5),
    )
    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata(vertices, (), faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.data.collections[collection].objects.link(obj)
    obj.data.materials.append(material)
    bevel = obj.modifiers.new("V2 gable edge finish", "BEVEL")
    bevel.width = 0.012
    bevel.segments = 2
    return obj


def add_soft_contact_shadow(
    name: str,
    *,
    location: tuple[float, float, float],
    radius_x: float,
    radius_y: float,
    collection: str,
) -> bpy.types.Object:
    """Add a transparent feathered ellipse instead of a visible studio floor."""
    segments = 64
    rings = (
        (0.00, 0.16),
        (0.28, 0.13),
        (0.55, 0.075),
        (0.78, 0.025),
        (1.00, 0.00),
    )
    vertices: list[tuple[float, float, float]] = [(0.0, 0.0, 0.0)]
    alphas: list[float] = [rings[0][1]]
    for radius, alpha in rings[1:]:
        for index in range(segments):
            angle = 2 * math.pi * index / segments
            vertices.append(
                (radius_x * radius * math.cos(angle), radius_y * radius * math.sin(angle), 0.0)
            )
            alphas.append(alpha)

    faces: list[tuple[int, ...]] = []
    first_ring = 1
    for index in range(segments):
        faces.append((0, first_ring + index, first_ring + (index + 1) % segments))
    for ring_index in range(1, len(rings) - 1):
        inner = 1 + (ring_index - 1) * segments
        outer = 1 + ring_index * segments
        for index in range(segments):
            next_index = (index + 1) % segments
            faces.append(
                (inner + index, outer + index, outer + next_index, inner + next_index)
            )

    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata(vertices, (), faces)
    mesh.update()
    colors = mesh.color_attributes.new(
        name="V2 Shadow Alpha", type="FLOAT_COLOR", domain="CORNER"
    )
    for entry, loop in zip(colors.data, mesh.loops, strict=True):
        # Fully opaque colour interpolation is more reliable than alpha
        # blending in Eevee and fades exactly into the white world background.
        alpha = alphas[loop.vertex_index]
        shade = 1.0 - 6.0 * alpha
        entry.color = (shade, shade, shade, 1.0)

    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    bpy.data.collections[collection].objects.link(obj)
    obj.data.materials.append(create_contact_shadow_material())
    return obj


def add_cylinder(
    name: str,
    location: tuple[float, float, float],
    *,
    radius: float,
    depth: float,
    material: bpy.types.Material,
    collection: str,
    vertices: int = 24,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    for source_collection in list(obj.users_collection):
        source_collection.objects.unlink(obj)
    bpy.data.collections[collection].objects.link(obj)
    obj.data.materials.append(material)
    return obj


def add_beam_between(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    *,
    thickness: float,
    material: bpy.types.Material,
    collection: str,
) -> bpy.types.Object:
    start_vector = Vector(start)
    end_vector = Vector(end)
    direction = end_vector - start_vector
    midpoint = (start_vector + end_vector) / 2
    bpy.ops.mesh.primitive_cube_add(location=midpoint)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    obj.dimensions = (thickness, thickness, direction.length)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for source_collection in list(obj.users_collection):
        source_collection.objects.unlink(obj)
    bpy.data.collections[collection].objects.link(obj)
    obj.data.materials.append(material)
    bevel = obj.modifiers.new("V2 edge finish", "BEVEL")
    bevel.width = min(0.018, thickness * 0.18)
    bevel.segments = 2
    return obj


def remove_objects_with_prefix(*prefixes: str) -> None:
    for obj in list(bpy.data.objects):
        if any(obj.name.startswith(prefix) for prefix in prefixes):
            bpy.data.objects.remove(obj, do_unlink=True)


def add_wall_x_with_openings(
    name: str,
    *,
    x_min: float,
    x_max: float,
    y: float,
    z_floor: float,
    z_ceiling: float,
    openings: tuple[tuple[float, float, float, float], ...],
    material: bpy.types.Material,
    collection: str,
    thickness: float = 0.18,
) -> None:
    """Build an X-aligned wall from non-overlapping blocks around openings."""
    cursor = x_min
    for index, (center, width, bottom, height) in enumerate(
        sorted(openings, key=lambda item: item[0])
    ):
        opening_min = center - width / 2
        opening_max = center + width / 2
        if opening_min > cursor:
            add_box(
                f"{name} span {index}",
                ((cursor + opening_min) / 2, y, (z_floor + z_ceiling) / 2),
                (opening_min - cursor, thickness, z_ceiling - z_floor),
                material,
                collection=collection,
                bevel=0.012,
            )
        if bottom > z_floor:
            add_box(
                f"{name} sill {index}",
                (center, y, (z_floor + bottom) / 2),
                (width, thickness, bottom - z_floor),
                material,
                collection=collection,
                bevel=0.012,
            )
        opening_top = bottom + height
        if opening_top < z_ceiling:
            add_box(
                f"{name} lintel {index}",
                (center, y, (opening_top + z_ceiling) / 2),
                (width, thickness, z_ceiling - opening_top),
                material,
                collection=collection,
                bevel=0.012,
            )
        cursor = opening_max
    if cursor < x_max:
        add_box(
            f"{name} span end",
            ((cursor + x_max) / 2, y, (z_floor + z_ceiling) / 2),
            (x_max - cursor, thickness, z_ceiling - z_floor),
            material,
            collection=collection,
            bevel=0.012,
        )


def add_wall_y_with_openings(
    name: str,
    *,
    x: float,
    y_min: float,
    y_max: float,
    z_floor: float,
    z_ceiling: float,
    openings: tuple[tuple[float, float, float, float], ...],
    material: bpy.types.Material,
    collection: str,
    thickness: float = 0.18,
) -> None:
    """Build a Y-aligned wall from non-overlapping blocks around openings."""
    cursor = y_min
    for index, (center, width, bottom, height) in enumerate(
        sorted(openings, key=lambda item: item[0])
    ):
        opening_min = center - width / 2
        opening_max = center + width / 2
        if opening_min > cursor:
            add_box(
                f"{name} span {index}",
                (x, (cursor + opening_min) / 2, (z_floor + z_ceiling) / 2),
                (thickness, opening_min - cursor, z_ceiling - z_floor),
                material,
                collection=collection,
                bevel=0.012,
            )
        if bottom > z_floor:
            add_box(
                f"{name} sill {index}",
                (x, center, (z_floor + bottom) / 2),
                (thickness, width, bottom - z_floor),
                material,
                collection=collection,
                bevel=0.012,
            )
        opening_top = bottom + height
        if opening_top < z_ceiling:
            add_box(
                f"{name} lintel {index}",
                (x, center, (opening_top + z_ceiling) / 2),
                (thickness, width, z_ceiling - opening_top),
                material,
                collection=collection,
                bevel=0.012,
            )
        cursor = opening_max
    if cursor < y_max:
        add_box(
            f"{name} span end",
            (x, (cursor + y_max) / 2, (z_floor + z_ceiling) / 2),
            (thickness, y_max - cursor, z_ceiling - z_floor),
            material,
            collection=collection,
            bevel=0.012,
        )


def add_plan_label(
    name: str,
    text: str,
    location: tuple[float, float, float],
    material: bpy.types.Material,
    *,
    size: float = 0.28,
) -> bpy.types.Object:
    bpy.ops.object.text_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.006
    for source_collection in list(obj.users_collection):
        source_collection.objects.unlink(obj)
    bpy.data.collections["V2 PLAN"].objects.link(obj)
    obj.data.materials.append(material)
    return obj


def add_plan_zone(
    name: str,
    label: str,
    center: tuple[float, float],
    dimensions: tuple[float, float],
    z: float,
    material: bpy.types.Material,
    text_material: bpy.types.Material,
) -> None:
    add_box(
        f"V2 Plan {name} zone",
        (center[0], center[1], z),
        (dimensions[0], dimensions[1], 0.035),
        material,
        collection="V2 PLAN",
        bevel=0.035,
    )
    if z < 0.0:
        label_z = DIMS.server_ceiling_z + 0.06
    elif z < 2.0:
        label_z = DIMS.upper_finish_z - 0.26
    else:
        label_z = DIMS.upper_ceiling_z - 0.24
    add_plan_label(
        f"V2 Plan {name} label",
        label,
        (center[0], center[1], label_z),
        text_material,
        size=min(
            0.30,
            max(0.11, dimensions[0] / (0.72 * max(len(label), 1))),
        ),
    )


def add_window_x(
    name: str,
    *,
    center_x: float,
    y: float,
    bottom: float,
    width: float,
    height: float,
    frame: bpy.types.Material,
    glass: bpy.types.Material,
    collection: str,
) -> None:
    center_z = bottom + height / 2
    add_box(
        f"{name} glass",
        (center_x, y, center_z),
        (width - 0.14, 0.045, height - 0.14),
        glass,
        collection=collection,
        bevel=0.008,
    )
    for suffix, x in (("left", center_x - width / 2), ("right", center_x + width / 2)):
        add_box(
            f"{name} frame {suffix}",
            (x, y, center_z),
            (0.075, 0.13, height),
            frame,
            collection=collection,
            bevel=0.008,
        )
    for suffix, z in (("bottom", bottom), ("top", bottom + height)):
        add_box(
            f"{name} frame {suffix}",
            (center_x, y, z),
            (width, 0.13, 0.075),
            frame,
            collection=collection,
            bevel=0.008,
        )
    if width >= 1.55:
        add_box(
            f"{name} frame mullion",
            (center_x, y - 0.012, center_z),
            (0.055, 0.145, height - 0.06),
            frame,
            collection=collection,
            bevel=0.008,
        )


def add_window_y(
    name: str,
    *,
    x: float,
    center_y: float,
    bottom: float,
    width: float,
    height: float,
    frame: bpy.types.Material,
    glass: bpy.types.Material,
    collection: str,
) -> None:
    center_z = bottom + height / 2
    add_box(
        f"{name} glass",
        (x, center_y, center_z),
        (0.045, width - 0.14, height - 0.14),
        glass,
        collection=collection,
        bevel=0.008,
    )
    for suffix, y in (("front", center_y - width / 2), ("rear", center_y + width / 2)):
        add_box(
            f"{name} frame {suffix}",
            (x, y, center_z),
            (0.13, 0.075, height),
            frame,
            collection=collection,
            bevel=0.008,
        )
    for suffix, z in (("bottom", bottom), ("top", bottom + height)):
        add_box(
            f"{name} frame {suffix}",
            (x, center_y, z),
            (0.13, width, 0.075),
            frame,
            collection=collection,
            bevel=0.008,
        )
    if width >= 1.55:
        add_box(
            f"{name} frame mullion",
            (x - 0.012, center_y, center_z),
            (0.145, 0.055, height - 0.06),
            frame,
            collection=collection,
            bevel=0.008,
        )


def add_door_x(
    name: str,
    *,
    center_x: float,
    y: float,
    bottom: float,
    width: float,
    height: float,
    material: bpy.types.Material,
    frame: bpy.types.Material,
    collection: str,
) -> None:
    add_box(
        f"{name} leaf",
        (center_x, y, bottom + height / 2),
        (width - 0.12, 0.055, height - 0.08),
        material,
        collection=collection,
        bevel=0.018,
    )
    for suffix, x in (("left", center_x - width / 2), ("right", center_x + width / 2)):
        add_box(
            f"{name} frame {suffix}",
            (x, y, bottom + height / 2),
            (0.07, 0.13, height),
            frame,
            collection=collection,
            bevel=0.008,
        )
    add_box(
        f"{name} frame top",
        (center_x, y, bottom + height),
        (width, 0.13, 0.07),
        frame,
        collection=collection,
        bevel=0.008,
    )
    add_box(
        f"{name} handle",
        (center_x + width * 0.30, y - 0.075, bottom + 1.02),
        (0.12, 0.055, 0.045),
        frame,
        collection=collection,
        bevel=0.012,
    )


def add_door_y(
    name: str,
    *,
    x: float,
    center_y: float,
    bottom: float,
    width: float,
    height: float,
    material: bpy.types.Material,
    frame: bpy.types.Material,
    collection: str,
) -> None:
    add_box(
        f"{name} leaf",
        (x, center_y, bottom + height / 2),
        (0.055, width - 0.12, height - 0.08),
        material,
        collection=collection,
        bevel=0.018,
    )
    for suffix, y in (("front", center_y - width / 2), ("rear", center_y + width / 2)):
        add_box(
            f"{name} frame {suffix}",
            (x, y, bottom + height / 2),
            (0.13, 0.07, height),
            frame,
            collection=collection,
            bevel=0.008,
        )
    add_box(
        f"{name} frame top",
        (x, center_y, bottom + height),
        (0.13, width, 0.07),
        frame,
        collection=collection,
        bevel=0.008,
    )
    add_box(
        f"{name} handle",
        (x - 0.075, center_y + width * 0.30, bottom + 1.02),
        (0.055, 0.12, 0.045),
        frame,
        collection=collection,
        bevel=0.012,
    )


def add_area_light(
    name: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    *,
    energy: float,
    size: float,
    color: tuple[float, float, float],
) -> bpy.types.Object:
    data = bpy.data.lights.new(f"{name} data", type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    light = bpy.data.objects.new(name, data)
    bpy.data.collections["V2 QA"].objects.link(light)
    light.location = location
    look_at(light, target)
    return light


def add_house_point_light(
    name: str,
    location: tuple[float, float, float],
    *,
    energy: float,
    color: tuple[float, float, float],
    radius: float = 0.28,
) -> bpy.types.Object:
    """Add one deliberately soft interior light to the final house scene."""
    data = bpy.data.lights.new(f"{name} data", type="POINT")
    data.energy = energy
    data.color = color
    data.shadow_soft_size = radius
    data.use_shadow = False
    light = bpy.data.objects.new(name, data)
    bpy.data.collections["V2 LIGHTING"].objects.link(light)
    light.location = location
    return light


def look_at(
    obj: bpy.types.Object,
    target: tuple[float, float, float],
) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def create_camera(
    name: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    *,
    lens: float = 64.0,
    orthographic_scale: float | None = None,
) -> bpy.types.Object:
    camera_data = bpy.data.cameras.new(f"{name} data")
    camera = bpy.data.objects.new(name, camera_data)
    bpy.data.collections["V2 QA"].objects.link(camera)
    camera.location = location
    if orthographic_scale is None:
        camera_data.type = "PERSP"
        camera_data.lens = lens
        camera_data.sensor_width = 36.0
    else:
        camera_data.type = "ORTHO"
        camera_data.ortho_scale = orthographic_scale
    look_at(camera, target)
    return camera


def configure_scene() -> None:
    scene = bpy.context.scene
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1484
    scene.render.resolution_y = 1060
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.exposure = 0.10
    try:
        scene.view_settings.look = "AgX - Very High Contrast"
    except Exception:
        pass

    scene.world.color = (1.0, 1.0, 1.0)
    scene.world.use_nodes = True
    nodes = scene.world.node_tree.nodes
    links = scene.world.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputWorld")
    mix = nodes.new("ShaderNodeMixShader")
    light_path = nodes.new("ShaderNodeLightPath")
    ambient = nodes.new("ShaderNodeBackground")
    ambient.inputs["Color"].default_value = (0.94, 0.95, 0.96, 1.0)
    ambient.inputs["Strength"].default_value = 0.36
    camera_background = nodes.new("ShaderNodeBackground")
    camera_background.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    camera_background.inputs["Strength"].default_value = 3.0
    links.new(light_path.outputs["Is Camera Ray"], mix.inputs[0])
    links.new(ambient.outputs["Background"], mix.inputs[1])
    links.new(camera_background.outputs["Background"], mix.inputs[2])
    links.new(mix.outputs["Shader"], output.inputs["Surface"])


def build_phase0() -> dict[str, bpy.types.Material]:
    """Create the clean V2 scene contract without committing geometry yet."""
    reset_scene()
    for name in COLLECTION_NAMES:
        create_collection(name)
    materials = create_v2_materials()

    hero_camera = create_camera(
        "V2 Camera Mockup",
        (14.5, -31.5, 8.2),
        (0.0, -0.20, 2.95),
        lens=66.0,
    )
    create_camera(
        "V2 Camera Front",
        (0.0, -34.0, 4.05),
        (0.0, -0.25, 3.10),
        lens=65.0,
    )
    create_camera(
        "V2 Camera Right",
        (34.0, 0.0, 4.20),
        (0.0, -0.15, 3.10),
        lens=50.0,
    )
    create_camera(
        "V2 Plan Ground",
        (0.0, 0.0, 15.0),
        (0.0, 0.0, 0.0),
        orthographic_scale=12.2,
    )
    create_camera(
        "V2 Plan Upper",
        (0.0, 0.0, 15.0),
        (0.0, 0.0, 0.0),
        orthographic_scale=12.2,
    )
    create_camera(
        "V2 Plan Server",
        (DIMS.service_x, DIMS.server_center_y, 8.0),
        (DIMS.service_x, DIMS.server_center_y, 0.0),
        orthographic_scale=4.8,
    )

    configure_scene()
    scene = bpy.context.scene
    scene.camera = hero_camera
    scene["hubmann_v2_stage"] = BUILD_STAGE
    scene["hubmann_v2_reference"] = str(REFERENCE_PATH)
    scene["hubmann_v2_dimensions"] = repr(DIMS)
    return materials


def build_phase1a(materials: dict[str, bpy.types.Material]) -> None:
    """Build only the approved V2 massing and load-bearing shell."""
    concrete = materials["concrete"]
    plaster = materials["plaster"]
    oak = materials["oak"]
    charcoal = materials["charcoal"]
    qa_floor = materials["qa_floor"]

    house_center_y = (DIMS.ground_front_y + DIMS.ground_rear_y) / 2
    house_half_width = DIMS.width / 2
    house_depth = DIMS.ground_rear_y - DIMS.ground_front_y

    # Grounded plinth, projecting terraces and three broad entrance treads.
    add_box(
        "V2 Foundation raft",
        (0.0, house_center_y, 0.02),
        (10.20, house_depth + 0.66, 0.34),
        concrete,
        collection="V2 STRUCTURE",
        bevel=0.025,
    )
    add_box(
        "V2 Front terrace",
        (0.0, DIMS.ground_front_y - 0.42, 0.17),
        (10.95, 1.08, 0.24),
        concrete,
        collection="V2 STRUCTURE",
        bevel=0.022,
    )
    for index, (width, depth, y, z) in enumerate(
        (
            (4.20, 0.62, -4.12, 0.03),
            (3.78, 0.62, -4.58, -0.10),
            (3.34, 0.62, -5.03, -0.23),
        )
    ):
        add_box(
            f"V2 Entrance step {index + 1}",
            (-2.05, y, z),
            (width, depth, 0.18),
            concrete,
            collection="V2 STRUCTURE",
            bevel=0.018,
        )

    # A few deliberate foundation piers reproduce the lifted right-hand slab
    # visible in the mockup without detailing the full structural design.
    for index, x in enumerate((-3.95, -1.30, 1.35, 4.00)):
        add_box(
            f"V2 Foundation pier {index + 1}",
            (x, DIMS.ground_rear_y - 0.32, -0.28),
            (0.46, 0.58, 0.54),
            concrete,
            collection="V2 STRUCTURE",
            bevel=0.018,
        )

    # Two expressive concrete trays and the upper roof-bearing plate define
    # the image before any facade or interior detail is allowed to appear.
    add_box(
        "V2 Upper floor tray",
        (0.0, house_center_y, DIMS.upper_finish_z - 0.19),
        (10.05, house_depth + 0.38, 0.38),
        concrete,
        collection="V2 STRUCTURE",
        bevel=0.026,
    )
    add_box(
        "V2 Upper ceiling tray",
        (0.0, house_center_y, DIMS.upper_ceiling_z - 0.13),
        (9.72, house_depth + 0.10, 0.28),
        concrete,
        collection="V2 STRUCTURE",
        bevel=0.024,
    )

    column_size = 0.30
    lower_column_height = DIMS.upper_finish_z - DIMS.ground_finish_z - 0.22
    lower_column_z = DIMS.ground_finish_z + lower_column_height / 2
    upper_column_height = DIMS.upper_ceiling_z - DIMS.upper_finish_z - 0.18
    upper_column_z = DIMS.upper_finish_z + upper_column_height / 2
    column_positions = (
        (-house_half_width + 0.16, DIMS.ground_front_y + 0.17),
        (house_half_width - 0.16, DIMS.ground_front_y + 0.17),
        (-house_half_width + 0.16, DIMS.ground_rear_y - 0.17),
        (house_half_width - 0.16, DIMS.ground_rear_y - 0.17),
    )
    for index, (x, y) in enumerate(column_positions):
        add_box(
            f"V2 Ground column {index + 1}",
            (x, y, lower_column_z),
            (column_size, column_size, lower_column_height),
            concrete,
            collection="V2 STRUCTURE",
            bevel=0.018,
        )
        add_box(
            f"V2 Upper column {index + 1}",
            (x, y, upper_column_z),
            (column_size, column_size, upper_column_height),
            concrete,
            collection="V2 STRUCTURE",
            bevel=0.018,
        )

    # Rear and left infill masses establish the cutaway volume. They are
    # placeholders only; phase 1B replaces facade masses with real openings.
    ground_wall_z = (DIMS.ground_finish_z + DIMS.upper_finish_z) / 2
    ground_wall_height = DIMS.upper_finish_z - DIMS.ground_finish_z - 0.28
    upper_wall_z = (DIMS.upper_finish_z + DIMS.upper_ceiling_z) / 2
    upper_wall_height = DIMS.upper_ceiling_z - DIMS.upper_finish_z - 0.25
    add_box(
        "V2 Ground rear infill",
        (0.0, DIMS.ground_rear_y - 0.10, ground_wall_z),
        (DIMS.width - 0.38, 0.20, ground_wall_height),
        plaster,
        collection="V2 EXTERIOR",
        bevel=0.014,
    )
    add_box(
        "V2 Ground left infill",
        (-house_half_width + 0.10, house_center_y, ground_wall_z),
        (0.20, house_depth - 0.38, ground_wall_height),
        plaster,
        collection="V2 EXTERIOR",
        bevel=0.014,
    )
    add_box(
        "V2 Upper rear infill",
        (0.0, DIMS.ground_rear_y - 0.10, upper_wall_z),
        (DIMS.width - 0.38, 0.20, upper_wall_height),
        plaster,
        collection="V2 EXTERIOR",
        bevel=0.014,
    )
    add_box(
        "V2 Upper left infill",
        (-house_half_width + 0.10, house_center_y, upper_wall_z),
        (0.20, house_depth - 0.38, upper_wall_height),
        plaster,
        collection="V2 EXTERIOR",
        bevel=0.014,
    )

    # Dedicated below-grade server cell aligned with the future distribution
    # cabinet. The front remains open for the canonical cutaway camera.
    server_x_min = DIMS.service_x - DIMS.server_width / 2
    server_x_max = DIMS.service_x + DIMS.server_width / 2
    server_y_max = DIMS.server_center_y + DIMS.server_depth / 2
    server_wall_height = DIMS.server_ceiling_z - DIMS.server_floor_z
    server_wall_z = (DIMS.server_ceiling_z + DIMS.server_floor_z) / 2
    add_box(
        "V2 Server floor",
        (DIMS.service_x, DIMS.server_center_y, DIMS.server_floor_z),
        (DIMS.server_width, DIMS.server_depth, 0.16),
        concrete,
        collection="V2 STRUCTURE",
        bevel=0.018,
    )
    for name, x in (("left", server_x_min + 0.07), ("right", server_x_max - 0.07)):
        add_box(
            f"V2 Server {name} wall",
            (x, DIMS.server_center_y, server_wall_z),
            (0.14, DIMS.server_depth, server_wall_height),
            concrete,
            collection="V2 STRUCTURE",
            bevel=0.018,
        )
    add_box(
        "V2 Server rear wall",
        (DIMS.service_x, server_y_max - 0.07, server_wall_z),
        (DIMS.server_width, 0.14, server_wall_height),
        concrete,
        collection="V2 STRUCTURE",
        bevel=0.018,
    )

    # One coherent roof assembly. The black weather skin sits on a slightly
    # larger warm-oak underlay so its construction reads from below.
    roof_half_span = house_half_width + DIMS.roof_overhang_x
    roof_rise = DIMS.roof_ridge_z - DIMS.roof_eave_z
    roof_angle = math.atan2(roof_rise, roof_half_span)
    roof_slope_length = math.hypot(roof_half_span, roof_rise)
    roof_depth = house_depth + 2 * DIMS.roof_overhang_y
    roof_center_z = (DIMS.roof_ridge_z + DIMS.roof_eave_z) / 2
    for side, x, angle in (
        ("left", -roof_half_span / 2, -roof_angle),
        ("right", roof_half_span / 2, roof_angle),
    ):
        add_box(
            f"V2 Roof timber {side}",
            (x, house_center_y, roof_center_z - 0.10),
            (roof_slope_length, roof_depth, 0.18),
            oak,
            collection="V2 STRUCTURE",
            rotation=(0.0, angle, 0.0),
            bevel=0.022,
        )
        add_box(
            f"V2 Roof skin {side}",
            (x, house_center_y, roof_center_z + 0.02),
            (roof_slope_length + 0.08, roof_depth + 0.06, 0.12),
            charcoal,
            collection="V2 EXTERIOR",
            rotation=(0.0, angle, 0.0),
            bevel=0.018,
        )

    pv_x = 2.45
    pv_surface_z = DIMS.roof_ridge_z - roof_rise * (pv_x / roof_half_span)
    add_box(
        "V2 PV massing",
        (pv_x, house_center_y + 0.45, pv_surface_z + 0.16),
        (3.75, 3.55, 0.10),
        charcoal,
        collection="V2 TECHNICAL",
        rotation=(0.0, roof_angle, 0.0),
        bevel=0.026,
    )

    # A conventional white floor still renders grey wherever it receives the
    # studio lights.  The feathered ellipse supplies only the desired grounding
    # shadow, while the actual background remains uniformly white.
    add_soft_contact_shadow(
        "V2 QA contact shadow",
        location=(0.45, -3.20, 0.02),
        radius_x=7.20,
        radius_y=2.60,
        collection="V2 QA",
    )
    light_target = (0.0, -0.2, 3.25)
    add_area_light(
        "V2 QA key",
        (-8.0, -11.0, 17.0),
        light_target,
        energy=620.0,
        size=7.0,
        color=(1.0, 0.92, 0.82),
    )
    add_area_light(
        "V2 QA fill",
        (12.0, -3.0, 11.0),
        light_target,
        energy=145.0,
        size=9.0,
        color=(0.84, 0.91, 1.0),
    )
    add_area_light(
        "V2 QA rear",
        (-4.0, 10.0, 13.0),
        light_target,
        energy=240.0,
        size=7.0,
        color=(1.0, 0.88, 0.72),
    )


def build_phase1b(materials: dict[str, bpy.types.Material]) -> None:
    """Replace placeholder infills with collision-free facade and plan zones."""
    plaster = materials["plaster"]
    oak = materials["oak"]
    plan_text = materials["plan_text"]

    remove_objects_with_prefix(
        "V2 Ground rear infill",
        "V2 Ground left infill",
        "V2 Upper rear infill",
        "V2 Upper left infill",
    )

    x_min = -DIMS.width / 2 + 0.10
    x_max = DIMS.width / 2 - 0.10
    y_min = DIMS.ground_front_y + 0.10
    y_max = DIMS.ground_rear_y - 0.10
    ground_floor = DIMS.ground_finish_z
    ground_ceiling = DIMS.upper_finish_z - 0.19
    upper_floor = DIMS.upper_finish_z
    upper_ceiling = DIMS.upper_ceiling_z - 0.14

    # The removable front facade is kept in its own collection. Canonical
    # cutaways hide it; facade QA turns it on as one coherent skin.
    add_wall_x_with_openings(
        "V2 Facade front ground",
        x_min=x_min,
        x_max=x_max,
        y=DIMS.ground_front_y + 0.08,
        z_floor=ground_floor,
        z_ceiling=ground_ceiling,
        openings=(
            (-3.05, 1.95, 0.48, 2.36),
            (-0.25, 1.02, ground_floor, 2.32),
            (2.85, 2.15, 0.48, 2.36),
        ),
        material=plaster,
        collection="V2 FACADE",
    )
    add_wall_x_with_openings(
        "V2 Facade front upper",
        x_min=x_min,
        x_max=x_max,
        y=DIMS.ground_front_y + 0.08,
        z_floor=upper_floor,
        z_ceiling=upper_ceiling,
        openings=(
            (-3.05, 1.80, 3.95, 1.65),
            (1.75, 1.15, 4.10, 1.35),
            (3.55, 0.82, 4.00, 1.60),
        ),
        material=plaster,
        collection="V2 FACADE",
    )
    add_triangular_prism(
        "V2 Facade front gable",
        center_x=0.0,
        y=DIMS.ground_front_y + 0.08,
        base_z=upper_ceiling - 0.02,
        width=DIMS.width - 0.20,
        height=DIMS.roof_ridge_z - upper_ceiling - 0.18,
        thickness=0.18,
        material=plaster,
        collection="V2 FACADE",
    )

    # Rear facade: dedicated window openings avoid later wall/window overlap.
    add_wall_x_with_openings(
        "V2 Exterior rear ground",
        x_min=x_min,
        x_max=x_max,
        y=DIMS.ground_rear_y - 0.08,
        z_floor=ground_floor,
        z_ceiling=ground_ceiling,
        openings=((3.15, 1.40, 1.02, 1.28),),
        material=plaster,
        collection="V2 EXTERIOR",
    )
    add_wall_x_with_openings(
        "V2 Exterior rear upper",
        x_min=x_min,
        x_max=x_max,
        y=DIMS.ground_rear_y - 0.08,
        z_floor=upper_floor,
        z_ceiling=upper_ceiling,
        openings=(
            (-3.05, 1.50, 4.08, 1.42),
            (1.82, 0.88, 4.42, 0.78),
        ),
        material=plaster,
        collection="V2 EXTERIOR",
    )

    # Both side facades use segmented wall blocks. On the important right
    # elevation the lamella layer sits beside, never across, the window void.
    add_wall_y_with_openings(
        "V2 Exterior left ground",
        x=x_min,
        y_min=y_min,
        y_max=y_max,
        z_floor=ground_floor,
        z_ceiling=ground_ceiling,
        openings=((0.45, 1.65, 0.88, 1.52),),
        material=plaster,
        collection="V2 EXTERIOR",
    )
    add_wall_y_with_openings(
        "V2 Exterior left upper",
        x=x_min,
        y_min=y_min,
        y_max=y_max,
        z_floor=upper_floor,
        z_ceiling=upper_ceiling,
        openings=((0.75, 1.55, 4.08, 1.48),),
        material=plaster,
        collection="V2 EXTERIOR",
    )
    add_wall_y_with_openings(
        "V2 Exterior right ground",
        x=x_max,
        y_min=y_min,
        y_max=y_max,
        z_floor=ground_floor,
        z_ceiling=ground_ceiling,
        openings=((1.90, 1.55, 0.88, 1.52),),
        material=plaster,
        collection="V2 EXTERIOR",
    )
    add_wall_y_with_openings(
        "V2 Exterior right upper",
        x=x_max,
        y_min=y_min,
        y_max=y_max,
        z_floor=upper_floor,
        z_ceiling=upper_ceiling,
        openings=((1.95, 1.35, 4.08, 1.48),),
        material=plaster,
        collection="V2 EXTERIOR",
    )

    right_window_min = 1.95 - 1.35 / 2
    right_window_max = 1.95 + 1.35 / 2
    slat_positions = (
        right_window_min - 0.42,
        right_window_min - 0.24,
        right_window_min - 0.06,
        right_window_max + 0.06,
        right_window_max + 0.24,
        right_window_max + 0.42,
    )
    for index, y in enumerate(slat_positions):
        add_box(
            f"V2 Exterior right upper slat {index + 1}",
            (x_max + 0.13, y, 4.92),
            (0.10, 0.085, 2.20),
            oak,
            collection="V2 EXTERIOR",
            bevel=0.012,
        )

    # Plan zones encode the visual room hierarchy before partitions or
    # furniture are introduced. They render only in orthographic QA views.
    plan_z_ground = ground_floor + 0.035
    add_plan_zone(
        "Ground living",
        "WOHNEN",
        (-2.80, 0.15),
        (3.25, 6.65),
        plan_z_ground,
        materials["plan_living"],
        plan_text,
    )
    add_plan_zone(
        "Ground circulation",
        "EINGANG / TREPPE",
        (-0.22, 0.15),
        (1.68, 6.65),
        plan_z_ground,
        materials["plan_circulation"],
        plan_text,
    )
    add_plan_zone(
        "Ground service",
        "VERTEILUNG",
        (1.20, 1.55),
        (0.88, 2.55),
        plan_z_ground,
        materials["plan_service"],
        plan_text,
    )
    add_plan_zone(
        "Ground dining",
        "ESSEN",
        (3.02, -1.15),
        (2.55, 3.85),
        plan_z_ground,
        materials["plan_kitchen"],
        plan_text,
    )
    add_plan_zone(
        "Ground kitchen",
        "KUECHE",
        (3.02, 2.10),
        (2.55, 2.45),
        plan_z_ground,
        materials["plan_kitchen"],
        plan_text,
    )

    plan_z_upper = upper_floor + 0.035
    add_plan_zone(
        "Upper bedroom",
        "SCHLAFEN",
        (-2.80, 0.15),
        (3.25, 6.65),
        plan_z_upper,
        materials["plan_bed"],
        plan_text,
    )
    add_plan_zone(
        "Upper circulation",
        "FLUR / TREPPE",
        (-0.22, 0.15),
        (1.68, 6.65),
        plan_z_upper,
        materials["plan_circulation"],
        plan_text,
    )
    add_plan_zone(
        "Upper bathroom",
        "BAD",
        (3.58, 0.15),
        (2.12, 6.65),
        plan_z_upper,
        materials["plan_bath"],
        plan_text,
    )
    add_plan_zone(
        "Upper gallery",
        "GALERIE",
        (1.61, 0.15),
        (1.50, 6.65),
        plan_z_upper,
        materials["plan_gallery"],
        plan_text,
    )

    add_plan_zone(
        "Server",
        "SERVER",
        (DIMS.service_x, DIMS.server_center_y),
        (DIMS.server_width - 0.28, DIMS.server_depth - 0.28),
        DIMS.server_floor_z + 0.095,
        materials["plan_service"],
        plan_text,
    )

    bpy.data.collections["V2 PLAN"].hide_render = True


def build_phase2a(materials: dict[str, bpy.types.Material]) -> None:
    """Add the real stair void, partitions, doors, windows and straight stair."""
    concrete = materials["concrete"]
    plaster = materials["plaster"]
    oak = materials["oak"]
    charcoal = materials["charcoal"]
    glass = materials["glass"]

    # Replace the monolithic upper slab with four collision-free pieces around
    # one real stair opening.
    remove_objects_with_prefix("V2 Upper floor tray")
    house_center_y = (DIMS.ground_front_y + DIMS.ground_rear_y) / 2
    outer_x_min = -5.025
    outer_x_max = 5.025
    outer_y_min = house_center_y - (DIMS.depth + 0.38) / 2
    outer_y_max = house_center_y + (DIMS.depth + 0.38) / 2
    opening_x_min = -0.74
    opening_x_max = 0.64
    opening_y_min = 0.15
    opening_y_max = 3.40
    slab_z = DIMS.upper_finish_z - 0.19
    slab_height = 0.38
    add_box(
        "V2 Upper floor tray left",
        ((outer_x_min + opening_x_min) / 2, house_center_y, slab_z),
        (opening_x_min - outer_x_min, outer_y_max - outer_y_min, slab_height),
        concrete,
        collection="V2 STRUCTURE",
        bevel=0.026,
    )
    add_box(
        "V2 Upper floor tray right",
        ((opening_x_max + outer_x_max) / 2, house_center_y, slab_z),
        (outer_x_max - opening_x_max, outer_y_max - outer_y_min, slab_height),
        concrete,
        collection="V2 STRUCTURE",
        bevel=0.026,
    )
    add_box(
        "V2 Upper floor tray stair front",
        (
            (opening_x_min + opening_x_max) / 2,
            (outer_y_min + opening_y_min) / 2,
            slab_z,
        ),
        (
            opening_x_max - opening_x_min,
            opening_y_min - outer_y_min,
            slab_height,
        ),
        concrete,
        collection="V2 STRUCTURE",
        bevel=0.026,
    )
    add_box(
        "V2 Upper floor tray stair rear",
        (
            (opening_x_min + opening_x_max) / 2,
            (opening_y_max + outer_y_max) / 2,
            slab_z,
        ),
        (
            opening_x_max - opening_x_min,
            outer_y_max - opening_y_max,
            slab_height,
        ),
        concrete,
        collection="V2 STRUCTURE",
        bevel=0.026,
    )

    ground_floor = DIMS.ground_finish_z
    ground_ceiling = DIMS.upper_finish_z - 0.19
    upper_floor = DIMS.upper_finish_z
    upper_ceiling = DIMS.upper_ceiling_z - 0.14

    # Ground-floor partitions stop before the open cutaway edge and leave a
    # generous shared front zone, as in the mockup.
    for name, x in (("living hall", -1.15), ("hall dining", 1.02)):
        add_wall_y_with_openings(
            f"V2 Ground partition {name}",
            x=x,
            y_min=0.62,
            y_max=DIMS.ground_rear_y - 0.18,
            z_floor=ground_floor,
            z_ceiling=ground_ceiling,
            openings=((2.55, 0.90, ground_floor, 2.18),),
            material=plaster,
            collection="V2 INTERIOR",
            thickness=0.14,
        )

    # Upper rooms run left-to-right: bedroom, circulation, gallery, bathroom.
    for name, x in (
        ("bedroom hall", -1.15),
        ("hall gallery", 0.76),
        ("gallery bathroom", 2.45),
    ):
        add_wall_y_with_openings(
            f"V2 Upper partition {name}",
            x=x,
            y_min=0.30,
            y_max=DIMS.ground_rear_y - 0.18,
            z_floor=upper_floor,
            z_ceiling=upper_ceiling,
            openings=((2.55, 0.88, upper_floor, 2.10),),
            material=plaster,
            collection="V2 INTERIOR",
            thickness=0.14,
        )

    # Straight timber stair inside the actual slab void.
    stair_count = 17
    stair_run = opening_y_max - opening_y_min
    tread = stair_run / stair_count
    rise = (DIMS.upper_finish_z - DIMS.ground_finish_z) / stair_count
    for index in range(stair_count):
        top_z = DIMS.ground_finish_z + rise * (index + 1)
        y = opening_y_min + tread * (index + 0.5)
        add_box(
            f"V2 Stair tread {index + 1:02d}",
            (-0.05, y, top_z - 0.065),
            (1.08, tread + 0.025, 0.13),
            oak,
            collection="V2 INTERIOR",
            bevel=0.018,
        )
    for x in (-0.48, 0.38):
        add_beam_between(
            f"V2 Stair stringer {x:+.2f}",
            (x, opening_y_min + 0.08, DIMS.ground_finish_z + 0.10),
            (x, opening_y_max - 0.08, DIMS.upper_finish_z - 0.10),
            thickness=0.09,
            material=oak,
            collection="V2 INTERIOR",
        )
    rail_x = -0.66
    for index in (0, 4, 8, 12, 16):
        y = opening_y_min + tread * (index + 0.5)
        tread_top = DIMS.ground_finish_z + rise * (index + 1)
        add_box(
            f"V2 Stair rail post {index + 1:02d}",
            (rail_x, y, tread_top + 0.48),
            (0.055, 0.055, 0.96),
            charcoal,
            collection="V2 INTERIOR",
            bevel=0.010,
        )
    add_beam_between(
        "V2 Stair handrail",
        (rail_x, opening_y_min + 0.10, DIMS.ground_finish_z + 1.00),
        (rail_x, opening_y_max - 0.10, DIMS.upper_finish_z + 0.94),
        thickness=0.075,
        material=oak,
        collection="V2 INTERIOR",
    )
    for y in (opening_y_min - 0.05, opening_y_max + 0.05):
        add_box(
            f"V2 Upper stair guard rail {y:+.2f}",
            (-0.05, y, DIMS.upper_finish_z + 0.94),
            (1.42, 0.065, 0.065),
            oak,
            collection="V2 INTERIOR",
            bevel=0.012,
        )
        for x in (-0.70, -0.05, 0.60):
            add_box(
                f"V2 Upper stair guard post {y:+.2f} {x:+.2f}",
                (x, y, DIMS.upper_finish_z + 0.47),
                (0.055, 0.055, 0.94),
                charcoal,
                collection="V2 INTERIOR",
                bevel=0.010,
            )

    # Front facade frames and entrance door.
    add_window_x(
        "V2 Facade ground living window",
        center_x=-3.05,
        y=DIMS.ground_front_y - 0.015,
        bottom=0.48,
        width=1.95,
        height=2.36,
        frame=charcoal,
        glass=glass,
        collection="V2 FACADE",
    )
    add_door_x(
        "V2 Facade entrance door",
        center_x=-0.25,
        y=DIMS.ground_front_y - 0.015,
        bottom=ground_floor,
        width=1.02,
        height=2.32,
        material=oak,
        frame=charcoal,
        collection="V2 FACADE",
    )
    add_window_x(
        "V2 Facade ground dining window",
        center_x=2.85,
        y=DIMS.ground_front_y - 0.015,
        bottom=0.48,
        width=2.15,
        height=2.36,
        frame=charcoal,
        glass=glass,
        collection="V2 FACADE",
    )
    for suffix, center_x, width, bottom, height in (
        ("bedroom", -3.05, 1.80, 3.95, 1.65),
        ("bathroom", 1.75, 1.15, 4.10, 1.35),
        ("gallery", 3.55, 0.82, 4.00, 1.60),
    ):
        add_window_x(
            f"V2 Facade upper {suffix} window",
            center_x=center_x,
            y=DIMS.ground_front_y - 0.015,
            bottom=bottom,
            width=width,
            height=height,
            frame=charcoal,
            glass=glass,
            collection="V2 FACADE",
        )

    # Rear and side frames sit exactly inside the openings built in phase 1B.
    add_window_x(
        "V2 Exterior rear ground kitchen window",
        center_x=3.15,
        y=DIMS.ground_rear_y - 0.015,
        bottom=1.02,
        width=1.40,
        height=1.28,
        frame=charcoal,
        glass=glass,
        collection="V2 EXTERIOR",
    )
    for suffix, center_x, width, bottom, height in (
        ("bedroom", -3.05, 1.50, 4.08, 1.42),
        ("bathroom", 1.82, 0.88, 4.42, 0.78),
    ):
        add_window_x(
            f"V2 Exterior rear upper {suffix} window",
            center_x=center_x,
            y=DIMS.ground_rear_y - 0.015,
            bottom=bottom,
            width=width,
            height=height,
            frame=charcoal,
            glass=glass,
            collection="V2 EXTERIOR",
        )
    for side, x in (("left", -DIMS.width / 2 + 0.015), ("right", DIMS.width / 2 - 0.015)):
        ground_y = 0.45 if side == "left" else 1.90
        upper_y = 0.75 if side == "left" else 1.95
        upper_width = 1.55 if side == "left" else 1.35
        add_window_y(
            f"V2 Exterior {side} ground window",
            x=x,
            center_y=ground_y,
            bottom=0.88,
            width=1.65 if side == "left" else 1.55,
            height=1.52,
            frame=charcoal,
            glass=glass,
            collection="V2 EXTERIOR",
        )
        add_window_y(
            f"V2 Exterior {side} upper window",
            x=x,
            center_y=upper_y,
            bottom=4.08,
            width=upper_width,
            height=1.48,
            frame=charcoal,
            glass=glass,
            collection="V2 EXTERIOR",
        )

    # Interior door leaves occupy the prepared voids rather than intersecting
    # the partitions.
    for name, x, bottom in (
        ("V2 Ground living door", -1.15, ground_floor),
        ("V2 Ground dining door", 1.02, ground_floor),
        ("V2 Upper bedroom door", -1.15, upper_floor),
        ("V2 Upper gallery door", 0.76, upper_floor),
        ("V2 Upper bathroom door", 2.45, upper_floor),
    ):
        add_door_y(
            name,
            x=x,
            center_y=2.55,
            bottom=bottom,
            width=0.88 if "Upper" in name else 0.90,
            height=2.10 if "Upper" in name else 2.18,
            material=oak,
            frame=charcoal,
            collection="V2 INTERIOR",
        )

    add_plan_zone(
        "Upper stair void",
        "TREPPENLOCH",
        ((opening_x_min + opening_x_max) / 2, (opening_y_min + opening_y_max) / 2),
        (opening_x_max - opening_x_min - 0.08, opening_y_max - opening_y_min - 0.08),
        DIMS.upper_finish_z + 0.075,
        materials["qa_floor"],
        materials["plan_text"],
    )
    remove_objects_with_prefix("V2 Plan Upper circulation label")
    add_plan_label(
        "V2 Plan Upper circulation label",
        "FLUR",
        (-0.22, -2.45, DIMS.upper_finish_z + 0.105),
        materials["plan_text"],
        size=0.22,
    )
    label_adjustments = (
        ("V2 Plan Ground living label", "WOHNEN", -3.00, -2.45, 0.24),
        ("V2 Plan Ground circulation label", "EINGANG", -0.22, -2.55, 0.15),
        ("V2 Plan Ground service label", "VERTEILER", 1.20, 2.45, 0.11),
        ("V2 Plan Upper bedroom label", "SCHLAFEN", -3.00, -2.45, 0.23),
        ("V2 Plan Upper gallery label", "GALERIE", 1.61, -2.25, 0.15),
        ("V2 Plan Server label", "SERVER", DIMS.service_x, -3.90, 0.20),
    )
    for name, text, x, y, size in label_adjustments:
        label = bpy.data.objects.get(name)
        if label is not None:
            label.data.body = text
            label.data.size = size
            label.location.x = x
            label.location.y = y


def build_phase2b(materials: dict[str, bpy.types.Material]) -> None:
    """Populate every V2 room with readable low-detail furniture silhouettes."""
    oak = materials["oak"]
    floor_oak = materials["floor_oak"]
    upholstery = materials["upholstery"]
    charcoal = materials["charcoal"]
    glass = materials["glass"]
    porcelain = materials["porcelain"]
    tile = materials["tile"]
    plant = materials["plant"]
    service_red = materials["service_red"]
    tech_blue = materials["tech_blue"]

    ground_floor = DIMS.ground_finish_z
    upper_floor = DIMS.upper_finish_z

    # Finish surfaces are thin and stay below furniture contact points.
    add_box(
        "V2 Ground oak finish",
        (0.0, 0.15, ground_floor - 0.035),
        (8.95, 6.92, 0.07),
        floor_oak,
        collection="V2 INTERIOR",
        bevel=0.010,
    )
    add_box(
        "V2 Upper bedroom oak finish",
        (-2.80, 0.15, upper_floor - 0.025),
        (3.25, 6.65, 0.05),
        floor_oak,
        collection="V2 INTERIOR",
        bevel=0.010,
    )
    add_box(
        "V2 Upper bathroom tile finish",
        (3.58, 0.15, upper_floor + 0.012),
        (2.02, 6.65, 0.045),
        tile,
        collection="V2 INTERIOR",
        bevel=0.010,
    )
    add_box(
        "V2 Upper gallery oak finish",
        (1.61, 0.15, upper_floor - 0.025),
        (1.50, 6.65, 0.05),
        floor_oak,
        collection="V2 INTERIOR",
        bevel=0.010,
    )

    # Living room: broad sofa, one chair, coffee table and TV wall establish
    # the same left-heavy silhouette as the reference.
    add_box(
        "V2 Ground living sofa base",
        (-3.05, 2.35, 0.57),
        (2.35, 0.86, 0.42),
        upholstery,
        collection="V2 FURNITURE",
        bevel=0.10,
    )
    add_box(
        "V2 Ground living sofa back",
        (-3.05, 2.72, 1.00),
        (2.35, 0.20, 0.88),
        upholstery,
        collection="V2 FURNITURE",
        bevel=0.08,
    )
    for side, x in (("left", -4.17), ("right", -1.93)):
        add_box(
            f"V2 Ground living sofa arm {side}",
            (x, 2.34, 0.80),
            (0.18, 0.84, 0.68),
            upholstery,
            collection="V2 FURNITURE",
            bevel=0.07,
        )
    add_box(
        "V2 Ground living chair seat",
        (-1.95, -0.75, 0.62),
        (0.82, 0.82, 0.38),
        upholstery,
        collection="V2 FURNITURE",
        rotation=(0.0, 0.0, math.radians(-18.0)),
        bevel=0.10,
    )
    add_box(
        "V2 Ground living chair back",
        (-1.82, -0.48, 1.02),
        (0.78, 0.18, 0.82),
        upholstery,
        collection="V2 FURNITURE",
        rotation=(0.0, 0.0, math.radians(-18.0)),
        bevel=0.08,
    )
    add_box(
        "V2 Ground living coffee table top",
        (-3.05, 0.40, 0.67),
        (1.45, 0.72, 0.09),
        oak,
        collection="V2 FURNITURE",
        bevel=0.035,
    )
    for x in (-3.62, -2.48):
        for y in (0.13, 0.67):
            add_box(
                f"V2 Ground living coffee table leg {x:+.2f} {y:+.2f}",
                (x, y, 0.48),
                (0.055, 0.055, 0.36),
                charcoal,
                collection="V2 FURNITURE",
                bevel=0.008,
            )
    add_box(
        "V2 Ground living TV console",
        (-1.32, 1.40, 0.64),
        (0.36, 1.70, 0.58),
        oak,
        collection="V2 FURNITURE",
        bevel=0.035,
    )
    add_box(
        "V2 Ground living TV",
        (-1.24, 1.40, 1.45),
        (0.075, 1.42, 0.82),
        charcoal,
        collection="V2 FURNITURE",
        bevel=0.035,
    )
    add_cylinder(
        "V2 Ground living plant pot",
        (-4.05, 1.05, 0.56),
        radius=0.23,
        depth=0.50,
        material=oak,
        collection="V2 FURNITURE",
    )
    for index, (x, y, z, scale) in enumerate(
        (
            (-4.05, 1.05, 1.02, 0.30),
            (-4.18, 1.02, 1.24, 0.23),
            (-3.94, 1.07, 1.35, 0.21),
        )
    ):
        add_cylinder(
            f"V2 Ground living plant leaf {index + 1}",
            (x, y, z),
            radius=scale,
            depth=0.12,
            material=plant,
            collection="V2 FURNITURE",
            vertices=16,
        )

    # Dining table and six intentionally simple chairs.
    add_box(
        "V2 Ground dining table top",
        (2.92, -0.75, 1.06),
        (1.78, 1.02, 0.12),
        oak,
        collection="V2 FURNITURE",
        bevel=0.035,
    )
    for x in (2.20, 3.64):
        for y in (-1.13, -0.37):
            add_box(
                f"V2 Ground dining table leg {x:+.2f} {y:+.2f}",
                (x, y, 0.68),
                (0.075, 0.075, 0.72),
                charcoal,
                collection="V2 FURNITURE",
                bevel=0.010,
            )
    chair_locations = (
        (2.28, -1.57, -1),
        (2.92, -1.57, -1),
        (3.56, -1.57, -1),
        (2.28, 0.07, 1),
        (2.92, 0.07, 1),
        (3.56, 0.07, 1),
    )
    for index, (x, y, facing) in enumerate(chair_locations):
        add_box(
            f"V2 Ground dining chair {index + 1} seat",
            (x, y, 0.76),
            (0.46, 0.48, 0.13),
            upholstery,
            collection="V2 FURNITURE",
            bevel=0.045,
        )
        add_box(
            f"V2 Ground dining chair {index + 1} back",
            (x, y - 0.21 * facing, 1.07),
            (0.46, 0.10, 0.66),
            upholstery,
            collection="V2 FURNITURE",
            bevel=0.045,
        )
        for dx in (-0.17, 0.17):
            add_box(
                f"V2 Ground dining chair {index + 1} leg {dx:+.2f}",
                (x + dx, y, 0.51),
                (0.045, 0.045, 0.46),
                charcoal,
                collection="V2 FURNITURE",
                bevel=0.008,
            )

    # Compact rear kitchen, kept below and beside the real rear window.
    add_box(
        "V2 Ground kitchen base cabinets",
        (3.20, 3.34, 0.72),
        (1.85, 0.58, 0.82),
        oak,
        collection="V2 FURNITURE",
        bevel=0.035,
    )
    add_box(
        "V2 Ground kitchen worktop",
        (3.20, 3.31, 1.17),
        (2.00, 0.66, 0.09),
        charcoal,
        collection="V2 FURNITURE",
        bevel=0.025,
    )
    add_box(
        "V2 Ground kitchen tall cabinet",
        (4.05, 2.72, 1.48),
        (0.64, 0.64, 2.28),
        oak,
        collection="V2 FURNITURE",
        bevel=0.035,
    )
    add_box(
        "V2 Ground kitchen oven",
        (4.05, 2.38, 1.48),
        (0.46, 0.055, 0.62),
        charcoal,
        collection="V2 FURNITURE",
        bevel=0.018,
    )

    # Open distribution cabinet located on the common server/bath/PV axis.
    cabinet_x = DIMS.service_x
    cabinet_y = 0.95
    add_box(
        "V2 Ground distribution cabinet back",
        (cabinet_x, cabinet_y, 1.62),
        (0.88, 0.18, 2.34),
        charcoal,
        collection="V2 TECHNICAL",
        bevel=0.035,
    )
    add_box(
        "V2 Ground distribution cabinet interior",
        (cabinet_x, cabinet_y - 0.13, 1.62),
        (0.72, 0.08, 2.12),
        tech_blue,
        collection="V2 TECHNICAL",
        bevel=0.018,
    )
    for row in range(6):
        z = 0.78 + row * 0.30
        add_box(
            f"V2 Ground distribution breaker rail {row + 1}",
            (cabinet_x, cabinet_y - 0.195, z),
            (0.58, 0.055, 0.13),
            materials["concrete"],
            collection="V2 TECHNICAL",
            bevel=0.010,
        )
        for slot in range(5):
            add_box(
                f"V2 Ground distribution breaker {row + 1}-{slot + 1}",
                (cabinet_x - 0.24 + slot * 0.12, cabinet_y - 0.235, z),
                (0.075, 0.035, 0.07),
                service_red if slot in (0, 4) else charcoal,
                collection="V2 TECHNICAL",
                bevel=0.006,
            )
    add_box(
        "V2 Ground distribution open door",
        (cabinet_x + 0.68, cabinet_y - 0.41, 1.62),
        (0.055, 0.72, 2.30),
        charcoal,
        collection="V2 TECHNICAL",
        rotation=(0.0, 0.0, math.radians(-28.0)),
        bevel=0.025,
    )

    # Bedroom furniture.
    add_box(
        "V2 Upper bedroom bed frame",
        (-3.05, 1.35, 3.70),
        (1.92, 2.18, 0.28),
        oak,
        collection="V2 FURNITURE",
        bevel=0.055,
    )
    add_box(
        "V2 Upper bedroom mattress",
        (-3.05, 1.32, 3.91),
        (1.82, 2.02, 0.26),
        upholstery,
        collection="V2 FURNITURE",
        bevel=0.11,
    )
    add_box(
        "V2 Upper bedroom headboard",
        (-3.05, 2.40, 4.20),
        (1.98, 0.16, 1.18),
        oak,
        collection="V2 FURNITURE",
        bevel=0.045,
    )
    for side, x in (("left", -3.55), ("right", -2.55)):
        add_box(
            f"V2 Upper bedroom pillow {side}",
            (x, 1.86, 4.12),
            (0.72, 0.45, 0.16),
            porcelain,
            collection="V2 FURNITURE",
            bevel=0.09,
        )
    for side, x in (("left", -4.28), ("right", -1.82)):
        add_box(
            f"V2 Upper bedroom nightstand {side}",
            (x, 2.10, 3.84),
            (0.48, 0.48, 0.62),
            oak,
            collection="V2 FURNITURE",
            bevel=0.035,
        )

    # Bathroom: shower, vanity, WC and a small tub make the room unmistakable.
    add_box(
        "V2 Upper bathroom vanity",
        (1.58, 3.32, 4.08),
        (1.20, 0.48, 0.92),
        oak,
        collection="V2 FURNITURE",
        bevel=0.035,
    )
    add_box(
        "V2 Upper bathroom basin",
        (1.58, 3.18, 4.57),
        (0.76, 0.38, 0.12),
        porcelain,
        collection="V2 FURNITURE",
        bevel=0.055,
    )
    add_box(
        "V2 Upper bathroom mirror",
        (1.58, 3.58, 5.18),
        (0.92, 0.045, 0.92),
        glass,
        collection="V2 FURNITURE",
        bevel=0.025,
    )
    add_box(
        "V2 Upper bathroom shower tray",
        (1.40, 1.55, 3.61),
        (1.02, 1.12, 0.14),
        porcelain,
        collection="V2 FURNITURE",
        bevel=0.045,
    )
    add_box(
        "V2 Upper bathroom shower glass rear",
        (1.40, 2.08, 4.58),
        (1.04, 0.04, 1.92),
        glass,
        collection="V2 FURNITURE",
        bevel=0.018,
    )
    add_box(
        "V2 Upper bathroom shower glass side",
        (0.90, 1.55, 4.58),
        (0.04, 1.08, 1.92),
        glass,
        collection="V2 FURNITURE",
        bevel=0.018,
    )
    add_cylinder(
        "V2 Upper bathroom toilet bowl",
        (2.44, -0.45, 3.83),
        radius=0.34,
        depth=0.38,
        material=porcelain,
        collection="V2 FURNITURE",
        vertices=32,
    )
    add_box(
        "V2 Upper bathroom toilet cistern",
        (2.44, -0.15, 4.12),
        (0.62, 0.24, 0.78),
        porcelain,
        collection="V2 FURNITURE",
        bevel=0.10,
    )
    add_box(
        "V2 Upper bathroom tub",
        (1.95, -2.45, 3.84),
        (1.72, 0.76, 0.62),
        porcelain,
        collection="V2 FURNITURE",
        bevel=0.16,
    )

    # The gallery remains intentionally narrow and furnished as circulation,
    # not mistaken for another empty room.
    add_box(
        "V2 Upper gallery bench",
        (3.78, 1.05, 3.82),
        (0.72, 1.58, 0.48),
        oak,
        collection="V2 FURNITURE",
        bevel=0.055,
    )
    add_box(
        "V2 Upper gallery cushion",
        (3.78, 1.05, 4.10),
        (0.66, 1.42, 0.16),
        upholstery,
        collection="V2 FURNITURE",
        bevel=0.08,
    )

    # Server cell: rack, visible server rows, UPS and cooling unit.
    rack_x = DIMS.service_x - 0.52
    add_box(
        "V2 Server rack shell",
        (rack_x, -4.64, -0.76),
        (0.78, 0.82, 1.52),
        charcoal,
        collection="V2 TECHNICAL",
        bevel=0.035,
    )
    add_box(
        "V2 Server rack face",
        (rack_x, -5.07, -0.76),
        (0.66, 0.045, 1.38),
        tech_blue,
        collection="V2 TECHNICAL",
        bevel=0.018,
    )
    for row in range(7):
        z = -1.30 + row * 0.18
        add_box(
            f"V2 Server rack unit {row + 1}",
            (rack_x, -5.105, z),
            (0.54, 0.035, 0.10),
            charcoal,
            collection="V2 TECHNICAL",
            bevel=0.008,
        )
        for light_index in range(3):
            add_box(
                f"V2 Server rack light {row + 1}-{light_index + 1}",
                (rack_x - 0.18 + light_index * 0.10, -5.13, z),
                (0.035, 0.018, 0.035),
                tech_blue,
                collection="V2 TECHNICAL",
                bevel=0.004,
            )
    add_box(
        "V2 Server UPS",
        (DIMS.service_x + 0.58, -4.96, -1.12),
        (0.62, 0.46, 0.72),
        charcoal,
        collection="V2 TECHNICAL",
        bevel=0.045,
    )
    add_box(
        "V2 Server cooling unit",
        (DIMS.service_x + 0.58, -4.18, -0.68),
        (0.68, 0.34, 1.42),
        porcelain,
        collection="V2 TECHNICAL",
        bevel=0.055,
    )
    add_cylinder(
        "V2 Server cooling fan",
        (DIMS.service_x + 0.58, -4.37, -0.58),
        radius=0.22,
        depth=0.06,
        material=charcoal,
        collection="V2 TECHNICAL",
        vertices=32,
    )


def build_rebuild_match_shell(materials: dict[str, bpy.types.Material]) -> None:
    """Apply the V2 mockup-driven shell rebuild after the functional blockout."""
    oak = materials["oak"]
    charcoal = materials["charcoal"]
    pv_blue = materials["pv_blue"]

    remove_objects_with_prefix("V2 Roof", "V2 PV")
    house_center_y = (DIMS.ground_front_y + DIMS.ground_rear_y) / 2
    house_half_width = DIMS.width / 2
    house_depth = DIMS.ground_rear_y - DIMS.ground_front_y
    roof_half_span = house_half_width + DIMS.roof_overhang_x
    roof_rise = DIMS.roof_ridge_z - DIMS.roof_eave_z
    roof_angle = math.atan2(roof_rise, roof_half_span)
    roof_slope_length = math.hypot(roof_half_span, roof_rise)
    roof_depth = house_depth + 2 * DIMS.roof_overhang_y
    roof_center_z = (DIMS.roof_ridge_z + DIMS.roof_eave_z) / 2

    # Thin plank lining plus exposed rafters replaces the former solid brown
    # roof block. The assembly remains simple but now reads like the mockup.
    for side, x, angle in (
        ("left", -roof_half_span / 2, -roof_angle),
        ("right", roof_half_span / 2, roof_angle),
    ):
        add_box(
            f"V2 Roof rebuild lining {side}",
            (x, house_center_y, roof_center_z - 0.10),
            (roof_slope_length, roof_depth, 0.10),
            oak,
            collection="V2 STRUCTURE",
            rotation=(0.0, angle, 0.0),
            bevel=0.012,
        )
        add_box(
            f"V2 Roof rebuild skin {side}",
            (x, house_center_y, roof_center_z + 0.01),
            (roof_slope_length + 0.10, roof_depth + 0.08, 0.12),
            charcoal,
            collection="V2 EXTERIOR",
            rotation=(0.0, angle, 0.0),
            bevel=0.014,
        )

    rafter_count = 12
    for index in range(rafter_count):
        y = (
            house_center_y
            - roof_depth / 2
            + 0.18
            + index * (roof_depth - 0.36) / (rafter_count - 1)
        )
        for side, x, angle in (
            ("left", -roof_half_span / 2, -roof_angle),
            ("right", roof_half_span / 2, roof_angle),
        ):
            add_box(
                f"V2 Roof rebuild rafter {side} {index + 1:02d}",
                (x, y, roof_center_z - 0.20),
                (roof_slope_length + 0.08, 0.105, 0.18),
                oak,
                collection="V2 STRUCTURE",
                rotation=(0.0, angle, 0.0),
                bevel=0.012,
            )

    # Long raised rows break the dark roof skin into a tile-like rhythm.
    for side_sign, side in ((-1.0, "left"), (1.0, "right")):
        for row in range(1, 10):
            x = side_sign * roof_half_span * row / 10
            z = DIMS.roof_ridge_z - roof_rise * abs(x) / roof_half_span + 0.12
            add_box(
                f"V2 Roof rebuild tile row {side} {row:02d}",
                (x, house_center_y, z),
                (0.040, roof_depth - 0.02, 0.035),
                charcoal,
                collection="V2 EXTERIOR",
                bevel=0.010,
            )

    add_box(
        "V2 Roof rebuild ridge cap",
        (0.0, house_center_y, DIMS.roof_ridge_z + 0.10),
        (0.22, roof_depth + 0.14, 0.18),
        charcoal,
        collection="V2 EXTERIOR",
        bevel=0.07,
    )
    for side_sign, side in ((-1.0, "left"), (1.0, "right")):
        add_box(
            f"V2 Roof rebuild gutter {side}",
            (side_sign * roof_half_span, house_center_y, DIMS.roof_eave_z - 0.02),
            (0.18, roof_depth + 0.16, 0.18),
            charcoal,
            collection="V2 EXTERIOR",
            bevel=0.07,
        )

    pv_x = 2.68
    pv_z = DIMS.roof_ridge_z - roof_rise * (pv_x / roof_half_span) + 0.38
    for index, y in enumerate((-1.45, 0.08, 1.61)):
        add_box(
            f"V2 PV module {index + 1}",
            (pv_x, house_center_y + y, pv_z),
            (2.62, 1.34, 0.15),
            charcoal,
            collection="V2 TECHNICAL",
            rotation=(0.0, roof_angle, 0.0),
            bevel=0.035,
        )

    # A second timber screen continues the upper facade motif beside the
    # ground-floor right window, never across its opening.
    x_max = DIMS.width / 2 - 0.10
    for index, y in enumerate((2.82, 3.00, 3.18, 3.36, 3.54)):
        add_box(
            f"V2 Exterior right ground rear slat {index + 1}",
            (x_max + 0.13, y, 1.78),
            (0.10, 0.085, 2.62),
            oak,
            collection="V2 EXTERIOR",
            bevel=0.012,
        )

    # The reference is materially wider than the initial generic house. A
    # single non-destructive visual-match root keeps every opening, item and
    # technical axis aligned while correcting that global silhouette.
    root = bpy.data.objects.new("V2 Rebuild width match", None)
    bpy.data.collections["V2 ANIMATION"].objects.link(root)
    target_collections = (
        "V2 STRUCTURE",
        "V2 EXTERIOR",
        "V2 FACADE",
        "V2 INTERIOR",
        "V2 FURNITURE",
        "V2 TECHNICAL",
        "V2 PLAN",
    )
    for collection_name in target_collections:
        for obj in list(bpy.data.collections[collection_name].objects):
            if obj is not root and obj.parent is None:
                obj.parent = root
    root.scale = (1.16, 1.0, 1.0)


def build_rebuild_match_anchors(materials: dict[str, bpy.types.Material]) -> None:
    """Recompose the stair, bathroom and technical anchors from mockup V2."""
    plaster = materials["plaster"]
    tile = materials["tile"]
    oak = materials["oak"]
    charcoal = materials["charcoal"]
    glass = materials["glass"]
    porcelain = materials["porcelain"]
    service_red = materials["service_red"]

    # The reference has no foreground tub or gallery sofa. Removing both opens
    # the upper cutaway and restores the bathroom/gallery hierarchy.
    remove_objects_with_prefix(
        "V2 Upper bathroom tub",
        "V2 Upper gallery bench",
        "V2 Upper gallery cushion",
        "V2 Upper bathroom shower glass",
    )

    # A full-height tiled back plane makes the bathroom read as a room rather
    # than as loose sanitary objects floating in the upper storey.
    add_box(
        "V2 Rebuild bathroom tiled back wall",
        (1.93, 2.85, 4.86),
        (2.24, 0.11, 2.48),
        tile,
        collection="V2 INTERIOR",
        bevel=0.018,
    )
    for joint in (-0.72, -0.24, 0.24, 0.72):
        add_box(
            f"V2 Rebuild bathroom tile joint {joint:+.2f}",
            (1.93 + joint, 2.785, 4.86),
            (0.018, 0.016, 2.36),
            plaster,
            collection="V2 INTERIOR",
            bevel=0.002,
        )

    # Reposition the existing fixtures into the three-part composition from
    # the mockup: vanity left/rear, shower centre, WC right/front.
    fixture_locations = {
        "V2 Upper bathroom vanity": (1.40, 2.60, 4.08),
        "V2 Upper bathroom basin": (1.40, 2.46, 4.57),
        "V2 Upper bathroom mirror": (1.40, 2.76, 5.18),
        "V2 Upper bathroom shower tray": (1.55, 2.08, 3.61),
        "V2 Upper bathroom toilet bowl": (2.48, 1.18, 3.83),
        "V2 Upper bathroom toilet cistern": (2.48, 1.48, 4.12),
    }
    for name, location in fixture_locations.items():
        obj = bpy.data.objects.get(name)
        if obj is not None:
            obj.location = location

    for x in (1.04, 2.06):
        add_box(
            f"V2 Rebuild shower frame {x:.2f}",
            (x, 1.54, 4.58),
            (0.045, 0.055, 1.92),
            charcoal,
            collection="V2 FURNITURE",
            bevel=0.008,
        )
    add_box(
        "V2 Rebuild shower top rail",
        (1.55, 1.54, 5.54),
        (1.06, 0.055, 0.045),
        charcoal,
        collection="V2 FURNITURE",
        bevel=0.008,
    )

    # A white service spine gives the distribution cabinet the same dominant,
    # recessed wall position as the mockup.
    add_box(
        "V2 Rebuild distribution spine",
        (DIMS.service_x, 1.14, 1.80),
        (1.28, 0.16, 2.92),
        plaster,
        collection="V2 INTERIOR",
        bevel=0.018,
    )
    for name in (
        "V2 Ground distribution cabinet back",
        "V2 Ground distribution cabinet interior",
        "V2 Ground distribution open door",
    ):
        obj = bpy.data.objects.get(name)
        if obj is not None:
            obj.location.y -= 0.12
    for obj in bpy.data.objects:
        if obj.name.startswith("V2 Ground distribution breaker"):
            obj.location.y -= 0.12

    # Visible red conduit is introduced now because it is one of the defining
    # graphic anchors of mockup V2, not a dispensable late-stage detail.
    conduit_x = 3.40
    conduit_wall_y = -2.70
    conduit_segments = (
        (
            (conduit_x, DIMS.server_center_y - 0.05, DIMS.server_floor_z + 0.28),
            (conduit_x, DIMS.server_center_y - 0.05, 0.02),
        ),
        (
            (conduit_x, DIMS.server_center_y - 0.05, 0.02),
            (conduit_x, conduit_wall_y, 0.02),
        ),
        (
            (conduit_x, conduit_wall_y, 0.02),
            (conduit_x, conduit_wall_y, 6.28),
        ),
        (
            (conduit_x, conduit_wall_y, 6.28),
            (2.68, -2.48, 7.95),
        ),
    )
    for index, (start, end) in enumerate(conduit_segments):
        add_beam_between(
            f"V2 Rebuild red conduit {index + 1}",
            start,
            end,
            thickness=0.028,
            material=service_red,
            collection="V2 TECHNICAL",
        )
    add_box(
        "V2 Rebuild bathroom controller",
        (2.58, 2.72, 5.02),
        (0.38, 0.10, 0.60),
        porcelain,
        collection="V2 TECHNICAL",
        bevel=0.055,
    )

    # Dark frames make the three PV modules legible as panels, not rails.
    roof_half_span = DIMS.width / 2 + DIMS.roof_overhang_x
    roof_rise = DIMS.roof_ridge_z - DIMS.roof_eave_z
    roof_angle = math.atan2(roof_rise, roof_half_span)
    pv_x = 2.68
    pv_z = DIMS.roof_ridge_z - roof_rise * (pv_x / roof_half_span) + 0.43
    house_center_y = (DIMS.ground_front_y + DIMS.ground_rear_y) / 2
    for index, y_offset in enumerate((-1.45, 0.08, 1.61)):
        for edge in (-0.69, 0.69):
            add_box(
                f"V2 PV module {index + 1} frame {edge:+.2f}",
                (pv_x, house_center_y + y_offset + edge, pv_z),
                (2.68, 0.035, 0.045),
                charcoal,
                collection="V2 TECHNICAL",
                rotation=(0.0, roof_angle, 0.0),
                bevel=0.008,
            )

    # New R3 objects inherit the same non-destructive width correction.
    root = bpy.data.objects.get("V2 Rebuild width match")
    if root is not None:
        for collection_name in (
            "V2 STRUCTURE",
            "V2 EXTERIOR",
            "V2 FACADE",
            "V2 INTERIOR",
            "V2 FURNITURE",
            "V2 TECHNICAL",
            "V2 PLAN",
        ):
            for obj in list(bpy.data.collections[collection_name].objects):
                if obj is not root and obj.parent is None:
                    obj.parent = root


def build_rebuild_match_furniture(materials: dict[str, bpy.types.Material]) -> None:
    """Strengthen the room silhouettes that define mockup V2 at hero scale."""
    oak = materials["oak"]
    floor_oak = materials["floor_oak"]
    upholstery = materials["upholstery"]
    charcoal = materials["charcoal"]
    porcelain = materials["porcelain"]
    plant = materials["plant"]
    plaster = materials["plaster"]
    service_red = materials["service_red"]

    # The first furniture pass was dimensionally plausible but visually too
    # small. Rebuild the living group as a compact, readable mockup silhouette.
    remove_objects_with_prefix("V2 Ground living")
    add_box(
        "V2 R4 living sofa plinth",
        (-3.42, 2.30, 0.48),
        (2.50, 0.94, 0.32),
        upholstery,
        collection="V2 FURNITURE",
        bevel=0.10,
    )
    for index, x in enumerate((-3.98, -2.86)):
        add_box(
            f"V2 R4 living sofa seat {index + 1}",
            (x, 2.18, 0.72),
            (1.04, 0.70, 0.20),
            porcelain,
            collection="V2 FURNITURE",
            bevel=0.095,
        )
        add_box(
            f"V2 R4 living sofa back cushion {index + 1}",
            (x, 2.56, 1.10),
            (1.00, 0.20, 0.62),
            upholstery,
            collection="V2 FURNITURE",
            bevel=0.10,
        )
    add_box(
        "V2 R4 living sofa back",
        (-3.42, 2.70, 1.02),
        (2.48, 0.18, 0.92),
        upholstery,
        collection="V2 FURNITURE",
        bevel=0.08,
    )
    for side, x in (("left", -4.62), ("right", -2.22)):
        add_box(
            f"V2 R4 living sofa arm {side}",
            (x, 2.28, 0.79),
            (0.18, 0.88, 0.66),
            upholstery,
            collection="V2 FURNITURE",
            bevel=0.07,
        )

    add_box(
        "V2 R4 living TV console",
        (-1.56, 3.26, 0.65),
        (1.20, 0.42, 0.58),
        oak,
        collection="V2 FURNITURE",
        bevel=0.035,
    )
    add_box(
        "V2 R4 living TV screen",
        (-1.56, 3.48, 1.44),
        (1.20, 0.07, 0.76),
        charcoal,
        collection="V2 FURNITURE",
        bevel=0.035,
    )
    add_box(
        "V2 R4 living chair seat",
        (-1.78, -0.18, 0.62),
        (0.84, 0.82, 0.38),
        upholstery,
        collection="V2 FURNITURE",
        rotation=(0.0, 0.0, math.radians(-16.0)),
        bevel=0.10,
    )
    add_box(
        "V2 R4 living chair back",
        (-1.68, 0.15, 1.03),
        (0.80, 0.18, 0.82),
        upholstery,
        collection="V2 FURNITURE",
        rotation=(0.0, 0.0, math.radians(-16.0)),
        bevel=0.08,
    )
    add_box(
        "V2 R4 living coffee table top",
        (-3.06, 0.55, 0.64),
        (1.45, 0.75, 0.10),
        oak,
        collection="V2 FURNITURE",
        bevel=0.035,
    )
    for x in (-3.63, -2.49):
        for y in (0.28, 0.82):
            add_box(
                f"V2 R4 living coffee leg {x:+.2f} {y:+.2f}",
                (x, y, 0.43),
                (0.055, 0.055, 0.39),
                charcoal,
                collection="V2 FURNITURE",
                bevel=0.008,
            )
    add_cylinder(
        "V2 R4 living plant pot",
        (-4.25, 0.95, 0.55),
        radius=0.22,
        depth=0.48,
        material=oak,
        collection="V2 FURNITURE",
    )
    for index, (x, y, z, radius) in enumerate(
        (
            (-4.25, 0.95, 0.98, 0.25),
            (-4.38, 0.94, 1.19, 0.20),
            (-4.13, 0.96, 1.31, 0.18),
        )
    ):
        add_cylinder(
            f"V2 R4 living plant crown {index + 1}",
            (x, y, z),
            radius=radius,
            depth=0.12,
            material=plant,
            collection="V2 FURNITURE",
            vertices=18,
        )

    # A full cabinet elevation and pendants give the right-hand ground room
    # the same warm kitchen/dining weight as the reference.
    remove_objects_with_prefix("V2 Ground kitchen")
    add_box(
        "V2 R4 kitchen lower cabinets",
        (3.18, 3.32, 0.73),
        (2.18, 0.58, 0.84),
        oak,
        collection="V2 FURNITURE",
        bevel=0.035,
    )
    add_box(
        "V2 R4 kitchen worktop",
        (3.18, 3.29, 1.18),
        (2.28, 0.66, 0.09),
        charcoal,
        collection="V2 FURNITURE",
        bevel=0.025,
    )
    add_box(
        "V2 R4 kitchen wall cabinets",
        (3.05, 3.47, 2.27),
        (1.70, 0.38, 0.78),
        oak,
        collection="V2 FURNITURE",
        bevel=0.028,
    )
    for x in (2.49, 3.05, 3.61):
        add_box(
            f"V2 R4 kitchen cabinet joint {x:.2f}",
            (x, 3.268, 2.27),
            (0.018, 0.016, 0.68),
            charcoal,
            collection="V2 FURNITURE",
            bevel=0.003,
        )
    add_box(
        "V2 R4 kitchen tall cabinet",
        (4.15, 2.64, 1.47),
        (0.66, 0.72, 2.30),
        oak,
        collection="V2 FURNITURE",
        bevel=0.035,
    )
    add_box(
        "V2 R4 kitchen oven",
        (4.15, 2.265, 1.46),
        (0.48, 0.06, 0.62),
        charcoal,
        collection="V2 FURNITURE",
        bevel=0.018,
    )
    add_box(
        "V2 R4 kitchen sink",
        (3.10, 2.94, 1.245),
        (0.62, 0.30, 0.06),
        porcelain,
        collection="V2 FURNITURE",
        bevel=0.045,
    )
    add_beam_between(
        "V2 R4 kitchen faucet rise",
        (3.10, 3.03, 1.27),
        (3.10, 3.03, 1.63),
        thickness=0.035,
        material=charcoal,
        collection="V2 FURNITURE",
    )
    add_beam_between(
        "V2 R4 kitchen faucet neck",
        (3.10, 3.03, 1.63),
        (3.10, 2.84, 1.63),
        thickness=0.035,
        material=charcoal,
        collection="V2 FURNITURE",
    )
    for index, x in enumerate((2.30, 2.92, 3.54)):
        add_beam_between(
            f"V2 R4 dining pendant cord {index + 1}",
            (x, -0.74, 2.98),
            (x, -0.74, 2.20),
            thickness=0.018,
            material=charcoal,
            collection="V2 LIGHTING",
        )
        add_cylinder(
            f"V2 R4 dining pendant shade {index + 1}",
            (x, -0.74, 2.11),
            radius=0.14,
            depth=0.22,
            material=charcoal,
            collection="V2 LIGHTING",
            vertices=24,
        )

    # Bedroom textiles and lamps prevent the upper-left room from reading as
    # a bare blockout without introducing late-stage decoration.
    add_box(
        "V2 R4 bedroom duvet",
        (-3.05, 1.17, 4.08),
        (1.70, 1.22, 0.12),
        plaster,
        collection="V2 FURNITURE",
        bevel=0.08,
    )
    for index, x in enumerate((-4.28, -1.82)):
        add_beam_between(
            f"V2 R4 bedroom lamp stem {index + 1}",
            (x, 2.02, 4.15),
            (x, 2.02, 4.50),
            thickness=0.025,
            material=charcoal,
            collection="V2 LIGHTING",
        )
        add_cylinder(
            f"V2 R4 bedroom lamp shade {index + 1}",
            (x, 2.02, 4.56),
            radius=0.13,
            depth=0.17,
            material=porcelain,
            collection="V2 LIGHTING",
            vertices=24,
        )

    # Give the bath recognizable fixtures instead of another coloured bay.
    for x in (1.56, 2.10):
        add_box(
            f"V2 R4 bathroom vanity joint {x:.2f}",
            (x, 3.025, 4.08),
            (0.018, 0.018, 0.76),
            charcoal,
            collection="V2 FURNITURE",
            bevel=0.003,
        )
    add_beam_between(
        "V2 R4 shower riser",
        (2.02, 2.65, 4.28),
        (2.02, 2.65, 5.35),
        thickness=0.028,
        material=charcoal,
        collection="V2 FURNITURE",
    )
    add_beam_between(
        "V2 R4 shower arm",
        (2.02, 2.65, 5.35),
        (2.02, 2.42, 5.35),
        thickness=0.028,
        material=charcoal,
        collection="V2 FURNITURE",
    )
    add_cylinder(
        "V2 R4 shower control",
        (2.02, 2.61, 4.66),
        radius=0.075,
        depth=0.05,
        material=charcoal,
        collection="V2 FURNITURE",
        vertices=24,
    )

    # The open black door hid the kitchen and made the service cabinet look
    # like a solid divider. The reference keeps the equipment face exposed.
    remove_objects_with_prefix("V2 Ground distribution open door")
    for index, x in enumerate((DIMS.service_x - 0.35, DIMS.service_x + 0.35)):
        add_box(
            f"V2 R4 distribution controller {index + 1}",
            (x, 0.73, 2.64),
            (0.44, 0.13, 0.38),
            porcelain,
            collection="V2 TECHNICAL",
            bevel=0.065,
        )
    add_beam_between(
        "V2 R4 distribution top conduit",
        (DIMS.service_x, -2.70, 2.89),
        (3.40, -2.70, 2.89),
        thickness=0.028,
        material=service_red,
        collection="V2 TECHNICAL",
    )
    add_beam_between(
        "V2 R4 upper ceiling conduit",
        (0.46, -2.70, 6.21),
        (3.40, -2.70, 6.21),
        thickness=0.028,
        material=service_red,
        collection="V2 TECHNICAL",
    )

    # A dark cap restores the strong three-panel PV read under studio light.
    roof_half_span = DIMS.width / 2 + DIMS.roof_overhang_x
    roof_rise = DIMS.roof_ridge_z - DIMS.roof_eave_z
    roof_angle = math.atan2(roof_rise, roof_half_span)
    pv_x = 2.68
    pv_z = DIMS.roof_ridge_z - roof_rise * (pv_x / roof_half_span) + 0.49
    house_center_y = (DIMS.ground_front_y + DIMS.ground_rear_y) / 2
    for index, y_offset in enumerate((-1.45, 0.08, 1.61)):
        add_box(
            f"V2 R4 PV dark face {index + 1}",
            (pv_x, house_center_y + y_offset, pv_z),
            (2.50, 1.22, 0.045),
            charcoal,
            collection="V2 TECHNICAL",
            rotation=(0.0, roof_angle, 0.0),
            bevel=0.025,
        )

    root = bpy.data.objects.get("V2 Rebuild width match")
    if root is not None:
        for collection_name in (
            "V2 FURNITURE",
            "V2 TECHNICAL",
            "V2 LIGHTING",
        ):
            for obj in list(bpy.data.collections[collection_name].objects):
                if obj is not root and obj.parent is None:
                    obj.parent = root


def build_rebuild_match_presentation(materials: dict[str, bpy.types.Material]) -> None:
    """Add the front-facing architectural cues visible in the V2 hero mockup."""
    oak = materials["oak"]
    charcoal = materials["charcoal"]
    plaster = materials["plaster"]
    porcelain = materials["porcelain"]
    service_red = materials["service_red"]
    pv_blue = materials["pv_blue"]
    tile = materials["tile"]

    def add_rear_door(name: str, x: float, bottom: float, width: float = 0.82) -> None:
        height = 2.08
        y = DIMS.ground_rear_y - 0.19
        add_box(
            f"{name} leaf",
            (x, y, bottom + height / 2),
            (width, 0.08, height),
            oak,
            collection="V2 INTERIOR",
            bevel=0.025,
        )
        for suffix, frame_x in (
            ("left", x - width / 2 - 0.045),
            ("right", x + width / 2 + 0.045),
        ):
            add_box(
                f"{name} frame {suffix}",
                (frame_x, y - 0.01, bottom + height / 2),
                (0.07, 0.11, height + 0.14),
                plaster,
                collection="V2 INTERIOR",
                bevel=0.008,
            )
        add_box(
            f"{name} frame top",
            (x, y - 0.01, bottom + height + 0.04),
            (width + 0.16, 0.11, 0.07),
            plaster,
            collection="V2 INTERIOR",
            bevel=0.008,
        )
        add_cylinder(
            f"{name} handle",
            (x + width * 0.31, y - 0.07, bottom + 1.03),
            radius=0.035,
            depth=0.06,
            material=charcoal,
            collection="V2 INTERIOR",
            vertices=18,
        )

    # These rear-facing leaves are the doors seen in the axonometric reference;
    # the side-wall leaves remain valid for the floor plan but read edge-on.
    add_rear_door("V2 R5 rear ground hall door", -0.62, DIMS.ground_finish_z)
    add_rear_door("V2 R5 rear upper hall door", -0.62, DIMS.upper_finish_z)
    add_rear_door("V2 R5 rear upper gallery door", 3.55, DIMS.upper_finish_z, 0.70)

    # Minimal framed art adds the same wall-scale cues as the mockup without
    # pretending that decoration is part of the technical model.
    for name, x, z, width, height in (
        ("living", -3.55, 1.83, 0.62, 0.78),
        ("bedroom", -3.55, 5.14, 0.62, 0.78),
    ):
        add_box(
            f"V2 R5 {name} picture",
            (x, DIMS.ground_rear_y - 0.235, z),
            (width, 0.035, height),
            porcelain,
            collection="V2 FURNITURE",
            bevel=0.012,
        )
        for suffix, frame_x in (("left", x - width / 2), ("right", x + width / 2)):
            add_box(
                f"V2 R5 {name} picture frame {suffix}",
                (frame_x, DIMS.ground_rear_y - 0.26, z),
                (0.035, 0.05, height + 0.04),
                oak,
                collection="V2 FURNITURE",
                bevel=0.004,
            )
        for suffix, frame_z in (("bottom", z - height / 2), ("top", z + height / 2)):
            add_box(
                f"V2 R5 {name} picture frame {suffix}",
                (x, DIMS.ground_rear_y - 0.26, frame_z),
                (width + 0.04, 0.05, 0.035),
                oak,
                collection="V2 FURNITURE",
                bevel=0.004,
            )

    # The grey bath wall needs a finer tile rhythm and a framed mirror to read
    # independently from the dark shower outline.
    for index, z in enumerate((4.02, 4.45, 4.88, 5.31, 5.74)):
        add_box(
            f"V2 R5 bathroom horizontal joint {index + 1}",
            (1.93, 2.782, z),
            (2.14, 0.016, 0.018),
            plaster,
            collection="V2 INTERIOR",
            bevel=0.002,
        )
    for suffix, x in (("left", 0.92), ("right", 1.88)):
        add_box(
            f"V2 R5 bathroom mirror frame {suffix}",
            (x, 2.705, 5.18),
            (0.035, 0.04, 0.98),
            charcoal,
            collection="V2 FURNITURE",
            bevel=0.005,
        )
    for suffix, z in (("bottom", 4.69), ("top", 5.67)):
        add_box(
            f"V2 R5 bathroom mirror frame {suffix}",
            (1.40, 2.705, z),
            (0.99, 0.04, 0.035),
            charcoal,
            collection="V2 FURNITURE",
            bevel=0.005,
        )

    add_box(
        "V2 R7 bathroom tiled side return",
        (3.03, 2.48, 4.86),
        (0.11, 0.74, 2.48),
        tile,
        collection="V2 INTERIOR",
        bevel=0.018,
    )

    # A compact front shower outline sits beside the vanity and leaves the WC
    # visible; this is the same three-part bath composition as the reference.
    remove_objects_with_prefix(
        "V2 Rebuild shower frame",
        "V2 Rebuild shower top rail",
    )
    shower_front_y = 2.16
    for index, x in enumerate((1.78, 2.72)):
        add_box(
            f"V2 R5 shower front upright {index + 1}",
            (x, shower_front_y, 4.64),
            (0.040, 0.050, 1.92),
            charcoal,
            collection="V2 FURNITURE",
            bevel=0.006,
        )
    add_box(
        "V2 R5 shower front top",
        (2.25, shower_front_y, 5.60),
        (0.98, 0.050, 0.040),
        charcoal,
        collection="V2 FURNITURE",
        bevel=0.006,
    )
    add_box(
        "V2 R5 shower front base",
        (2.25, shower_front_y, 3.68),
        (0.98, 0.050, 0.040),
        charcoal,
        collection="V2 FURNITURE",
        bevel=0.006,
    )

    # Trace the front of the distribution field as in the mockup. This makes
    # the electrical story legible before late-stage cable detailing.
    cabinet_x = DIMS.service_x
    cabinet_y = 0.64
    cable_segments = (
        ((cabinet_x - 0.55, cabinet_y, 2.86), (cabinet_x + 0.55, cabinet_y, 2.86)),
        ((cabinet_x + 0.55, cabinet_y, 2.86), (cabinet_x + 0.55, cabinet_y, 0.38)),
        ((cabinet_x + 0.55, cabinet_y, 0.38), (cabinet_x - 0.55, cabinet_y, 0.38)),
        ((cabinet_x - 0.55, cabinet_y, 0.38), (cabinet_x - 0.55, cabinet_y, 1.05)),
    )
    for index, (start, end) in enumerate(cable_segments):
        add_beam_between(
            f"V2 R5 distribution red outline {index + 1}",
            start,
            end,
            thickness=0.026,
            material=service_red,
            collection="V2 TECHNICAL",
        )

    server_outline = (
        ((DIMS.service_x + 1.05, -4.24, -1.58), (DIMS.service_x + 1.05, -4.24, -0.16)),
        ((DIMS.service_x + 1.05, -4.24, -1.58), (DIMS.service_x + 0.15, -4.24, -1.58)),
    )
    for index, (start, end) in enumerate(server_outline):
        add_beam_between(
            f"V2 R5 server red outline {index + 1}",
            start,
            end,
            thickness=0.026,
            material=service_red,
            collection="V2 TECHNICAL",
        )

    # Larger modules compensate for the strong depth foreshortening of the
    # selected camera while retaining the three-panel composition.
    remove_objects_with_prefix("V2 R4 PV dark face")
    roof_half_span = DIMS.width / 2 + DIMS.roof_overhang_x
    roof_rise = DIMS.roof_ridge_z - DIMS.roof_eave_z
    roof_angle = math.atan2(roof_rise, roof_half_span)
    pv_x = 2.60
    pv_z = DIMS.roof_ridge_z - roof_rise * (pv_x / roof_half_span) + 0.42
    house_center_y = (DIMS.ground_front_y + DIMS.ground_rear_y) / 2
    for index, y_offset in enumerate((-1.72, 0.08, 1.88)):
        add_box(
            f"V2 R5 PV face {index + 1}",
            (pv_x, house_center_y + y_offset, pv_z),
            (2.62, 1.66, 0.075),
            pv_blue,
            collection="V2 TECHNICAL",
            rotation=(0.0, roof_angle, 0.0),
            bevel=0.035,
        )

    # Soft room-specific fill brings back the localized illumination visible
    # in the mockup without starting the final lighting phase.
    for name, location, target, energy, size in (
        ("living", (-3.0, -0.4, 2.75), (-3.0, 1.4, 0.75), 85.0, 3.0),
        ("kitchen", (3.0, -0.2, 2.72), (3.1, 2.0, 0.95), 72.0, 2.6),
        ("bedroom", (-3.0, -0.2, 5.95), (-3.0, 1.4, 4.05), 72.0, 2.8),
        ("bathroom", (1.8, -0.1, 5.95), (1.8, 2.1, 4.45), 68.0, 2.4),
    ):
        add_area_light(
            f"V2 R5 {name} fill",
            location,
            target,
            energy=energy,
            size=size,
            color=(1.0, 0.88, 0.72),
        )

    # Clear the two most important front-view sightlines after all furniture
    # has been assembled.
    console = bpy.data.objects.get("V2 R4 living TV console")
    if console is not None:
        console.location = (-1.00, 1.42, 0.65)
        console.dimensions = (0.34, 1.52, 0.58)
    tv = bpy.data.objects.get("V2 R4 living TV screen")
    if tv is not None:
        tv.location = (-1.00, 1.42, 1.50)
        tv.dimensions = (0.07, 1.32, 0.80)
    dining_prefixes = ("V2 Ground dining", "V2 R4 dining pendant")
    for obj in bpy.data.objects:
        if obj.name.startswith(dining_prefixes):
            obj.location.x += 0.48

    root = bpy.data.objects.get("V2 Rebuild width match")
    if root is not None:
        for collection_name in (
            "V2 INTERIOR",
            "V2 FURNITURE",
            "V2 TECHNICAL",
        ):
            for obj in list(bpy.data.collections[collection_name].objects):
                if obj is not root and obj.parent is None:
                    obj.parent = root


def build_rebuild_match_layout(materials: dict[str, bpy.types.Material]) -> None:
    """Rebuild real partitions and furniture orientation from the V2 plans."""
    plaster = materials["plaster"]
    oak = materials["oak"]
    upholstery = materials["upholstery"]
    porcelain = materials["porcelain"]
    charcoal = materials["charcoal"]
    plant = materials["plant"]

    ground_floor = DIMS.ground_finish_z
    ground_ceiling = DIMS.upper_finish_z - 0.19
    upper_floor = DIMS.upper_finish_z
    upper_ceiling = DIMS.upper_ceiling_z - 0.14
    partition_front_y = DIMS.ground_front_y + 0.42
    partition_rear_y = DIMS.ground_rear_y - 0.18

    # The previous partitions began around the room centre. In both plan and
    # cutaway they therefore read as isolated rear fins instead of real room
    # boundaries. Rebuild every main axis from the section edge to the rear.
    remove_objects_with_prefix(
        "V2 Ground partition",
        "V2 Upper partition",
        "V2 Ground living door",
        "V2 Ground dining door",
        "V2 Upper bedroom door",
        "V2 Upper bathroom door",
        "V2 Upper gallery door",
        "V2 R5 rear ground hall door",
        "V2 R5 rear upper hall door",
        "V2 R5 rear upper gallery door",
    )
    for name, x in (("living hall", -1.15), ("hall dining", 1.02)):
        add_wall_y_with_openings(
            f"V2 R8 Ground partition {name}",
            x=x,
            y_min=partition_front_y,
            y_max=partition_rear_y,
            z_floor=ground_floor,
            z_ceiling=ground_ceiling,
            openings=((2.55, 0.94, ground_floor, 2.18),),
            material=plaster,
            collection="V2 INTERIOR",
            thickness=0.20,
        )
        add_box(
            f"V2 R8 Ground cut post {name}",
            (x, partition_front_y + 0.10, (ground_floor + ground_ceiling) / 2),
            (0.20, 0.20, ground_ceiling - ground_floor),
            plaster,
            collection="V2 INTERIOR",
            bevel=0.012,
        )
    for name, x in (
        ("bedroom hall", -1.15),
        ("hall gallery", 0.76),
        ("gallery bathroom", 2.45),
    ):
        add_wall_y_with_openings(
            f"V2 R8 Upper partition {name}",
            x=x,
            y_min=partition_front_y,
            y_max=partition_rear_y,
            z_floor=upper_floor,
            z_ceiling=upper_ceiling,
            openings=((2.55, 0.92, upper_floor, 2.10),),
            material=plaster,
            collection="V2 INTERIOR",
            thickness=0.20,
        )
        add_box(
            f"V2 R8 Upper cut post {name}",
            (x, partition_front_y + 0.10, (upper_floor + upper_ceiling) / 2),
            (0.20, 0.20, upper_ceiling - upper_floor),
            plaster,
            collection="V2 INTERIOR",
            bevel=0.012,
        )
    for name, x, bottom, width, height in (
        ("V2 R8 Ground living door", -1.15, ground_floor, 0.94, 2.18),
        ("V2 R8 Ground dining door", 1.02, ground_floor, 0.94, 2.18),
        ("V2 R8 Upper bedroom door", -1.15, upper_floor, 0.92, 2.10),
        ("V2 R8 Upper gallery door", 0.76, upper_floor, 0.92, 2.10),
        ("V2 R8 Upper bathroom door", 2.45, upper_floor, 0.92, 2.10),
    ):
        add_door_y(
            name,
            x=x,
            center_y=2.55,
            bottom=bottom,
            width=width,
            height=height,
            material=oak,
            frame=charcoal,
            collection="V2 INTERIOR",
        )

    # Ground-floor living follows the authoritative plan: sofa on the left
    # wall, table beside it, loose chair toward the open front and TV on the
    # partition. This also clears the entrance route beside the stair.
    remove_objects_with_prefix("V2 R4 living")
    add_box(
        "V2 R8 living sofa plinth",
        (-4.12, 1.55, 0.49),
        (0.92, 2.42, 0.32),
        upholstery,
        collection="V2 FURNITURE",
        bevel=0.10,
    )
    add_box(
        "V2 R8 living sofa back",
        (-4.50, 1.55, 1.02),
        (0.18, 2.42, 0.92),
        upholstery,
        collection="V2 FURNITURE",
        bevel=0.08,
    )
    for index, y in enumerate((1.00, 2.10)):
        add_box(
            f"V2 R8 living sofa seat {index + 1}",
            (-4.00, y, 0.72),
            (0.70, 1.02, 0.20),
            porcelain,
            collection="V2 FURNITURE",
            bevel=0.09,
        )
        add_box(
            f"V2 R8 living sofa cushion {index + 1}",
            (-4.35, y, 1.10),
            (0.20, 0.98, 0.62),
            upholstery,
            collection="V2 FURNITURE",
            bevel=0.09,
        )
    for suffix, y in (("front", 0.39), ("rear", 2.71)):
        add_box(
            f"V2 R8 living sofa arm {suffix}",
            (-4.10, y, 0.79),
            (0.88, 0.18, 0.66),
            upholstery,
            collection="V2 FURNITURE",
            bevel=0.07,
        )
    add_box(
        "V2 R8 living coffee table",
        (-3.12, 1.47, 0.64),
        (1.12, 0.74, 0.10),
        oak,
        collection="V2 FURNITURE",
        bevel=0.035,
    )
    for x in (-3.53, -2.71):
        for y in (1.22, 1.72):
            add_box(
                f"V2 R8 living coffee leg {x:+.2f} {y:+.2f}",
                (x, y, 0.43),
                (0.05, 0.05, 0.38),
                charcoal,
                collection="V2 FURNITURE",
                bevel=0.006,
            )
    add_box(
        "V2 R8 living chair seat",
        (-3.28, -1.25, 0.62),
        (0.82, 0.82, 0.38),
        upholstery,
        collection="V2 FURNITURE",
        rotation=(0.0, 0.0, math.radians(24.0)),
        bevel=0.10,
    )
    add_box(
        "V2 R8 living chair back",
        (-3.43, -0.95, 1.03),
        (0.78, 0.18, 0.82),
        upholstery,
        collection="V2 FURNITURE",
        rotation=(0.0, 0.0, math.radians(24.0)),
        bevel=0.08,
    )
    add_box(
        "V2 R8 living TV console",
        (-1.43, 1.40, 0.65),
        (0.34, 1.48, 0.58),
        oak,
        collection="V2 FURNITURE",
        bevel=0.035,
    )
    add_box(
        "V2 R8 living TV",
        (-1.29, 1.40, 1.50),
        (0.07, 1.30, 0.80),
        charcoal,
        collection="V2 FURNITURE",
        bevel=0.025,
    )
    add_cylinder(
        "V2 R8 living plant pot",
        (-4.22, 3.18, 0.55),
        radius=0.22,
        depth=0.48,
        material=oak,
        collection="V2 FURNITURE",
    )
    for index, (x, y, z, radius) in enumerate(
        (
            (-4.22, 3.18, 0.98, 0.24),
            (-4.34, 3.17, 1.19, 0.19),
            (-4.10, 3.19, 1.30, 0.18),
        )
    ):
        add_cylinder(
            f"V2 R8 living plant crown {index + 1}",
            (x, y, z),
            radius=radius,
            depth=0.12,
            material=plant,
            collection="V2 FURNITURE",
            vertices=18,
        )

    # Upper bedroom: headboard on the left exterior wall, bed extending
    # toward the hall. The old model was rotated ninety degrees from the plan.
    remove_objects_with_prefix(
        "V2 Upper bedroom bed",
        "V2 Upper bedroom mattress",
        "V2 Upper bedroom headboard",
        "V2 Upper bedroom pillow",
        "V2 Upper bedroom nightstand",
        "V2 R4 bedroom",
    )
    bed_center = (-3.38, -0.72)
    add_box(
        "V2 R8 bedroom bed frame",
        (bed_center[0], bed_center[1], 3.70),
        (2.22, 1.92, 0.28),
        oak,
        collection="V2 FURNITURE",
        bevel=0.055,
    )
    add_box(
        "V2 R8 bedroom mattress",
        (-3.33, bed_center[1], 3.91),
        (2.02, 1.82, 0.26),
        upholstery,
        collection="V2 FURNITURE",
        bevel=0.11,
    )
    add_box(
        "V2 R8 bedroom headboard",
        (-4.50, bed_center[1], 4.20),
        (0.16, 2.00, 1.18),
        oak,
        collection="V2 FURNITURE",
        bevel=0.045,
    )
    for index, y in enumerate((-1.18, -0.26)):
        add_box(
            f"V2 R8 bedroom pillow {index + 1}",
            (-3.96, y, 4.12),
            (0.45, 0.72, 0.16),
            porcelain,
            collection="V2 FURNITURE",
            bevel=0.09,
        )
    add_box(
        "V2 R8 bedroom duvet",
        (-3.06, bed_center[1], 4.08),
        (1.18, 1.70, 0.12),
        plaster,
        collection="V2 FURNITURE",
        bevel=0.08,
    )
    for index, y in enumerate((-1.98, 0.54)):
        add_box(
            f"V2 R8 bedroom nightstand {index + 1}",
            (-4.36, y, 3.84),
            (0.48, 0.48, 0.62),
            oak,
            collection="V2 FURNITURE",
            bevel=0.035,
        )
        add_beam_between(
            f"V2 R8 bedroom lamp stem {index + 1}",
            (-4.36, y, 4.15),
            (-4.36, y, 4.50),
            thickness=0.025,
            material=charcoal,
            collection="V2 LIGHTING",
        )
        add_cylinder(
            f"V2 R8 bedroom lamp shade {index + 1}",
            (-4.36, y, 4.56),
            radius=0.13,
            depth=0.17,
            material=porcelain,
            collection="V2 LIGHTING",
            vertices=24,
        )
    add_box(
        "V2 R8 bedroom wardrobe",
        (-1.55, 1.72, 4.64),
        (0.52, 1.62, 2.12),
        oak,
        collection="V2 FURNITURE",
        bevel=0.035,
    )
    add_box(
        "V2 R8 bedroom wardrobe joint",
        (-1.275, 1.72, 4.64),
        (0.018, 0.04, 1.96),
        charcoal,
        collection="V2 FURNITURE",
        bevel=0.003,
    )

    # Complete the bathroom sequence from rear to front. Its side partitions
    # are now real walls, and the former empty lower half receives the tub.
    for name, location in (
        ("V2 Upper bathroom toilet bowl", (2.48, 0.26, 3.83)),
        ("V2 Upper bathroom toilet cistern", (2.48, 0.56, 4.12)),
    ):
        obj = bpy.data.objects.get(name)
        if obj is not None:
            obj.location = location
    remove_objects_with_prefix("V2 R8 bathroom tub")
    add_box(
        "V2 R8 bathroom tub body",
        (1.96, -1.88, 3.84),
        (1.62, 0.80, 0.58),
        porcelain,
        collection="V2 FURNITURE",
        bevel=0.16,
    )
    add_box(
        "V2 R8 bathroom tub inset",
        (1.96, -1.88, 4.05),
        (1.22, 0.48, 0.12),
        charcoal,
        collection="V2 FURNITURE",
        bevel=0.12,
    )

    root = bpy.data.objects.get("V2 Rebuild width match")
    if root is not None:
        for collection_name in (
            "V2 INTERIOR",
            "V2 FURNITURE",
            "V2 LIGHTING",
        ):
            for obj in list(bpy.data.collections[collection_name].objects):
                if obj is not root and obj.parent is None:
                    obj.parent = root


def parent_unparented_to_rebuild_root(*collection_names: str) -> None:
    """Keep late-stage objects on the same approved width-correction root."""
    root = bpy.data.objects.get("V2 Rebuild width match")
    if root is None:
        return
    for collection_name in collection_names:
        collection = bpy.data.collections.get(collection_name)
        if collection is None:
            continue
        for obj in list(collection.objects):
            if obj is not root and obj.parent is None:
                obj.parent = root


def build_final_detailed_furniture() -> None:
    """Replace the old blockouts with the mockup-aligned furniture library."""
    module_dir = str(ROOT / "blender")
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
    import furniture_v2_detailed as furniture_detail

    detailed = furniture_detail.build_furniture()
    dining_prefixes = ("F2 dining", "F2 chair", "F2 pendant")
    for obj in detailed.objects:
        if obj.parent is None and obj.name.startswith(dining_prefixes):
            obj.location.x += 0.38
    blockout = bpy.data.collections.get("V2 FURNITURE")
    if blockout is not None:
        blockout.hide_render = True
        blockout.hide_viewport = True
    parent_unparented_to_rebuild_root(furniture_detail.COLLECTION_NAME)
    detailed["hubmann_final_furniture"] = True
    bpy.context.scene["hubmann_v2_furniture"] = "furniture-detail-v04"


def build_phase3a(materials: dict[str, bpy.types.Material]) -> None:
    """Finish the architectural material hierarchy and construction edges."""
    concrete = materials["concrete"]
    plaster = materials["plaster"]
    oak = materials["oak"]
    charcoal = materials["charcoal"]
    floor_oak = materials["floor_oak"]
    tile = materials["tile"]

    add_surface_bump(concrete, scale=4.2, detail=4.0, strength=0.22, distance=0.055)
    add_surface_bump(plaster, scale=34.0, detail=2.2, strength=0.11, distance=0.018)
    add_surface_bump(oak, scale=8.0, detail=3.0, strength=0.16, distance=0.025)
    add_surface_bump(floor_oak, scale=12.0, detail=2.0, strength=0.10, distance=0.018)

    trim_oak = create_material(
        "V2 Finished oak trim", (0.48, 0.29, 0.12, 1.0), roughness=0.56
    )
    joint = create_material(
        "V2 Architectural shadow joint", (0.055, 0.050, 0.044, 1.0), roughness=0.68
    )
    floor_joint = create_material(
        "V2 Oak floor joint", (0.31, 0.22, 0.14, 1.0), roughness=0.76
    )

    # The former presentation wall sat in front of the final vanity. Replace
    # it with one true rear wall so vanity, shower and WC share the same room.
    remove_objects_with_prefix(
        "V2 Rebuild bathroom tiled back wall",
        "V2 Rebuild bathroom tile joint",
        "V2 R5 bathroom horizontal joint",
        "V2 R5 bathroom mirror frame",
        "V2 R7 bathroom tiled side return",
    )
    add_box(
        "V2 P3A bathroom tiled rear wall",
        (3.58, DIMS.ground_rear_y - 0.24, 4.86),
        (2.02, 0.11, 2.48),
        tile,
        collection="V2 INTERIOR",
        bevel=0.018,
    )
    for index, x in enumerate((2.86, 3.22, 3.58, 3.94, 4.30), 1):
        add_box(
            f"V2 P3A bathroom rear vertical joint {index}",
            (x, DIMS.ground_rear_y - 0.302, 4.86),
            (0.012, 0.014, 2.36),
            plaster,
            collection="V2 INTERIOR",
            bevel=0.002,
        )
    for index, z in enumerate((4.10, 4.48, 4.86, 5.24, 5.62), 1):
        add_box(
            f"V2 P3A bathroom rear horizontal joint {index}",
            (3.58, DIMS.ground_rear_y - 0.302, z),
            (1.92, 0.014, 0.012),
            plaster,
            collection="V2 INTERIOR",
            bevel=0.002,
        )

    house_center_y = (DIMS.ground_front_y + DIMS.ground_rear_y) / 2
    roof_half_span = DIMS.width / 2 + DIMS.roof_overhang_x
    front_gable_y = DIMS.ground_front_y - DIMS.roof_overhang_y - 0.055
    rear_gable_y = DIMS.ground_rear_y + DIMS.roof_overhang_y + 0.055
    for end_name, y in (("front", front_gable_y), ("rear", rear_gable_y)):
        for side_name, eave_x in (("left", -roof_half_span), ("right", roof_half_span)):
            add_beam_between(
                f"V2 P3A {end_name} {side_name} bargeboard",
                (0.0, y, DIMS.roof_ridge_z + 0.02),
                (eave_x, y, DIMS.roof_eave_z + 0.02),
                thickness=0.105,
                material=trim_oak,
                collection="V2 EXTERIOR",
            )

    # Right facade sills sit below the real openings and therefore cannot
    # collide with glazing or the adjacent timber-screen layer.
    x_max = DIMS.width / 2 - 0.10
    for level, center_y, width, bottom in (
        ("ground", 1.90, 1.55, 0.88),
        ("upper", 1.95, 1.35, 4.08),
    ):
        add_box(
            f"V2 P3A right {level} window sill",
            (x_max + 0.035, center_y, bottom - 0.035),
            (0.30, width + 0.18, 0.075),
            concrete,
            collection="V2 EXTERIOR",
            bevel=0.012,
        )

    # Explicit cut returns make every room boundary readable in the hero view
    # without turning the cutaway back into a closed box.
    for level_name, floor, ceiling, axes in (
        (
            "ground",
            DIMS.ground_finish_z,
            DIMS.upper_finish_z - 0.19,
            (-1.15, 1.02),
        ),
        (
            "upper",
            DIMS.upper_finish_z,
            DIMS.upper_ceiling_z - 0.14,
            (-1.15, 0.76, 2.45),
        ),
    ):
        for index, x in enumerate(axes, 1):
            add_box(
                f"V2 P3A {level_name} partition cut return {index}",
                (x, DIMS.ground_front_y + 0.73, (floor + ceiling) / 2),
                (0.24, 0.78, ceiling - floor),
                plaster,
                collection="V2 INTERIOR",
                bevel=0.018,
            )
            add_box(
                f"V2 P3A {level_name} partition shadow edge {index}",
                (x + 0.126, DIMS.ground_front_y + 0.34, (floor + ceiling) / 2),
                (0.014, 0.035, ceiling - floor - 0.08),
                joint,
                collection="V2 INTERIOR",
                bevel=0.002,
            )

    # Floor-board rhythm, rear skirtings and slab joints provide scale at hero
    # distance while staying intentionally simpler than a photoreal interior.
    for level_name, floor in (
        ("ground", DIMS.ground_finish_z),
        ("upper", DIMS.upper_finish_z),
    ):
        for index in range(1, 16):
            x = -4.55 + index * 0.58
            if level_name == "upper" and -0.74 < x < 0.64:
                continue
            add_box(
                f"V2 P3A {level_name} floor joint {index:02d}",
                (x, house_center_y, floor + 0.016),
                (0.009, 6.88, 0.008),
                floor_joint,
                collection="V2 INTERIOR",
                bevel=0.002,
            )
        add_box(
            f"V2 P3A {level_name} rear skirting",
            (0.0, DIMS.ground_rear_y - 0.235, floor + 0.065),
            (9.05, 0.055, 0.13),
            trim_oak,
            collection="V2 INTERIOR",
            bevel=0.008,
        )

    for level_name, z in (
        ("ground", 0.11),
        ("upper", DIMS.upper_finish_z - 0.19),
        ("ceiling", DIMS.upper_ceiling_z - 0.13),
    ):
        for index, x in enumerate((-2.65, 0.0, 2.65), 1):
            add_box(
                f"V2 P3A {level_name} slab joint {index}",
                (x, DIMS.ground_front_y - 0.585, z),
                (0.025, 0.035, 0.24),
                joint,
                collection="V2 STRUCTURE",
                bevel=0.002,
            )

    add_beam_between(
        "V2 P3A right rain downpipe",
        (roof_half_span + 0.02, DIMS.ground_rear_y + 0.42, DIMS.roof_eave_z),
        (roof_half_span + 0.02, DIMS.ground_rear_y + 0.42, 0.44),
        thickness=0.075,
        material=charcoal,
        collection="V2 EXTERIOR",
    )

    create_camera(
        "V2 Camera Material Detail",
        (15.0, -8.0, 6.2),
        (4.50, 1.85, 3.55),
        lens=78.0,
    )
    parent_unparented_to_rebuild_root(
        "V2 STRUCTURE", "V2 EXTERIOR", "V2 INTERIOR"
    )
    bpy.context.scene["hubmann_v2_phase3a"] = "complete"


def build_phase3b(materials: dict[str, bpy.types.Material]) -> None:
    """Finish the electrical story, server room and readable house lighting."""
    plaster = materials["plaster"]
    concrete = materials["concrete"]
    charcoal = materials["charcoal"]
    porcelain = materials["porcelain"]
    service_red = materials["service_red"]
    tech_blue = materials["tech_blue"]

    service_red.node_tree.nodes["Principled BSDF"].inputs[
        "Emission Color"
    ].default_value = (1.0, 0.012, 0.006, 1.0)
    emission_strength = service_red.node_tree.nodes["Principled BSDF"].inputs.get(
        "Emission Strength"
    )
    if emission_strength is not None:
        emission_strength.default_value = 0.42

    warm_glow = create_emission_material(
        "V2 Warm interior glow", (1.0, 0.54, 0.20, 1.0), strength=5.0
    )
    led_blue = create_emission_material(
        "V2 Server status blue", (0.015, 0.42, 1.0, 1.0), strength=6.0
    )
    panel_grey = create_material(
        "V2 Distribution enclosure", (0.43, 0.45, 0.45, 1.0), roughness=0.58
    )

    remove_objects_with_prefix(
        "V2 Ground distribution",
        "V2 R4 distribution",
        "V2 R5 distribution",
        "V2 Rebuild distribution spine",
        "V2 Rebuild red conduit",
        "V2 R4 upper ceiling conduit",
        "V2 R5 server red outline",
        "V2 Server rack",
        "V2 Server UPS",
        "V2 Server cooling",
        "V2 Rebuild bathroom controller",
    )

    # Keep the distribution field on the stair-side service wall, as in the
    # reference, instead of floating behind the dining area.
    cabinet_x = 1.05
    cabinet_y = 0.72
    add_box(
        "V2 P3B distribution recess",
        (cabinet_x, cabinet_y + 0.10, 1.62),
        (1.34, 0.28, 2.66),
        plaster,
        collection="V2 INTERIOR",
        bevel=0.025,
    )
    add_box(
        "V2 P3B distribution enclosure",
        (cabinet_x, cabinet_y - 0.08, 1.62),
        (1.08, 0.18, 2.46),
        panel_grey,
        collection="V2 TECHNICAL",
        bevel=0.035,
    )
    add_box(
        "V2 P3B distribution dark interior",
        (cabinet_x, cabinet_y - 0.19, 1.62),
        (0.91, 0.075, 2.24),
        charcoal,
        collection="V2 TECHNICAL",
        bevel=0.018,
    )
    for row in range(5):
        z = 0.78 + row * 0.36
        add_box(
            f"V2 P3B DIN rail {row + 1}",
            (cabinet_x, cabinet_y - 0.245, z),
            (0.78, 0.035, 0.16),
            concrete,
            collection="V2 TECHNICAL",
            bevel=0.010,
        )
        for slot in range(6):
            x = cabinet_x - 0.32 + slot * 0.128
            add_box(
                f"V2 P3B breaker {row + 1}-{slot + 1}",
                (x, cabinet_y - 0.272, z),
                (0.092, 0.035, 0.105),
                porcelain,
                collection="V2 TECHNICAL",
                bevel=0.008,
            )
            add_box(
                f"V2 P3B breaker toggle {row + 1}-{slot + 1}",
                (x, cabinet_y - 0.295, z + 0.012),
                (0.036, 0.018, 0.038),
                service_red if slot in (0, 5) else charcoal,
                collection="V2 TECHNICAL",
                bevel=0.004,
            )
    for index, x in enumerate((cabinet_x - 0.31, cabinet_x + 0.31), 1):
        add_box(
            f"V2 P3B distribution gateway {index}",
            (x, cabinet_y - 0.26, 2.69),
            (0.45, 0.08, 0.36),
            porcelain,
            collection="V2 TECHNICAL",
            bevel=0.065,
        )
        add_box(
            f"V2 P3B distribution gateway light {index}",
            (x, cabinet_y - 0.307, 2.64),
            (0.055, 0.015, 0.025),
            led_blue,
            collection="V2 TECHNICAL",
            bevel=0.004,
        )
    add_box(
        "V2 P3B distribution open door",
        (cabinet_x + 0.78, cabinet_y - 0.05, 1.62),
        (0.055, 1.02, 2.44),
        panel_grey,
        collection="V2 TECHNICAL",
        rotation=(0.0, 0.0, math.radians(-18.0)),
        bevel=0.025,
    )

    rack_x = DIMS.service_x - 0.58
    rack_y = DIMS.server_center_y - 0.03
    add_box(
        "V2 P3B server rack shell",
        (rack_x, rack_y, -0.75),
        (0.90, 0.92, 1.62),
        charcoal,
        collection="V2 TECHNICAL",
        bevel=0.035,
    )
    add_box(
        "V2 P3B server rack face",
        (rack_x, rack_y - 0.475, -0.75),
        (0.76, 0.035, 1.48),
        panel_grey,
        collection="V2 TECHNICAL",
        bevel=0.015,
    )
    for row in range(8):
        z = -1.35 + row * 0.17
        add_box(
            f"V2 P3B server unit {row + 1}",
            (rack_x, rack_y - 0.50, z),
            (0.66, 0.025, 0.105),
            tech_blue if row in (1, 5) else charcoal,
            collection="V2 TECHNICAL",
            bevel=0.008,
        )
        for index in range(4):
            add_box(
                f"V2 P3B server LED {row + 1}-{index + 1}",
                (rack_x - 0.24 + index * 0.10, rack_y - 0.52, z),
                (0.028, 0.012, 0.028),
                led_blue,
                collection="V2 TECHNICAL",
                bevel=0.004,
            )
    add_box(
        "V2 P3B server UPS",
        (DIMS.service_x + 0.60, DIMS.server_center_y - 0.22, -1.10),
        (0.64, 0.56, 0.76),
        charcoal,
        collection="V2 TECHNICAL",
        bevel=0.055,
    )
    add_box(
        "V2 P3B server cooling unit",
        (DIMS.service_x + 0.60, DIMS.server_center_y + 0.47, -0.66),
        (0.70, 0.34, 1.46),
        porcelain,
        collection="V2 TECHNICAL",
        bevel=0.055,
    )
    cooling_fan = add_cylinder(
        "V2 P3B server cooling fan",
        (DIMS.service_x + 0.60, DIMS.server_center_y + 0.285, -0.58),
        radius=0.23,
        depth=0.055,
        material=charcoal,
        collection="V2 TECHNICAL",
        vertices=40,
    )
    cooling_fan.rotation_euler.x = math.pi / 2

    conduit_x = DIMS.service_x + 0.63
    service_wall_y = 0.55
    conduit_segments = (
        (
            (DIMS.service_x + 0.58, DIMS.server_center_y - 0.40, -1.42),
            (conduit_x, service_wall_y, -1.42),
        ),
        ((conduit_x, service_wall_y, -1.42), (conduit_x, service_wall_y, 6.24)),
        (
            (conduit_x, service_wall_y, 0.48),
            (cabinet_x + 0.48, cabinet_y - 0.31, 0.48),
        ),
        (
            (conduit_x, service_wall_y, 2.86),
            (cabinet_x + 0.48, cabinet_y - 0.31, 2.86),
        ),
        (
            (conduit_x, service_wall_y, 5.02),
            (4.24, service_wall_y, 5.02),
        ),
        ((4.24, service_wall_y, 5.02), (4.24, 2.72, 5.02)),
    )
    for index, (start, end) in enumerate(conduit_segments, 1):
        add_beam_between(
            f"V2 P3B service path {index}",
            start,
            end,
            thickness=0.032,
            material=service_red,
            collection="V2 TECHNICAL",
        )
    add_beam_between(
        "V2 P3B flexible roof riser",
        (conduit_x, service_wall_y, 6.24),
        (conduit_x, service_wall_y, 7.46),
        thickness=0.032,
        material=service_red,
        collection="V2 TECHNICAL",
    )
    add_beam_between(
        "V2 P3B roof service path",
        (conduit_x, service_wall_y, 7.46),
        (2.72, -2.34, 7.95),
        thickness=0.032,
        material=service_red,
        collection="V2 TECHNICAL",
    )
    add_box(
        "V2 P3B bathroom controller",
        (4.24, 2.72, 5.04),
        (0.38, 0.10, 0.58),
        porcelain,
        collection="V2 TECHNICAL",
        bevel=0.06,
    )

    downlights = (
        ("living 1", -3.45, 0.05, 3.18),
        ("living 2", -3.45, 2.50, 3.18),
        ("hall", -0.10, -0.65, 3.18),
        ("kitchen", 3.20, 2.10, 3.18),
        ("bedroom 1", -3.35, 0.15, 6.05),
        ("bedroom 2", -3.35, 2.50, 6.05),
        ("bathroom 1", 3.10, 0.45, 6.05),
        ("bathroom 2", 4.05, 2.55, 6.05),
    )
    for name, x, y, z in downlights:
        add_cylinder(
            f"V2 P3B downlight {name}",
            (x, y, z),
            radius=0.085,
            depth=0.035,
            material=warm_glow,
            collection="V2 LIGHTING",
            vertices=24,
        )
        add_house_point_light(
            f"V2 P3B room light {name}",
            (x, y, z - 0.18),
            energy=46.0 if "bathroom" not in name else 38.0,
            color=(1.0, 0.67, 0.40),
            radius=0.34,
        )
    add_house_point_light(
        "V2 P3B server light",
        (DIMS.service_x + 0.35, DIMS.server_center_y + 0.30, -0.12),
        energy=16.0,
        color=(0.74, 0.84, 1.0),
        radius=0.52,
    )

    create_camera(
        "V2 Camera Distribution Detail",
        (7.8, -14.6, 3.0),
        (1.05, 0.62, 1.58),
        lens=80.0,
    )
    create_camera(
        "V2 Camera Server Detail",
        (7.8, -15.2, 0.55),
        (DIMS.service_x, DIMS.server_center_y, -0.72),
        lens=68.0,
    )
    parent_unparented_to_rebuild_root(
        "V2 INTERIOR", "V2 TECHNICAL", "V2 LIGHTING"
    )
    bpy.context.scene["hubmann_v2_phase3b"] = "complete"


def build_premium_architecture(materials: dict[str, bpy.types.Material]) -> None:
    """Add the architectural depth that the web hero needs at normal size.

    Earlier phases deliberately concentrated on plan correctness.  This pass
    keeps that plan intact and fixes the parts that make the house read as a
    blockout: broken slab edges, unsupported eaves, flat glazing and missing
    front-facing interior doors.
    """
    concrete = materials["concrete"]
    plaster = materials["plaster"]
    oak = materials["oak"]
    charcoal = materials["charcoal"]

    house_center_y = (DIMS.ground_front_y + DIMS.ground_rear_y) / 2
    roof_half_span = DIMS.width / 2 + DIMS.roof_overhang_x
    roof_depth = DIMS.depth + 2 * DIMS.roof_overhang_y
    roof_rise = DIMS.roof_ridge_z - DIMS.roof_eave_z
    roof_at_wall = DIMS.roof_ridge_z - roof_rise * (
        (DIMS.width / 2) / roof_half_span
    )
    upper_ceiling = DIMS.upper_ceiling_z - 0.14

    # The previous gable used the building width with the overhang pitch, so
    # its sloping edge could never meet the roof. Replace it with a rectangular
    # wall extension plus a correctly pitched triangle at both ends.
    remove_objects_with_prefix("V2 Facade front gable")
    for face, y, collection, prefix in (
        (
            "front",
            DIMS.ground_front_y + 0.08,
            "V2 FACADE",
            "V2 Facade premium",
        ),
        (
            "rear",
            DIMS.ground_rear_y - 0.08,
            "V2 EXTERIOR",
            "V2 Exterior rear premium",
        ),
    ):
        band_height = roof_at_wall - upper_ceiling
        add_box(
            f"{prefix} {face} gable bearing band",
            (0.0, y, upper_ceiling + band_height / 2),
            (DIMS.width - 0.20, 0.18, band_height),
            plaster,
            collection=collection,
            bevel=0.010,
        )
        add_triangular_prism(
            f"{prefix} {face} gable triangle",
            center_x=0.0,
            y=y,
            base_z=roof_at_wall - 0.015,
            width=DIMS.width - 0.20,
            height=DIMS.roof_ridge_z - roof_at_wall - 0.055,
            thickness=0.18,
            material=plaster,
            collection=collection,
        )

    # Continue the upper side walls to the real roof bearing height. This
    # removes the daylight slot previously visible below both eaves.
    side_extension_height = roof_at_wall - upper_ceiling
    for side, x, collection, name_prefix in (
        ("left", -DIMS.width / 2 + 0.10, "V2 EXTERIOR", "V2 Exterior left"),
        ("right", DIMS.width / 2 - 0.10, "V2 EXTERIOR", "V2 Exterior right"),
    ):
        add_box(
            f"{name_prefix} premium roof bearing wall",
            (x, house_center_y, upper_ceiling + side_extension_height / 2),
            (0.20, DIMS.depth - 0.38, side_extension_height),
            plaster,
            collection=collection,
            bevel=0.010,
        )

    # Continuous structural edge bands hide the seams of the stair-opening
    # slab pieces and create the crisp, monolithic concrete trays in the mockup.
    for name, y, z, width, depth, height in (
        ("foundation", DIMS.ground_front_y - 0.34, 0.02, 10.24, 0.18, 0.36),
        (
            "upper floor",
            DIMS.ground_front_y - 0.30,
            DIMS.upper_finish_z - 0.19,
            10.12,
            0.18,
            0.40,
        ),
        (
            "upper ceiling",
            DIMS.ground_front_y - 0.22,
            DIMS.upper_ceiling_z - 0.13,
            9.78,
            0.16,
            0.30,
        ),
    ):
        add_box(
            f"V2 Premium {name} front fascia",
            (0.0, y, z),
            (width, depth, height),
            concrete,
            collection="V2 STRUCTURE",
            bevel=0.018,
        )

    # The roof now visibly bears on two timber wall plates instead of hovering
    # above the upper storey. Fascia boards and gable bargeboards complete the
    # junction and move with the roof during the installation reveal.
    for side, x in (("left", -DIMS.width / 2 + 0.12), ("right", DIMS.width / 2 - 0.12)):
        add_box(
            f"V2 Premium eave bearing {side}",
            (x, house_center_y, roof_at_wall - 0.14),
            (0.24, DIMS.depth - 0.10, 0.24),
            oak,
            collection="V2 STRUCTURE",
            bevel=0.018,
        )
        add_box(
            f"V2 Roof premium fascia {side}",
            (
                -roof_half_span if side == "left" else roof_half_span,
                house_center_y,
                DIMS.roof_eave_z - 0.03,
            ),
            (0.16, roof_depth + 0.12, 0.26),
            oak,
            collection="V2 STRUCTURE",
            bevel=0.025,
        )

    front_roof_y = DIMS.ground_front_y - DIMS.roof_overhang_y - 0.03
    rear_roof_y = DIMS.ground_rear_y + DIMS.roof_overhang_y + 0.03
    for face, y in (("front", front_roof_y), ("rear", rear_roof_y)):
        for side, eave_x in (("left", -roof_half_span), ("right", roof_half_span)):
            add_beam_between(
                f"V2 Roof premium {face} bargeboard {side}",
                (0.0, y, DIMS.roof_ridge_z + 0.02),
                (eave_x, y, DIMS.roof_eave_z + 0.01),
                thickness=0.17,
                material=oak,
                collection="V2 STRUCTURE",
            )

    # Window sills and shallow shadow joints give the otherwise flat white
    # elevations scale, reveals and a believable construction depth.
    for name, x, bottom, width in (
        ("ground living", -3.05, 0.48, 1.95),
        ("ground dining", 2.85, 0.48, 2.15),
        ("upper bedroom", -3.05, 3.95, 1.80),
        ("upper bathroom", 1.75, 4.10, 1.15),
        ("upper gallery", 3.55, 4.00, 0.82),
    ):
        add_box(
            f"V2 Facade premium sill {name}",
            (x, DIMS.ground_front_y - 0.095, bottom - 0.055),
            (width + 0.22, 0.22, 0.085),
            concrete,
            collection="V2 FACADE",
            bevel=0.014,
        )
    add_box(
        "V2 Facade premium floor shadow joint",
        (0.0, DIMS.ground_front_y - 0.115, DIMS.upper_finish_z - 0.42),
        (DIMS.width - 0.20, 0.035, 0.045),
        charcoal,
        collection="V2 FACADE",
        bevel=0.006,
    )
    add_box(
        "V2 Exterior right premium floor shadow joint",
        (DIMS.width / 2 + 0.115, house_center_y, DIMS.upper_finish_z - 0.42),
        (0.035, DIMS.depth - 0.18, 0.045),
        charcoal,
        collection="V2 EXTERIOR",
        bevel=0.006,
    )

    # Two restrained timber fields break up the blank render facade and repeat
    # the vertical rhythm already used on the right elevation.
    for level, z, height, x_start in (
        ("ground", 1.66, 2.46, 0.58),
        ("upper", 4.78, 2.30, 2.62),
    ):
        for index in range(5):
            add_box(
                f"V2 Facade premium {level} timber slat {index + 1}",
                (x_start + index * 0.13, DIMS.ground_front_y - 0.085, z),
                (0.065, 0.10, height),
                oak,
                collection="V2 FACADE",
                bevel=0.009,
            )

    # Close the service room structurally against the foundation. It stays
    # open only on the camera side, exactly like the technical mockup.
    add_box(
        "V2 Server premium ceiling",
        (DIMS.service_x, DIMS.server_center_y, 0.02),
        (DIMS.server_width, DIMS.server_depth, 0.16),
        concrete,
        collection="V2 STRUCTURE",
        bevel=0.018,
    )

    # These front-facing leaves are the doors that the cutaway camera actually
    # sees. The plan-correct side doors remain in place as functional openings.
    def add_visible_interior_door(name: str, x: float, bottom: float, width: float = 0.88) -> None:
        y = DIMS.ground_rear_y - 0.205
        height = 2.12
        add_box(
            f"V2 Premium {name} leaf",
            (x, y, bottom + height / 2),
            (width, 0.075, height),
            oak,
            collection="V2 INTERIOR",
            bevel=0.028,
        )
        for suffix, frame_x in (("left", x - width / 2 - 0.055), ("right", x + width / 2 + 0.055)):
            add_box(
                f"V2 Premium {name} frame {suffix}",
                (frame_x, y - 0.012, bottom + height / 2),
                (0.075, 0.11, height + 0.14),
                plaster,
                collection="V2 INTERIOR",
                bevel=0.008,
            )
        add_box(
            f"V2 Premium {name} frame top",
            (x, y - 0.012, bottom + height + 0.05),
            (width + 0.18, 0.11, 0.075),
            plaster,
            collection="V2 INTERIOR",
            bevel=0.008,
        )
        add_box(
            f"V2 Premium {name} handle",
            (x + width * 0.31, y - 0.075, bottom + 1.03),
            (0.12, 0.055, 0.045),
            charcoal,
            collection="V2 INTERIOR",
            bevel=0.012,
        )

    add_visible_interior_door("ground hall door", -0.36, DIMS.ground_finish_z)
    add_visible_interior_door("upper bedroom door", -0.32, DIMS.upper_finish_z)
    add_visible_interior_door(
        "upper bathroom door", 3.54, DIMS.upper_finish_z, width=0.80
    )

    # Quiet oak skirtings prevent the rooms from reading as white boxes pasted
    # onto the floor and also visually connect the new door leaves.
    for level, z in (("ground", DIMS.ground_finish_z + 0.055), ("upper", DIMS.upper_finish_z + 0.055)):
        add_box(
            f"V2 Premium {level} rear skirting",
            (0.0, DIMS.ground_rear_y - 0.235, z),
            (DIMS.width - 0.42, 0.055, 0.11),
            oak,
            collection="V2 INTERIOR",
            bevel=0.006,
        )

    parent_unparented_to_rebuild_root(
        "V2 STRUCTURE", "V2 FACADE", "V2 EXTERIOR", "V2 INTERIOR"
    )
    bpy.context.scene["hubmann_v2_premium_architecture"] = "complete"


def build_phase4(materials: dict[str, bpy.types.Material]) -> None:
    """Create stable explosion groups and deliberate scroll-camera keyframes."""
    root = bpy.data.objects.get("V2 Rebuild width match")
    if root is None:
        raise RuntimeError("Phase 4 requires the V2 rebuild root")

    def animation_group(name: str) -> bpy.types.Object:
        group = bpy.data.objects.new(name, None)
        bpy.data.collections["V2 ANIMATION"].objects.link(group)
        group.parent = root
        return group

    roof_group = animation_group("V2 Animation roof group")
    front_group = animation_group("V2 Animation front facade group")
    right_group = animation_group("V2 Animation right facade group")
    pv_group = animation_group("V2 Animation PV group")
    server_group = animation_group("V2 Animation server group")
    pv_group.parent = roof_group

    roof_prefixes = (
        "V2 Roof",
        "V2 P3A front",
        "V2 P3A rear",
        "V2 P3B roof service path",
    )
    pv_prefixes = ("V2 PV", "V2 R4 PV", "V2 R5 PV")
    server_prefixes = ("V2 Server", "V2 Plan Server", "V2 P3B server")
    for obj in list(bpy.data.objects):
        if obj in {
            root,
            roof_group,
            front_group,
            right_group,
            pv_group,
            server_group,
        }:
            continue
        if obj.name.startswith(server_prefixes):
            obj.parent = server_group
        elif obj.name.startswith(pv_prefixes):
            obj.parent = pv_group
        elif obj.name.startswith(roof_prefixes):
            obj.parent = roof_group
        elif obj.name.startswith("V2 Facade"):
            obj.parent = front_group
        elif obj.name.startswith(("V2 Exterior right", "V2 P3A right")):
            obj.parent = right_group

    # Fade the two camera-facing skins as coherent architectural layers.  The
    # previous seven-metre translations exposed every wall segment and window
    # as separate flying objects, which made the building look broken.  A short
    # outward ease plus material dissolve reveals the section without ever
    # sacrificing the interior partitions.
    fade_inputs: list[bpy.types.NodeSocket] = []
    fade_materials: dict[bpy.types.Material, bpy.types.Material] = {}
    dissolve_objects = tuple(
        obj
        for obj in bpy.data.objects
        if obj.parent in {front_group, right_group} and hasattr(obj.data, "materials")
    )
    for obj in dissolve_objects:
        for slot in obj.material_slots:
            source = slot.material
            if source is None:
                continue
            faded = fade_materials.get(source)
            if faded is None:
                faded = source.copy()
                faded.name = f"{source.name} facade dissolve"
                faded.use_nodes = True
                nodes = faded.node_tree.nodes
                links = faded.node_tree.links
                output = nodes.get("Material Output")
                if output is None:
                    output = next(
                        (node for node in nodes if node.type == "OUTPUT_MATERIAL"),
                        None,
                    )
                if output is None or not output.inputs["Surface"].links:
                    continue
                surface_link = output.inputs["Surface"].links[0]
                opaque_socket = surface_link.from_socket
                links.remove(surface_link)
                transparent = nodes.new("ShaderNodeBsdfTransparent")
                transparent.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
                mix = nodes.new("ShaderNodeMixShader")
                mix.name = "V2 facade dissolve control"
                links.new(opaque_socket, mix.inputs[1])
                links.new(transparent.outputs["BSDF"], mix.inputs[2])
                links.new(mix.outputs["Shader"], output.inputs["Surface"])
                mix.inputs[0].default_value = 0.0
                try:
                    faded.surface_render_method = "DITHERED"
                except Exception:
                    pass
                fade_materials[source] = faded
                fade_inputs.append(mix.inputs[0])
            slot.material = faded

    panel_keyframes = (
        (1, 0.0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), 0.0),
        (26, 0.0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), 0.0),
        (32, 0.16, (0.0, -0.10, 0.0), (0.10, 0.0, 0.0), 0.42),
        (38, 0.66, (0.0, -0.22, 0.0), (0.22, 0.0, 0.0), 1.0),
        (52, 0.66, (0.0, -0.22, 0.0), (0.22, 0.0, 0.0), 1.0),
        (70, 0.66, (0.0, -0.22, 0.0), (0.22, 0.0, 0.0), 1.0),
        (82, 0.66, (0.0, -0.22, 0.0), (0.22, 0.0, 0.0), 1.0),
        (96, 0.66, (0.0, -0.22, 0.0), (0.22, 0.0, 0.0), 1.0),
        (102, 0.46, (0.0, -0.14, 0.0), (0.14, 0.0, 0.0), 0.68),
        (108, 0.18, (0.0, -0.04, 0.0), (0.04, 0.0, 0.0), 0.16),
        (112, 0.0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), 0.0),
        (120, 0.0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), 0.0),
    )
    flexible = bpy.data.objects.get("V2 P3B flexible roof riser")
    flexible_base_location = flexible.location.copy() if flexible is not None else None
    flexible_length = 1.22
    for frame, roof_lift, front_location, right_location, fade in panel_keyframes:
        roof_group.location = (0.0, 0.0, roof_lift)
        front_group.location = front_location
        right_group.location = right_location
        for group in (roof_group, front_group, right_group):
            group.keyframe_insert(data_path="location", frame=frame)
        if flexible is not None and flexible_base_location is not None:
            flexible.location = flexible_base_location + Vector((0.0, 0.0, roof_lift / 2))
            flexible.scale = (1.0, 1.0, 1.0 + roof_lift / flexible_length)
            flexible.keyframe_insert(data_path="location", frame=frame)
            flexible.keyframe_insert(data_path="scale", frame=frame)
        for fade_input in fade_inputs:
            fade_input.default_value = fade
            fade_input.keyframe_insert(data_path="default_value", frame=frame)

    # The planning state starts without modules.  They descend only during the
    # energy chapter and remain installed for the finished-house state.
    for frame, lift in (
        (1, 6.0),
        (28, 6.0),
        (40, 6.0),
        (52, 6.0),
        (70, 6.0),
        (82, 3.0),
        (92, 0.85),
        (104, 0.0),
        (120, 0.0),
    ):
        pv_group.location = (0.0, 0.0, lift)
        pv_group.keyframe_insert(data_path="location", frame=frame)

    # The underground service cell belongs to the installation chapter.  It
    # rises into the cutaway and clears the clean exterior hero states again.
    for frame, drop in (
        (1, -4.0),
        (28, -4.0),
        (40, 0.0),
        (52, 0.0),
        (70, 0.0),
        (82, 0.0),
        (92, -4.0),
        (104, -4.0),
        (120, -4.0),
    ):
        server_group.location = (0.0, 0.0, drop)
        server_group.keyframe_insert(data_path="location", frame=frame)

    contact_shadow = bpy.data.objects.get("V2 QA contact shadow")
    if contact_shadow is not None:
        for frame, y, z in (
            (1, -3.20, 0.02),
            (28, -3.20, 0.02),
            (40, DIMS.server_center_y, DIMS.server_floor_z - 0.10),
            (82, DIMS.server_center_y, DIMS.server_floor_z - 0.10),
            (92, -3.20, 0.02),
            (120, -3.20, 0.02),
        ):
            contact_shadow.location = (0.45, y, z)
            contact_shadow.keyframe_insert(data_path="location", frame=frame)

    camera = bpy.data.objects["V2 Camera Mockup"]
    camera_keyframes = (
        (1, (10.2, -34.8, 8.7), (0.0, -0.08, 3.30), 62.0),
        (26, (10.1, -34.4, 8.5), (0.0, -0.02, 3.28), 62.5),
        (38, (10.0, -33.8, 8.0), (0.10, 0.12, 3.18), 63.0),
        (52, (9.9, -33.5, 7.8), (0.18, 0.18, 3.08), 63.0),
        (70, (9.8, -33.2, 7.7), (0.28, 0.22, 3.04), 63.5),
        (82, (9.9, -33.5, 8.4), (0.40, 0.18, 3.72), 63.5),
        (96, (10.0, -33.9, 9.3), (0.58, 0.10, 4.62), 63.5),
        (102, (10.1, -34.3, 9.0), (0.36, 0.02, 3.88), 63.0),
        (112, (10.2, -34.8, 8.7), (0.12, -0.06, 3.38), 62.0),
        (120, (10.2, -34.8, 8.7), (0.0, -0.08, 3.30), 62.0),
    )
    for frame, location, target, lens in camera_keyframes:
        camera.location = location
        look_at(camera, target)
        camera.data.lens = lens
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame)
        camera.data.keyframe_insert(data_path="lens", frame=frame)

    bpy.context.scene.frame_set(1)
    bpy.context.scene["hubmann_v2_phase4"] = "complete"
    bpy.context.scene["hubmann_v2_animation_keyframes"] = (
        "1,26,32,38,52,70,82,96,102,108,112,120"
    )


def save_scene() -> None:
    BLEND_PATH.parent.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))


def script_args() -> set[str]:
    """Return only arguments passed to this script after Blender's ``--``."""
    if "--" not in sys.argv:
        return set()
    return set(sys.argv[sys.argv.index("--") + 1 :])


def render_phase1a_proofs() -> None:
    """Render the three agreed phase-1A stills and never the timeline."""
    scene = bpy.context.scene
    proof_dir = QA_DIR / "phase-01a-massing-v03"
    proof_dir.mkdir(parents=True, exist_ok=True)
    proofs = (
        ("V2 Camera Mockup", "01-mockup-three-quarter.png"),
        ("V2 Camera Right", "02-right-proportions.png"),
        ("V2 Camera Front", "03-front-proportions.png"),
    )
    for camera_name, filename in proofs:
        scene.camera = bpy.data.objects[camera_name]
        scene.render.filepath = str(proof_dir / filename)
        bpy.ops.render.render(write_still=True)


def render_still(
    camera_name: str,
    output_path: Path,
    *,
    mode: str,
) -> None:
    """Render one controlled V2 proof while restoring all visibility state."""
    scene = bpy.context.scene
    object_state = {obj: obj.hide_render for obj in bpy.data.objects}
    collection_state = {
        collection: collection.hide_render for collection in bpy.data.collections
    }
    try:
        for obj in bpy.data.objects:
            obj.hide_render = False
        for collection in bpy.data.collections:
            collection.hide_render = False

        # From phase 3 onward the detailed F2 collection is authoritative.
        # Never re-enable the retired blockouts during proof rendering.
        if bpy.data.collections.get("V2 DETAILED FURNITURE") is not None:
            bpy.data.collections["V2 FURNITURE"].hide_render = True

        if mode in {"cutaway", "plan_ground", "plan_upper", "plan_server"}:
            bpy.data.collections["V2 FACADE"].hide_render = True
        if mode == "cutaway":
            for obj in bpy.data.objects:
                if obj.name.startswith("V2 Exterior right") and "span 0" in obj.name:
                    obj.hide_render = True
                if (
                    obj.name.startswith((
                        "V2 R8 Ground partition",
                        "V2 R8 Upper partition",
                    ))
                    and "span 0" in obj.name
                ):
                    obj.hide_render = True
        if mode not in {"plan_ground", "plan_upper", "plan_server"}:
            bpy.data.collections["V2 PLAN"].hide_render = True
        if mode == "animation" and (
            scene.frame_current <= 28 or scene.frame_current >= 112
        ):
            # Closed exterior states do not need hundreds of occluded furniture
            # and lighting objects.  Hiding them keeps the 120-frame web render
            # practical without changing a visible pixel.
            for collection_name in (
                "V2 INTERIOR",
                "V2 LIGHTING",
                "V2 DETAILED FURNITURE",
            ):
                collection = bpy.data.collections.get(collection_name)
                if collection is not None:
                    collection.hide_render = True

        if mode == "plan_ground":
            hidden_prefixes = (
                "V2 Roof",
                "V2 PV",
                "V2 R5 PV",
                "V2 Rebuild red conduit",
                "V2 R4 distribution top conduit",
                "V2 R4 upper ceiling conduit",
                "V2 R5 distribution red outline",
                "V2 P3B service path",
                "V2 P3B flexible roof riser",
                "V2 P3B roof service path",
                "V2 P3B bathroom controller",
                "V2 Upper",
                "V2 Server",
                "V2 R4 bedroom",
                "V2 R4 bathroom",
                "V2 R5 rear upper",
                "V2 R5 bedroom",
                "V2 R5 bathroom",
                "V2 R7 bathroom",
                "V2 Rebuild bathroom",
                "V2 R8 Upper",
                "V2 R8 bedroom",
                "V2 R8 bathroom",
                "V2 Plan Upper",
                "V2 Plan Server",
                "F2 bedroom",
                "F2 bed ",
                "F2 nightstand",
                "F2 bedside",
                "F2 bathroom",
                "F2 vanity",
                "F2 basin",
                "F2 mirror",
                "F2 shower",
                "F2 rain shower",
                "F2 toilet",
            )
            for obj in bpy.data.objects:
                if obj.name.startswith(hidden_prefixes):
                    obj.hide_render = True
        elif mode == "plan_upper":
            hidden_prefixes = (
                "V2 Roof",
                "V2 PV",
                "V2 R5 PV",
                "V2 Rebuild red conduit",
                "V2 R4 distribution top conduit",
                "V2 R4 upper ceiling conduit",
                "V2 R5 distribution red outline",
                "V2 P3B service path",
                "V2 P3B flexible roof riser",
                "V2 P3B roof service path",
                "V2 P3B bathroom controller",
                "V2 Upper ceiling",
                "V2 Ground",
                "V2 Foundation",
                "V2 Front terrace",
                "V2 Entrance step",
                "V2 Server",
                "V2 R4 living",
                "V2 R4 kitchen",
                "V2 R4 dining",
                "V2 R4 distribution",
                "V2 R5 living",
                "V2 R5 distribution",
                "V2 R5 rear ground",
                "V2 R8 Ground",
                "V2 R8 living",
                "V2 Plan Ground",
                "V2 Plan Server",
                "F2 sofa",
                "F2 lounge",
                "F2 coffee",
                "F2 TV",
                "F2 plant",
                "F2 dining",
                "F2 chair",
                "F2 kitchen",
                "F2 tall cabinet",
                "F2 oven",
                "F2 cooktop",
                "F2 pendant",
            )
            for obj in bpy.data.objects:
                if obj.name.startswith(hidden_prefixes):
                    obj.hide_render = True
        elif mode == "plan_server":
            allowed_prefixes = (
                "V2 Server",
                "V2 Plan Server",
                "V2 P3B server",
                "V2 P3B service path 1",
            )
            for obj in bpy.data.objects:
                if obj.type in {"MESH", "FONT", "CURVE"} and not obj.name.startswith(
                    allowed_prefixes
                ):
                    obj.hide_render = True

        scene.camera = bpy.data.objects[camera_name]
        scene.render.filepath = str(output_path)
        bpy.ops.render.render(write_still=True)
    finally:
        for obj, hidden in object_state.items():
            obj.hide_render = hidden
        for collection, hidden in collection_state.items():
            collection.hide_render = hidden


def render_proof_set(
    dirname: str,
    proofs: tuple[tuple[str, str, str], ...],
) -> None:
    proof_dir = QA_DIR / dirname
    proof_dir.mkdir(parents=True, exist_ok=True)
    for camera_name, filename, mode in proofs:
        render_still(camera_name, proof_dir / filename, mode=mode)


def render_phase1b_proofs() -> None:
    render_proof_set(
        "phase-01b-layout-v01",
        (
            ("V2 Camera Mockup", "01-closed-facade.png", "facade"),
            ("V2 Camera Right", "02-right-facade.png", "facade"),
            ("V2 Plan Server", "03-server-plan.png", "plan_server"),
            ("V2 Plan Ground", "04-ground-plan.png", "plan_ground"),
            ("V2 Plan Upper", "05-upper-plan.png", "plan_upper"),
        ),
    )


def render_phase2a_proofs() -> None:
    render_proof_set(
        "phase-02a-architecture-v01",
        (
            ("V2 Camera Mockup", "01-open-cutaway.png", "cutaway"),
            ("V2 Plan Upper", "02-upper-plan.png", "plan_upper"),
            ("V2 Camera Right", "03-right-facade.png", "facade"),
        ),
    )


def render_phase2b_proofs() -> None:
    render_proof_set(
        "phase-02b-furniture-v03",
        (
            ("V2 Camera Mockup", "01-furnished-cutaway.png", "cutaway"),
            ("V2 Plan Ground", "02-ground-plan.png", "plan_ground"),
            ("V2 Plan Upper", "03-upper-plan.png", "plan_upper"),
            ("V2 Plan Server", "04-server-plan.png", "plan_server"),
        ),
    )


def render_rebuild_hero() -> None:
    dirname = os.environ.get("HUBMANN_V2_QA_DIR", "rebuild-current")
    render_proof_set(
        dirname,
        (("V2 Camera Mockup", "hero.png", "cutaway"),),
    )


def render_rebuild_validation() -> None:
    dirname = os.environ.get("HUBMANN_V2_QA_DIR", "rebuild-validation")
    render_proof_set(
        dirname,
        (
            ("V2 Camera Right", "01-right-facade.png", "facade"),
            ("V2 Plan Ground", "02-ground-plan.png", "plan_ground"),
            ("V2 Plan Upper", "03-upper-plan.png", "plan_upper"),
            ("V2 Plan Server", "04-server-plan.png", "plan_server"),
        ),
    )


def render_rebuild_plans() -> None:
    dirname = os.environ.get("HUBMANN_V2_QA_DIR", "rebuild-plans")
    render_proof_set(
        dirname,
        (
            ("V2 Plan Ground", "01-ground-plan.png", "plan_ground"),
            ("V2 Plan Upper", "02-upper-plan.png", "plan_upper"),
            ("V2 Plan Server", "03-server-plan.png", "plan_server"),
        ),
    )


def render_rebuild_layout_plans() -> None:
    dirname = os.environ.get("HUBMANN_V2_QA_DIR", "rebuild-layout-plans")
    render_proof_set(
        dirname,
        (
            ("V2 Plan Ground", "01-ground-plan.png", "plan_ground"),
            ("V2 Plan Upper", "02-upper-plan.png", "plan_upper"),
        ),
    )


def render_rebuild_layout_final() -> None:
    dirname = os.environ.get("HUBMANN_V2_QA_DIR", "rebuild-layout-final")
    render_proof_set(
        dirname,
        (
            ("V2 Plan Upper", "01-upper-plan.png", "plan_upper"),
            ("V2 Camera Mockup", "02-hero.png", "cutaway"),
        ),
    )


def render_phase3a_proofs() -> None:
    render_proof_set(
        "phase-03a-materials-v01",
        (
            ("V2 Camera Mockup", "01-material-cutaway.png", "cutaway"),
            ("V2 Camera Material Detail", "02-right-facade-detail.png", "facade"),
            ("V2 Camera Right", "03-right-facade.png", "facade"),
        ),
    )


def render_phase3b_proofs() -> None:
    render_proof_set(
        "phase-03b-technical-light-v01",
        (
            ("V2 Camera Mockup", "01-lit-cutaway.png", "cutaway"),
            (
                "V2 Camera Distribution Detail",
                "02-distribution-detail.png",
                "cutaway",
            ),
            ("V2 Camera Server Detail", "03-server-detail.png", "cutaway"),
        ),
    )


def render_phase4_keyframes() -> None:
    proof_dir = QA_DIR / "phase-04-animation-keyframes-v02"
    proof_dir.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    default_frames = (1, 38, 52, 70, 96, 120)
    frame_filter = os.environ.get("HUBMANN_V2_FRAMES", "").strip()
    frames = (
        tuple(int(value.strip()) for value in frame_filter.split(",") if value.strip())
        if frame_filter
        else default_frames
    )
    invalid = tuple(frame for frame in frames if frame not in default_frames)
    if invalid:
        raise ValueError(f"Unsupported Phase 4 proof frames: {invalid}")
    for frame in frames:
        scene.frame_set(frame)
        render_still(
            "V2 Camera Mockup",
            proof_dir / f"frame-{frame:03d}.png",
            mode="animation",
        )
    scene.frame_set(1)


def render_web_sequence() -> None:
    """Render V2 directly into the frame contract consumed by HouseStory."""
    scene = bpy.context.scene
    start = int(os.environ.get("HUBMANN_V2_FRAME_START", str(FRAME_START)))
    end = int(os.environ.get("HUBMANN_V2_FRAME_END", str(FRAME_END)))
    if start < FRAME_START or end > FRAME_END or start > end:
        raise ValueError(
            f"Invalid V2 web frame range {start}..{end}; expected "
            f"{FRAME_START}..{FRAME_END}"
        )

    sequence_dir = Path(
        os.environ.get("HUBMANN_V2_SEQUENCE_DIR", str(SEQUENCE_DIR))
    )
    sequence_dir.mkdir(parents=True, exist_ok=True)
    scene.render.resolution_x = int(os.environ.get("HUBMANN_V2_WEB_WIDTH", "1600"))
    scene.render.resolution_y = int(os.environ.get("HUBMANN_V2_WEB_HEIGHT", "900"))
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.quality = int(
        os.environ.get("HUBMANN_V2_WEB_QUALITY", "92")
    )
    scene.render.film_transparent = False
    if scene.render.engine == "BLENDER_EEVEE":
        scene.eevee.taa_render_samples = int(
            os.environ.get("HUBMANN_V2_WEB_SAMPLES", "12")
        )
        scene.eevee.use_fast_gi = False
        scene.eevee.volumetric_samples = 16
    bpy.data.objects["V2 Camera Mockup"].data.sensor_fit = "AUTO"

    for frame in range(start, end + 1):
        scene.frame_set(frame)
        render_still(
            "V2 Camera Mockup",
            sequence_dir / f"house-{frame:04d}.jpg",
            mode="animation",
        )
    scene.frame_set(1)


def render_final_model_proofs() -> None:
    proof_dir = QA_DIR / os.environ.get("HUBMANN_V2_FINAL_DIR", "final-model-v03")
    proof_dir.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.frame_set(120)
    proofs = (
        ("V2 Camera Mockup", "01-final-cutaway.png", "cutaway"),
        ("V2 Camera Right", "02-final-right-facade.png", "facade"),
        ("V2 Plan Ground", "03-final-ground-plan.png", "plan_ground"),
        ("V2 Plan Upper", "04-final-upper-plan.png", "plan_upper"),
        ("V2 Plan Server", "05-final-server-plan.png", "plan_server"),
        (
            "V2 Camera Distribution Detail",
            "06-final-distribution.png",
            "cutaway",
        ),
        ("V2 Camera Server Detail", "07-final-server.png", "cutaway"),
    )
    proof_filter = os.environ.get("HUBMANN_V2_FINAL_PROOFS", "").strip()
    selected = (
        {int(value.strip()) for value in proof_filter.split(",") if value.strip()}
        if proof_filter
        else set(range(1, len(proofs) + 1))
    )
    invalid = selected.difference(range(1, len(proofs) + 1))
    if invalid:
        raise ValueError(f"Unsupported final proof indices: {sorted(invalid)}")
    for index, (camera_name, filename, mode) in enumerate(proofs, 1):
        if index not in selected:
            continue
        render_still(camera_name, proof_dir / filename, mode=mode)
    scene.frame_set(1)


def main() -> None:
    args = script_args()
    if "--render-web-sequence-existing" in args:
        render_web_sequence()
        return
    if BUILD_STAGE not in VALID_STAGES:
        raise ValueError(
            f"Unknown HUBMANN_V2_STAGE={BUILD_STAGE!r}; expected one of {VALID_STAGES}"
        )
    implemented_stages = VALID_STAGES
    materials = build_phase0()
    stage_index = implemented_stages.index(BUILD_STAGE)
    if stage_index >= implemented_stages.index("phase1a"):
        build_phase1a(materials)
    if stage_index >= implemented_stages.index("phase1b"):
        build_phase1b(materials)
    if stage_index >= implemented_stages.index("phase2a"):
        build_phase2a(materials)
    if stage_index >= implemented_stages.index("phase2b"):
        build_phase2b(materials)
        build_rebuild_match_shell(materials)
        build_rebuild_match_anchors(materials)
        build_rebuild_match_furniture(materials)
        build_rebuild_match_presentation(materials)
        build_rebuild_match_layout(materials)
    if stage_index >= implemented_stages.index("phase3a"):
        build_final_detailed_furniture()
        build_phase3a(materials)
    if stage_index >= implemented_stages.index("phase3b"):
        build_phase3b(materials)
    if stage_index >= implemented_stages.index("phase4"):
        build_premium_architecture(materials)
        build_phase4(materials)
    save_scene()
    if "--render-phase1a-proofs" in args:
        if BUILD_STAGE != "phase1a":
            raise ValueError("Phase 1A proofs require HUBMANN_V2_STAGE=phase1a")
        render_phase1a_proofs()
    if "--render-phase1b-proofs" in args:
        if BUILD_STAGE != "phase1b":
            raise ValueError("Phase 1B proofs require HUBMANN_V2_STAGE=phase1b")
        render_phase1b_proofs()
    if "--render-phase2a-proofs" in args:
        if BUILD_STAGE != "phase2a":
            raise ValueError("Phase 2A proofs require HUBMANN_V2_STAGE=phase2a")
        render_phase2a_proofs()
    if "--render-phase2b-proofs" in args:
        if BUILD_STAGE != "phase2b":
            raise ValueError("Phase 2B proofs require HUBMANN_V2_STAGE=phase2b")
        render_phase2b_proofs()
    if "--render-rebuild-hero" in args:
        if BUILD_STAGE != "phase2b":
            raise ValueError("Rebuild hero requires HUBMANN_V2_STAGE=phase2b")
        render_rebuild_hero()
    if "--render-rebuild-validation" in args:
        if BUILD_STAGE != "phase2b":
            raise ValueError("Rebuild validation requires HUBMANN_V2_STAGE=phase2b")
        render_rebuild_validation()
    if "--render-rebuild-plans" in args:
        if BUILD_STAGE != "phase2b":
            raise ValueError("Rebuild plans require HUBMANN_V2_STAGE=phase2b")
        render_rebuild_plans()
    if "--render-rebuild-layout-plans" in args:
        if BUILD_STAGE != "phase2b":
            raise ValueError("Rebuild layout plans require HUBMANN_V2_STAGE=phase2b")
        render_rebuild_layout_plans()
    if "--render-rebuild-layout-final" in args:
        if BUILD_STAGE != "phase2b":
            raise ValueError("Rebuild layout final requires HUBMANN_V2_STAGE=phase2b")
        render_rebuild_layout_final()
    if "--render-phase3a-proofs" in args:
        if BUILD_STAGE != "phase3a":
            raise ValueError("Phase 3A proofs require HUBMANN_V2_STAGE=phase3a")
        render_phase3a_proofs()
    if "--render-phase3b-proofs" in args:
        if BUILD_STAGE != "phase3b":
            raise ValueError("Phase 3B proofs require HUBMANN_V2_STAGE=phase3b")
        render_phase3b_proofs()
    if "--render-phase4-keyframes" in args:
        if BUILD_STAGE != "phase4":
            raise ValueError("Phase 4 proofs require HUBMANN_V2_STAGE=phase4")
        render_phase4_keyframes()
    if "--render-web-sequence" in args:
        if BUILD_STAGE != "phase4":
            raise ValueError("The V2 web sequence requires HUBMANN_V2_STAGE=phase4")
        render_web_sequence()
    if "--render-final-model-proofs" in args:
        if BUILD_STAGE != "phase4":
            raise ValueError("Final proofs require HUBMANN_V2_STAGE=phase4")
        render_final_model_proofs()


if __name__ == "__main__":
    main()
