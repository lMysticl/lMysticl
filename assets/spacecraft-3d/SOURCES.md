# Original spacecraft for the profile cover

Aster and Vesper are original procedural Blender models with no imported meshes,
textures or logos. The requested visual reference was the four separated wings
and four engine pods of the [X-wing starfighter](https://www.starwars.com/databank/x-wing-starfighter).
Aster adds a long angular prow, layered armor, foil radiators, canopy hardware,
engine feed conduits and open nozzles with flange bolts and stators. Vesper has
a faceted cockpit, two radiator shields with recessed cells and rim fasteners,
coolant conduits, cooling slots and two forward cannons.

## Reproduce the renders

The producer is `scripts/render_profile_ship.py`, verified with Blender 5.2.1
LTS, Cycles, HIP on the Radeon RX 6950 XT, AgX, seed 42 and 96 samples. Choose
an available backend explicitly. Every output directory must be new. Master
renders are 1200 × 900, with a self-contained editable `.blend`, transparent
PNG and render manifest. They are local deliverables outside this repository.

```text
blender --background --factory-startup --python-exit-code 1 --python scripts/render_profile_ship.py -- --model aster --out E:/CodexData/GeneratedImages/aster-master --width 1200 --samples 96 --backend HIP --device-name 6950
blender --background --factory-startup --python-exit-code 1 --python scripts/render_profile_ship.py -- --model interceptor --out E:/CodexData/GeneratedImages/vesper-master --width 1200 --samples 96 --backend HIP --device-name 6950
```

The web sprites use 320 × 240 for Aster and 256 × 192 for Vesper. The PNG and
JSON manifest are installed with same-directory atomic replacement. The
manifest contains the projected engine and cannon muzzle coordinates used by
the SVG compositor.

```text
blender --background --factory-startup --python-exit-code 1 --python scripts/render_profile_ship.py -- --model aster --out E:/CodexData/GeneratedImages/aster-web --asset-out assets/spacecraft-3d --width 320 --samples 96 --backend HIP --device-name 6950
blender --background --factory-startup --python-exit-code 1 --python scripts/render_profile_ship.py -- --model interceptor --out E:/CodexData/GeneratedImages/vesper-web --asset-out assets/spacecraft-3d --width 256 --samples 96 --backend HIP --device-name 6950
python scripts/build_profile_orbits.py
```

## Motion and image contract

`scripts/profile_ship.py` supplies the shared sprite definitions, exhaust,
curved approach and departure paths, and four short cyan/amber laser volleys.
Shots start at the rendered cannon muzzle coordinates. The 48-second loop has
a four-second intro offset, so the exchange appears near the first page load.
After the exchange Aster passes behind Earth and exits below it; Vesper turns
away above it. Earth draws in front of both ships and the shots.

The mobile layout stages the exchange left of Earth, below both description
lines. Its clipping region is y=390–516 in the 620 × 580 viewBox. The desktop
clip keeps the scene to the right of the profile copy. Static and reduced-motion
variants retain both ships. The two PNG definitions are embedded once per SVG
and reused; the animation uses SVG/SMIL without runtime JavaScript, WebGL or
external image requests. The added 3D detail is baked into those sprites.

The accepted Earth/satellite PNGs, original orbit geometry and timing, rich
starfield and six meteors are preserved. This is an artistic space vignette,
with no claim of physically accurate spacecraft, planetary scale or combat.
