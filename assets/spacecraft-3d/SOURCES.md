# Spacecraft for the profile cover

Aster and Vesper are authored procedural Blender models. The film references
are the [X-wing](https://www.starwars.com/databank/x-wing-starfighter) and
[TIE fighter](https://www.starwars.com/databank/tie-fighter): a long nose with
four separated S-foils and engines, and a compact cockpit between two hexagonal
panel wings. Both retain layered armor, mechanical seams, fasteners, radiator
cells, open nozzles, conduits and cockpit hardware. No imported meshes,
textures or movie footage are embedded in the product.

Flight staging was informed by the actual official clips
[Use the Force, Luke](https://www.starwars.com/video/use-the-force-luke) and
[Into the Trap](https://www.starwars.com/video/into-the-trap). The adopted
mechanisms are forward movement through a brief exchange, bank into a flowing
break, and decreasing apparent size on departure. The miniature detail approach
is also described in [ILM's Rogue One discussion](https://www.ilm.com/john-knoll-discusses-rogue-one/).

## Reproduce the master renders

The producer is `scripts/render_profile_ship.py`, verified with Blender 5.2.1
LTS, Cycles, HIP on the Radeon RX 6950 XT, AgX and seed 42. Choose an available
backend explicitly. Every output directory must be new. Master portraits are
1200 x 900, with a self-contained editable `.blend`, transparent PNG and render
manifest. These larger local deliverables are saved outside this repository.

```text
blender --background --factory-startup --python-exit-code 1 --python scripts/render_profile_ship.py -- --model aster --out E:/CodexData/GeneratedImages/aster-master --width 1200 --samples 96 --backend HIP --device-name 6950
blender --background --factory-startup --python-exit-code 1 --python scripts/render_profile_ship.py -- --model interceptor --out E:/CodexData/GeneratedImages/vesper-master --width 1200 --samples 96 --backend HIP --device-name 6950
```

## Build the changing 3D views

`--flight` renders 85 actual bank/pitch attitudes per model using the canonical
`profile_flight.py` choreography. Camera framing stays fixed throughout the
view set; perspective scale is applied by the final scene. The saved flight
`.blend` includes the attitude keyframes for inspection and editing.

```text
blender --background --factory-startup --python-exit-code 1 --python scripts/render_profile_ship.py -- --flight --model aster --out E:/CodexData/GeneratedImages/aster-views --width 192 --samples 48 --backend HIP --device-name 6950
blender --background --factory-startup --python-exit-code 1 --python scripts/render_profile_ship.py -- --flight --model interceptor --out E:/CodexData/GeneratedImages/vesper-views --width 144 --samples 48 --backend HIP --device-name 6950
python scripts/build_flight_atlas.py --source E:/CodexData/GeneratedImages/aster-views --assets assets/spacecraft-3d --stem aster-ship
python scripts/build_flight_atlas.py --source E:/CodexData/GeneratedImages/vesper-views --assets assets/spacecraft-3d --stem vesper-interceptor
python scripts/build_profile_orbits.py
```

The atlas builder preserves tile dimensions and projected cannon/engine
coordinates. It uses a 256-color RGBA palette and records its measured pixel
error, source hashes and tile map. PNGs and JSON manifests are installed by
same-directory atomic replacement. One shared PNG is embedded per ship in each
SVG; the base view remains opaque while the next view fades in, retaining the
hull silhouette between attitudes. All native animations use the same parent
SMIL clock, including view windows that target nested SVG viewports.

## Motion and consumer contract

`profile_flight.py` remains the source of the retained real 3D attitude renders.
`profile_battle.py` maps those views onto four connected fleet passes in 48
seconds. Hull heading follows the current projected path velocity; changing
real atlas views supply bank and depth pitch. Arrival brakes from a short jump,
ordinary combat maintains forward motion, and departure accelerates. Brief
colored light transfers link each craft's exit to its next entrance.

`profile_ship.py` applies those poses, interpolates the rendered views and
launches three red bursts and three green bursts on each pass from the current cannon
coordinates. Each fast impulse keeps its forward launch vector after leaving
the barrel. The 48-second loop has a four-second intro offset: the encounter
appears immediately after page load. Fleet passes enter from four directions;
the same ships return after each short departure instead of leaving the scene
empty for the remainder of the sky loop. Narrow flares, local light streaks
and short longitudinal hull stretches explain the hyperspace transitions.

Two original distant capital ships, Aurora and Vanguard, have layered hulls,
bridge/sensor structures, deck machinery, turrets, cooling grilles and five
engine nozzles each. `render_profile_cruisers.py` builds 129/131 mesh objects
using the existing Blender 5.2/Cycles helpers. Seed 42, 48 samples, AgX and the
named RX 6950 XT HIP device match the recorded manifest. Their two 320 x 240
RGBA views are shared once per SVG; slower ordinary movement and lower contrast
place them behind the fighters. They arrive and jump away with the fleet.
The editable scene and 1600 x 1000 inspection plate are retained outside Git.

The mobile exchange is staged left of Earth, below both description lines.
Its clipping region is y=390-516 in the 620 x 580 viewBox. The desktop clip
keeps the scene to the right of the profile copy. Static and reduced-motion
variants retain both ships and a still exchange. There are no runtime scripts,
WebGL contexts or external image requests in the SVG. The accepted Earth and
three colorful satellite PNGs, original orbit geometry/periods, three-layer
moving starfield and six meteors are preserved.
