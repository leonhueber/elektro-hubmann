# Prompt-Spezifikationen

## 01 – Master Cutaway

```text
Use case: stylized-concept
Asset type: master architectural working mockup for accurate Blender reconstruction, landscape 3:2
Primary request: Create one exceptionally clear, high-fidelity 3D architectural cutaway of the SAME compact gable-roof house shown in the reference images. This is a geometry reference, not a marketing page.
Input images: Images 1-2 define the desired premium architectural rendering, materials and original house identity; Image 3 defines the current model massing and cutaway viewpoint; Images 4-5 define the authoritative current basement and upper-floor layouts.
Scene/backdrop: seamless neutral white/very light gray studio background with a soft contact shadow.
Subject and exact zoning: preserve a two-storey house above a small dedicated basement server room. Ground floor: living room left, central entrance and straight stair, electrical distribution/service core center-right, dining and kitchen right. Upper floor: bedroom left, central stair landing, fully enclosed bathroom center-right containing bathtub, shower, WC and vanity, and only a narrow gallery strip along the far-right exterior wall. Basement: a real walk-in server/network room directly below the service core, black server rack on the left, UPS/security equipment on the right, cooling and rear access.
Architecture: exposed concrete floor slabs and corner posts, clean white interior walls, pale oak floors and doors, warm timber roof structure and vertical right-facade slats, dark window frames, coherent right exterior wall with windows seated inside real wall openings—no overlaps or floating wall pieces.
Composition: orthographic-feeling three-quarter view from the front-right, full house centered and completely visible from roof ridge to basement floor. Remove only the front and near-right facade surfaces as a precise architectural section. Keep all remaining walls aligned. Slightly lift the complete roof as one aligned assembly just enough to reveal the upper level, without scattering parts.
Technical layer: one restrained red electrical route from the basement server room up through the ground-floor distribution cabinet and into upper-floor/bathroom and roof/PV systems. Keep it clean and physically continuous.
Lighting/mood: premium warm-white architectural visualization, crisp edges, readable room depth, balanced contrast, no fog.
Constraints: preserve the same house silhouette, proportions, right-side wall logic, room adjacency and service-stack alignment across all levels. Every room boundary must be unambiguous. The server room and all bathroom fixtures must be fully visible. Do not invent extra rooms or a second staircase.
Avoid: website chrome, logos, captions, callouts, labels, arrows, human figures, cars, landscaping, dramatic cinematic effects, fisheye, missing walls, overlapping windows, floating furniture, impossible stairs, duplicated fixtures, text, watermark.
```

## 02 – Technical Axonometric

```text
Use case: precise-object-edit
Asset type: technical architectural working mockup
Primary request: Transform Image 1 into a precise, orthographic-looking technical axonometric cutaway of the exact same house. Images 2–4 are supporting floor-plan references for spatial consistency only.
Input images: Image 1 is the edit target and controls the exact camera, crop, house silhouette, floor heights, room positions, opening positions, roof shape, basement server-room position, and overall composition. Images 2–4 are supporting references for the basement, ground-floor, and upper-floor layouts.
Scene/backdrop: seamless neutral off-white architectural studio background.
Subject: the same two-storey gable-roof house in the same three-quarter cutaway view, including the projecting underground server room. Ground floor: living area left, entrance and stairs in the middle, electrical distribution/service core center-right, dining and kitchen right. Upper floor: bedroom left, stair and hall middle, bathroom center-right, narrow gallery at far right. Basement server room directly beneath the service core, fully visible, with a black server rack on the left, UPS/security equipment on the right, cooling unit and a credible access opening.
Style/medium: high-end technical 3D architectural clay visualization; precise, calm, buildable and diagrammatically clear, not photorealistic lifestyle imagery.
Composition/framing: preserve Image 1's camera, crop, perspective/axonometric angle, proportions and silhouette exactly; complete building centered with all slabs and the server-room projection visible.
Lighting/mood: bright diffuse studio light, soft contact shadows, high legibility, no dramatic mood.
Color palette: warm white and pale-grey clay materials, light natural oak floors and restrained oak furniture footprints, dark charcoal roof/PV/window frames, one continuous saturated red electrical service strand.
Materials/textures: clearly readable concrete slab thicknesses, wall thicknesses, lintels, sills, window reveals, door openings, roof build-up and furniture footprints; crisp edges with slight bevels; subtle material separation, no visual clutter.
Technical installation: show one uninterrupted red service route from the basement server room upward to the ground-floor distribution cabinet, onward through the upper-floor bathroom/service zone, and finally to the photovoltaic array on the roof. Keep the route physically continuous and clean.
Critical invariants: change only the rendering/material language and technical clarity. Keep Image 1's exact house identity, geometry, room layout, camera, crop, roof and PV placement, facade proportions, stairs, server-room projection and furniture placement. The right exterior house wall must be solid construction with genuine recessed openings, clean lintels and reveals; no wall/window intersections, no coplanar overlap, no floating panes. Server room must remain fully visible and usable, with rack left, UPS/security right and access.
Constraints: one clean single image; no labels, no text, no dimension lines, no arrows, no legend, no UI, no people, no watermark.
Avoid: redesigning the house, changing camera or crop, adding rooms, moving the bathroom, moving the gallery, moving the server room, duplicated objects, malformed stairs, melted furniture, transparent exterior walls, overlapping walls and windows, broken red cable, red cable that stops between floors, excessive reflections, dramatic shadows, sketch lines, blueprint background.
```

## 03 – Animation Exploded

```text
Use case: stylized-concept
Asset type: production reference mockup for a 3D scroll-driven architectural animation
Input images: Image 1 is the primary edit target and absolute geometry/layout authority. Images 2 and 3 are style and controlled exploded-view references only.
Primary request: Transform only the assembly state of the exact house from Image 1 into a controlled exploded architectural view. Preserve the same house identity, front-right three-quarter camera, lens, silhouette, proportions, two-storey geometry, foundation and all room positions.
Scene/backdrop: seamless warm-white studio cyclorama with abundant negative white space around every displaced assembly, soft contact shadows, no horizon clutter.
Subject: the exact cutaway house from Image 1. Keep the entire furnished core fixed and fully visible: living room lower left, entry and stairs center, kitchen/dining lower right, bedroom upper left, bathroom immediately right of center upstairs, narrow gallery at the far right, central open electrical distribution cabinet, and the below-grade server/network room with black rack.
Exploded assembly: move the complete roof upward as one rigid aligned construction assembly; move the frontal facade shell toward the viewer as a small number of complete straight full-height panels; move the right facade shell to image-right as a small number of complete straight full-height panels; leave the load-bearing core, slabs, internal walls, furniture, distribution cabinet and server room stationary; maintain a continuous thin red electrical route from PV through the service core into the server room.
Style/medium: premium photorealistic 3D architectural visualization, precise CAD-like assembly logic, sharp clean edges, realistic scale.
Materials/textures: warm natural oak floors and rafters, white mineral plaster, pale architectural concrete, charcoal roof tiles, dark aluminum window frames, matte black PV panels, realistic but restrained material grain.
Composition/framing: centered landscape image, same slightly elevated front-right three-quarter view as Image 1, entire roof and all displaced facade panels fully inside frame, ample white space above roof and on both sides, server room fully inside the lower frame. Displacements must make motion directions self-evident through position alone.
Lighting/mood: bright diffuse premium studio light, soft ambient occlusion, calm technical clarity.
Constraints: change only the assembly state. Preserve Image 1 geometry, room arrangement, furniture placement, camera, material palette and house identity. PV panels remain attached to the roof. The bathroom remains upstairs immediately right of center; narrow gallery remains at the far right. The distribution cabinet and server room must be unobstructed and clearly visible. Keep all construction pieces physically plausible, straight, complete and aligned.
Avoid: arrows, labels, text, numbers, UI, logos, watermarks, dimensions, callout lines, people, cars, landscape, random floating furniture, detached furniture, fragmented walls, bent facade panels, duplicated elements, missing rooms, extra rooms, warped architecture, diagonal scatter, roof split into multiple floating parts, PV panels floating separately, broken red wire, cropped displaced parts.
```
