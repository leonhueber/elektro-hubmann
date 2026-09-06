# Elektro Hubmann – Blender House Story

## Aktuelles Modell: V4

Die [ausgewählten V4-Mockups und Vorgaben](../docs/14-haus-v4-verbindliche-vorlage-und-kamerafahrten.md)
sind als `v4-reference-01` gesichert: zwei Vollgeschosse, Satteldach, detaillierte
Einrichtung und durchgängige Kamerafahrten. Das native V4-Modell liegt in
`assets/3d/elektro-hubmann-house-v4.blend`. Acht Ansichten lassen sich in Blender
über die Seitenleiste **V4 Haus** kontrollieren. Die separate Animationsdatei
`assets/3d/elektro-hubmann-house-v4-web.blend` enthält die durchgehende Kamera
und alle reversiblen Bewegungen für die Website.

[Modellumfang und Bedienung](house_v4/README.md) ·
[V4-Prüfbilder](../docs/version-g-qa/blender-v4/)
· [Animation und Web-Export](../docs/15-haus-v4-website-animation.md)

## Vorheriges Modell: V3 / R3

Das vollständige eingeschossige R3-Haus ist als neue Szene in
`assets/3d/elektro-hubmann-house-v3-r3.blend` aufgebaut. Es enthält Eltern- und
Kinderzimmer, Büro/Gast, Wohnküche, Bad/WC, Hauswirtschaft/Technik und den
durchgehenden Flur. Dachöffnung, Schnittwände, Beleuchtung und Beschattung sind
mit nativen Keyframes vorbereitet.

[Bedienung, Modellumfang und Renderbefehle](house_r3/README.md) ·
[Renderings und Prüfung](../docs/version-g-qa/blender-v3-r3/README.md)

Die folgenden V3-Befehle beschreiben die ältere zweigeschossige Szene.

## House V3

The first V3 visual design is paused following review. See the
[new design proposal](../docs/11-hausmodell-v3-gestalterischer-neustart.md)
before continuing modelling. The commands below describe the existing draft.

V3 is an earlier independent scene. It contains the complete two-storey
house, an animated roof and facade, electrical and network installations,
lighting, a moving blind, security devices and a photovoltaic installation.
The optional storage and wallbox collection is modelled but hidden pending
confirmation of the services offered.

- Source: `blender/house_v3.py` and `blender/house_v3/`
- Editable scene: `assets/3d/elektro-hubmann-house-v3.blend`
- Shared timeline: `src/config/house-v3-manifest.json`
- Generated frame aliases: `src/config/house-v3-frames.json`
- Projected component labels: `src/config/house-v3-annotations.json`
- Renders and QA: `docs/version-g-qa/blender-v3/`
- Website media: `public/images/version-g/house-v3/`

Build and save the scene without rendering:

```powershell
blender --background --python-exit-code 1 --python blender/house_v3.py
```

Render only selected proof frames:

```powershell
blender assets/3d/elektro-hubmann-house-v3.blend --background --python-exit-code 1 --python blender/house_v3.py -- --existing --proofs --frames 1,34,59,86,109,129,159,181
```

Render the two cameras separately, then create the website assets:

```powershell
blender assets/3d/elektro-hubmann-house-v3.blend --background --python-exit-code 1 --python blender/house_v3.py -- --existing --sequence desktop --samples 24
blender assets/3d/elektro-hubmann-house-v3.blend --background --python-exit-code 1 --python blender/house_v3.py -- --existing --sequence mobile --samples 24
python blender/house_v3/export_web.py
blender assets/3d/elektro-hubmann-house-v3.blend --background --python-exit-code 1 --python blender/house_v3/export_annotations.py
```

The conversion script needs Pillow. It checks that every required Blender
frame exists, composites the transparent renders onto white, writes WebP
files, and reuses identical hold images through the generated alias map.
`--start` and `--end` select a render range; all other ranges remain available.
Use `--width` only for proofs, as production dimensions belong to the manifest.

Validate the saved scene:

```powershell
blender assets/3d/elektro-hubmann-house-v3.blend --background --python-exit-code 1 --python blender/house_v3/validate_scene.py
```

Validation checks roof grouping, reversible animation, shell visibility,
optional-device visibility and framing through both cameras. All animation
is baked into normal Blender keyframes; the saved scene needs no Python
handlers or add-ons to play. Scene changes belong in the source modules before
rebuilding. V1 and V2 files are independent and are not overwritten.

## Earlier house source

The source scene for Version G is generated reproducibly with Blender Python.

## Requirements

- Blender 5.2 or newer
- No third-party Blender add-ons

## Generate the scene and a proof render

```powershell
blender --background --python blender/house_story.py -- --render-still
```

The default proof frame is frame 1. Set `HUBMANN_FRAME` to inspect another state.

For a compact visual review of all camera and model beats, render the curated
story proofs:

```powershell
blender --background --python blender/house_story.py -- --render-story-proofs
```

Set `HUBMANN_STORY_PROOF_FRAMES` to a comma-separated frame list when another
selection is needed.

To render a selected stable proof from the already generated `.blend` source
without rebuilding the procedural model, use:

```powershell
blender assets/3d/elektro-hubmann-house.blend --background --python blender/house_story.py -- --render-proofs-existing
```

Set `HUBMANN_PROOF_ONLY` to the requested proof filename or camera name.

## Render the three level plans

```powershell
blender --background --python blender/house_story.py -- --render-floorplans
```

This rebuilds the source scene and writes only the labelled server/technical,
ground- and upper-floor plans to `docs/version-g-qa/blender/floorplans/`. For
quick label, slice or presentation iterations, reuse the existing source scene
instead:

```powershell
blender assets/3d/elektro-hubmann-house.blend --background --python blender/house_story.py -- --render-floorplans-existing
```

Set `HUBMANN_FLOORPLAN_ONLY` to `basement`, `ground` or `upper` to render one
level only.

## Render the complete web sequence

```powershell
blender --background --python blender/house_story.py -- --render-animation
```

For a partial re-render, set `HUBMANN_FRAME_START` and `HUBMANN_FRAME_END`.
During model development, prefer the sparse story proofs and floor plans. The
complete 120-frame sequence is intended for the final approved model only.

The script writes:

- editable source scene: `assets/3d/elektro-hubmann-house.blend`
- proof renders: `docs/version-g-qa/blender/`
- story proof renders: `docs/version-g-qa/blender/story-proofs/`
- floor-plan renders: `docs/version-g-qa/blender/floorplans/`
- 120-frame web sequence: `public/images/version-g/sequence/`

The house is a fictional reference building derived from the approved visual mockup. It must not be presented as an actual Elektro Hubmann reference project.
