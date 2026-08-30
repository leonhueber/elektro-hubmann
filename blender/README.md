# Elektro Hubmann – Blender House Story

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
