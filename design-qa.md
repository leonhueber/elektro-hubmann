# Design QA – Version G Blender House Story

## Visual reference

- `C:/Users/hueberl/.codex/codex-remote-attachments/01a04a96-8142-7883-a181-7e8b120d4281/1090ECC8-E82C-4C9C-9468-9D1B9FE9BACD/1-Foto-1.jpg`
- Reference size: 1280 × 910 px, desktop planning state.

## Current implementation evidence

- `docs/version-g-qa/blender-scroll-planning-1440x1024.png`
- `docs/version-g-qa/blender-scroll-installation-1440x1024.png`
- `docs/version-g-qa/blender-scroll-energy-1440x1024.png`
- `docs/version-g-qa/blender-scroll-service-1440x1024.png`
- `docs/version-g-qa/blender-static-mobile-390x844.png`
- Before/after animation audit in `docs/version-g-qa/animation-audit/`
- Blender proof renders in `docs/version-g-qa/blender/`
- Editable source scene: `assets/3d/elektro-hubmann-house.blend`
- Reproducible scene generator: `blender/house_story.py`

The persistent design-version switcher is a preview-only element and is not part of the selected design.

## Result

- The house is one coherent Blender scene instead of four unrelated image layers.
- Desktop and tablet use 120 rendered frames controlled by GSAP ScrollTrigger and a canvas. Normal page scrolling remains intact; no wheel interception or scroll-jacking is used.
- The front and right facade move sideways, the roof lifts away, the camera moves into the cutaway, photovoltaic modules fly into position, and the facade closes for the service state.
- The cutaway contains floors, partitions, furniture, distribution and network cabinets, KNX controls, lighting and a visible Hubmann-red installation route.
- The final state removes temporary technical equipment from the exterior while keeping the photovoltaic system.
- The 120 Blender frames now use a deliberately non-linear scroll timeline: opening the facade receives the largest part of the scroll distance, followed by the roof/PV assembly and the closing service state.
- The first frame, chapter transitions and important intermediate states are loaded first. Frames close to the current scroll target are requested immediately, so fast scrolling no longer leaves the canvas visibly frozen on an old image.
- The canvas adds restrained scale and vertical camera movement. Installation and energy callouts enter separately to make the system changes easier to follow.
- At widths below 621 px, a bandwidth-conscious sequence using every second Blender frame remains animated. Only `prefers-reduced-motion` replaces the animation with four complete vertical chapters, without information loss.
- The 390 × 844 check reports identical client and scroll width and therefore no horizontal overflow.
- The 1024 × 768 and 768 × 1024 tablet checks also report identical client and scroll width; the animated stage remains active.
- Header, progress rail, copy, CTAs and the house remain readable at the tested desktop and mobile sizes.
- Browser console check: no errors or warnings.

## Technical checks

- Astro check: passed with zero errors, warnings or hints.
- ESLint: passed.
- Vitest: 10/10 assertions passed.
- Production build: 26 static pages built successfully.

## Known content follow-ups

- The building is a fictional design model based on the approved mockup and must not be presented as a real Elektro Hubmann reference project.
- Project imagery and metadata still need verified real references.
- Legal pages still require Austrian legal and DSGVO review before production indexing.

final result: passed
