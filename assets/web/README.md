# Lossless web renders

The original planet PNGs, 85-view fighter atlases, camera manifests and editable
Blender scenes remain the full-resolution sources. The profile embeds these six
derived WebP images once per SVG. The fighter atlases contain eight real camera
views each, selected from the originals without resizing or repainting.

Rebuild with the existing Pillow runtime (verified with Pillow 12.3.0):

```sh
python -B scripts/build_profile_web_assets.py
python -B scripts/build_profile_orbits.py
```

The producer checks decoded RGBA equality, including transparent RGB pixels,
before atomic replacement. The compact manifests retain each view's original
cannon/exhaust coordinates and bind its source PNG and manifest hashes.
`encoding-proof.json` records dimensions, sizes and hashes.

The browser uses native SVG motion paths and SMIL: a 1.05-second arrival runs
once, followed by a continuous 48-second pursuit. Both ships move forward along
their tangent headings and trade the pursuing role. Static and reduced-motion
variants retain both fighters. Cruisers are absent from the current web scene;
their original modeling sources remain available separately.
