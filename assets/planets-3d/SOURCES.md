# Cover artwork sources

The cover combines original Blender geometry and lighting with NASA surface
maps. The gold P is extruded from the custom outline in `profile_materials.py`.
Saturn's bands and separated ring geometry, atmospheric shells, starfield and
orbital animation are authored procedurally. This is an artistic scene, not a
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
implied. The central ocean planet also uses the Blue Marble cloud map.

## Rebuild

From the repository root, using Blender 5.2 and Python 3:

```text
blender --background --factory-startup --python-exit-code 1 --python scripts/render_profile_3d.py -- --out assets/planets-3d --size 640 --samples 96 --backend HIP
python scripts/build_profile_orbits.py
```

Select an available Cycles backend explicitly (`HIP`, `CUDA`, `OPTIX`, `METAL`
or `CPU`). The render saves a self-contained `.blend` with packed surface maps,
four transparent PNGs and a render manifest. The compositor embeds those PNGs
in each SVG so they work in GitHub's image context without external requests.
The `.blend` is a local working deliverable and is not committed to the profile.

Motion retains a 48-second seamless composition with 24/16/12-second orbits,
front/back occlusion and perspective scaling. The background stays still.
Reduced-motion visitors receive a static composition.
