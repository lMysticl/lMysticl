# Cover artwork sources

The cover combines original Blender geometry and lighting with NASA surface
maps. The central daylight Earth shows the Americas with raised cloud geometry
and a thin blue atmosphere, without a monogram or city lights. Its ocean has
soft daylight reflections while the land stays matte. The web version uses
three color accents: golden Saturn, a lavender cratered Moon and a turquoise
cloud world. The Moon's relief keeps its source geometry; its tint is artistic.
Saturn's bands and separated ring geometry with differently colored particle
zones, atmospheric shells, starfield,
shooting stars and orbital animation are authored procedurally. This is an artistic scene, not a
scientific model of planetary positions or scale.

## Surface maps

- **Moon color and elevation:** NASA Scientific Visualization Studio,
  [CGI Moon Kit](https://svs.gsfc.nasa.gov/4720/), Ernie Wright;
  Lunar Reconnaissance Orbiter / LROC / LOLA. Color data credit:
  NASA / GSFC / Arizona State University.
  [Color map](https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/lroc_color_2k.jpg),
  [elevation map](https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/ldem_3_8bit.jpg).
- **Earth surface and clouds:** NASA Blue Marble, Reto Stöckli and Robert Simmon.
  [Background and image use](https://science.nasa.gov/blogs/earth-matters/2011/10/06/crafting-the-blue-marble/).
  [Surface map](https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57730/land_ocean_ice_2048.jpg),
  [cloud map](https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57747/cloud_combined_2048.jpg).

NASA source images retain their original attribution. No NASA endorsement is
implied. The central Earth and the optional natural cobalt satellite use the
Blue Marble cloud map. The turquoise world's turbulent clouds are procedural.

## Rebuild

From the repository root, using Blender 5.2 and Python 3. Use a fresh render
directory on E: for each iteration; the editable scene and master PNGs stay
outside Git. To build 960 px masters:

```text
blender --background --factory-startup --python-exit-code 1 --python scripts/render_profile_3d.py -- --out E:/CodexData/GeneratedImages/profile-planets-master --size 960 --samples 96 --backend HIP --vivid-satellites
```

Select an available Cycles backend explicitly (`HIP`, `CUDA`, `OPTIX`, `METAL`
or `CPU`); `--device-name 6950` can select the dedicated Radeon instead of also
using integrated graphics. The render saves a self-contained `.blend` with packed surface maps,
four transparent PNGs and a render manifest. The compositor embeds those PNGs
in each SVG so they work in GitHub's image context without external requests.
The `.blend` is a local working deliverable and is not committed to the profile.

Render the web assets at 640 px for Earth and 256 px for each satellite. PNG
compression is lossless; the smaller resolution matches their displayed size
with headroom for high density screens. `--asset-out` installs only PNGs and the
manifest with same-directory atomic replacement, then the compositor rebuilds
all eight themes/motion/layout variants:

```text
blender --background --factory-startup --python-exit-code 1 --python scripts/render_profile_3d.py -- --out E:/CodexData/GeneratedImages/profile-planets-web --asset-out assets/planets-3d --size 640 --satellite-size 256 --samples 96 --backend HIP --vivid-satellites
python scripts/build_profile_orbits.py
```

`--sprite core` can update only Earth. Re-render all four when lighting or shared
materials change. Camera framing, surface orientation and seed 42 stay fixed
across comparisons; exact pixels may vary across Blender versions and drivers.
The central subject stays Earth. Omit `--vivid-satellites` for the natural
Moon/Saturn/cobalt palette. Artistic satellite colors do not represent measured
planetary albedo.

Motion retains a 48-second seamless composition with 24/16/12-second orbits,
front/back occlusion and perspective scaling. Six shooting stars follow
staggered 12/16/24-second schedules. Three depth layers drift behind Earth with
16/24/48-second periods and repeatable tiles. Star points are batched into shared
SVG paths to avoid a separate DOM/paint node for each dot. All moving stars stay
behind the planetary scene and clear of the text. Reduced-motion visitors receive
a static composition with the three satellites and a stationary starfield.
