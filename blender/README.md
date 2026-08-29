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

## Render the complete web sequence

```powershell
blender --background --python blender/house_story.py -- --render-animation
```

For a partial re-render, set `HUBMANN_FRAME_START` and `HUBMANN_FRAME_END`.

The script writes:

- editable source scene: `assets/3d/elektro-hubmann-house.blend`
- proof renders: `docs/version-g-qa/blender/`
- 120-frame web sequence: `public/images/version-g/sequence/`

The house is a fictional reference building derived from the approved visual mockup. It must not be presented as an actual Elektro Hubmann reference project.
