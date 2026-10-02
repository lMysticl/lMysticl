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

The browser uses native SVG motion paths and SMIL. Each six-second story starts
with a 0.8-second hyperspace arrival, followed by three seconds of pursuit and
crossfire. The X-wing's final forward volley defeats the interceptor at 3.8
seconds; a small impact flash and six fragments mark the hit. The winner
accelerates away and the next story enters from the opposite side. Two mirrored
passes repeat every 12 seconds, aligned with the scene's 48-second planet and
star clock. Both ships follow their tangent headings and use the same camera
views for their turns. Static and reduced-motion variants retain both fighters.
Cruisers are absent from the current web scene; their original modeling sources
remain available separately.
