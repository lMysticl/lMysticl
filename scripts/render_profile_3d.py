"""Render original Cycles planetary sprites; run with Blender --background --python.

The SVG compositor owns trajectories, text and full-banner sky. The saved .blend
owns the daylight Earth, crater relief, ring gaps and physical lighting.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
TEXTURES = Path(__file__).resolve().parents[1] / 'assets' / 'planets-3d' / 'textures'
CORE_ORIENTATION = (-74, 0, -12)
CORE_CLOUD_RANGE = (.29, .94)

args = argparse.ArgumentParser()
args.add_argument('--out', required=True)
args.add_argument('--asset-out', help='Atomically install rendered PNGs and manifest into the compositor asset directory')
args.add_argument('--size', type=int, default=640)
args.add_argument('--satellite-size', type=int, help='Render satellites at a smaller web resolution')
args.add_argument('--samples', type=int, default=48)
args.add_argument('--sprite', choices=['core', 'amber', 'moon', 'ocean'])
args.add_argument('--vivid-satellites', action='store_true', help='Use amber, lavender and turquoise satellite accents')
args.add_argument('--backend', choices=['HIP', 'CUDA', 'OPTIX', 'METAL', 'CPU'], default='HIP')
args.add_argument('--device-name', help='Select a GPU by a case-insensitive name fragment')
opts = args.parse_args(sys.argv[sys.argv.index('--') + 1:])
out = Path(opts.out)
out.mkdir(parents=True, exist_ok=True)
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
if opts.backend != 'CPU':
    prefs.compute_device_type = opts.backend
    prefs.get_devices()
    selected = [d for d in prefs.devices if d.type == opts.backend and
                (not opts.device_name or opts.device_name.lower() in d.name.lower())]
    if not selected:
        raise RuntimeError(f'No {opts.backend} device; choose an available --backend explicitly')
    for device in prefs.devices:
        device.use = device in selected
    scene.cycles.device = 'GPU'
else:
    selected = []
    scene.cycles.device = 'CPU'
scene.cycles.samples = opts.samples
scene.cycles.use_denoising = True
scene.cycles.seed = 42
scene.render.resolution_x = opts.size
scene.render.resolution_y = opts.size
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.compression = 100
scene.render.film_transparent = True
scene.view_settings.view_transform = 'AgX'
scene.world.color = (.025, .025, .025)


def material(name, color, metallic=0, rough=.45):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = rough
    return m, p


def node(mat, kind):
    return mat.node_tree.nodes.new(kind)


def link(mat, a, output, b, input):
    mat.node_tree.links.new(a.outputs[output], b.inputs[input])


def ramp(mat, texture, stops):
    r = node(mat, 'ShaderNodeValToRGB')
    for e in list(r.color_ramp.elements)[2:]:
        r.color_ramp.elements.remove(e)
    for i, (position, color) in enumerate(stops):
        e = r.color_ramp.elements[i] if i < 2 else r.color_ramp.elements.new(position)
        e.position = position
        e.color = (*color, 1)
    link(mat, texture, 'Fac', r, 'Fac')
    return r


def noise(mat, scale, detail=6, distortion=0):
    t = node(mat, 'ShaderNodeTexNoise')
    t.inputs['Scale'].default_value = scale
    t.inputs['Detail'].default_value = detail
    t.inputs['Roughness'].default_value = .7
    t.inputs['Distortion'].default_value = distortion
    return t


def image_texture(mat, name, data=False):
    texture = node(mat, 'ShaderNodeTexImage')
    texture.image = bpy.data.images.load(str(TEXTURES / name), check_existing=True)
    if data:
        texture.image.colorspace_settings.name = 'Non-Color'
    texture.image.pack()
    return texture


def linear_color(hex_color):
    values = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values)


WORLD_PALETTES = {
    'turquoise': ['#06394F', '#147B91', '#45CAC2', '#B4EEE1', '#299CAC'],
    'violet': ['#202249', '#554299', '#996ACE', '#C6B7E7', '#607DC0'],
    'amber': ['#653317', '#B16429', '#D89645', '#FFE2A4', '#B97640'],
    'coral': ['#4A2740', '#9E415B', '#D97972', '#F6C7B0', '#B575AB'],
}


def cloud_world(parent, palette, atmosphere_color, orientation=CORE_ORIENTATION):
    m, p = material(parent.name + ' cloud bands', linear_color(palette[2]), rough=.48)
    p.inputs['Specular IOR Level'].default_value = .32
    coordinates = node(m, 'ShaderNodeTexCoord')
    latitude = node(m, 'ShaderNodeVectorMath')
    latitude.operation = 'MULTIPLY'
    latitude.inputs[1].default_value = (1.2, 1.2, 4)
    link(m, coordinates, 'Generated', latitude, 0)
    turbulence = noise(m, 4.2, 6, 1.2)
    link(m, latitude, 'Vector', turbulence, 'Vector')
    colors = ramp(m, turbulence, list(zip((.18, .36, .49, .62, .8), map(linear_color, palette))))
    link(m, colors, 'Color', p, 'Base Color')
    relief = node(m, 'ShaderNodeBump')
    relief.inputs['Strength'].default_value = .12
    relief.inputs['Distance'].default_value = .007
    link(m, turbulence, 'Fac', relief, 'Height')
    link(m, relief, 'Normal', p, 'Normal')
    surface = sphere('Turbulent cloud world', 1, m, parent)
    surface.rotation_euler = tuple(map(math.radians, orientation))
    atmosphere(parent, 1.017, atmosphere_color)


def sphere(name, radius, mat, parent):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=192, ring_count=96, radius=radius)
    obj = bpy.context.object
    obj.name = name
    obj.parent = parent
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def group(name):
    obj = bpy.data.objects.new(name, None)
    scene.collection.objects.link(obj)
    return obj


def atmosphere(parent, radius, color):
    m, p = material(parent.name + ' atmosphere', color)
    n = m.node_tree.nodes
    n.remove(p)
    trans = node(m, 'ShaderNodeBsdfTransparent')
    emission = node(m, 'ShaderNodeEmission')
    emission.inputs['Color'].default_value = (*color, 1)
    emission.inputs['Strength'].default_value = 2.2
    weight = node(m, 'ShaderNodeLayerWeight')
    weight.inputs['Blend'].default_value = .12
    edge = node(m, 'ShaderNodeMath')
    edge.operation = 'POWER'
    edge.inputs[1].default_value = 2.5
    link(m, weight, 'Fresnel', edge, 0)
    mix = node(m, 'ShaderNodeMixShader')
    link(m, edge, 'Value', mix, 0)
    link(m, trans, 'BSDF', mix, 1)
    link(m, emission, 'Emission', mix, 2)
    link(m, mix, 'Shader', n.get('Material Output'), 'Surface')
    sphere('Thin blue atmospheric scattering', radius, m, parent)


def ocean(parent, continents=False, orientation=(74, 0, -20), cloud_range=(.40, .97)):
    m, p = material('Deep cobalt ocean', (.006, .038, .11), rough=.28)
    p.inputs['Specular IOR Level'].default_value = .4
    p.inputs['IOR'].default_value = 1.333
    t = noise(m, 4.4, 8, .65)
    colors = ([(.28, (.004,.014,.045)),(.52,(.008,.075,.2)),
               (.57,(.075,.14,.078)),(.68,(.21,.23,.12))] if continents else
              [(.28,(.003,.018,.065)),(.53,(.008,.075,.24)),(.73,(.025,.18,.42))])
    r = ramp(m, t, colors)
    link(m, r, 'Color', p, 'Base Color')
    micro = noise(m, 110, 3)
    bump = node(m, 'ShaderNodeBump')
    bump.inputs['Strength'].default_value = .08
    bump.inputs['Distance'].default_value = .004
    link(m, micro, 'Fac', bump, 'Height')
    link(m, bump, 'Normal', p, 'Normal')
    if continents:
        land=image_texture(m,'earth-color.jpg')
        grade = node(m, 'ShaderNodeHueSaturation')
        grade.inputs['Saturation'].default_value = 1.12
        grade.inputs['Value'].default_value = .92
        link(m, land, 'Color', grade, 'Color')
        link(m, grade, 'Color', p, 'Base Color')
        # Dark ocean texels reflect the broad daylight key; brighter land stays
        # matte. This keeps the existing Blue Marble map and coast alignment.
        roughness = node(m, 'ShaderNodeValToRGB')
        roughness.color_ramp.elements[0].position = .08
        roughness.color_ramp.elements[0].color = (.32, .32, .32, 1)
        roughness.color_ramp.elements[1].position = .38
        roughness.color_ramp.elements[1].color = (.64, .64, .64, 1)
        link(m, land, 'Color', roughness, 'Fac')
        link(m, roughness, 'Color', p, 'Roughness')
    surface=sphere('Ocean surface', 1, m, parent)
    surface.rotation_euler=tuple(map(math.radians, orientation))
    clouds, cp = material('Raised white cloud deck', (.92,.96,1), rough=.74)
    c=image_texture(clouds,'earth-clouds.jpg',True)
    density=node(clouds,'ShaderNodeValToRGB')
    density.color_ramp.elements[0].position=cloud_range[0]
    density.color_ramp.elements[1].position=cloud_range[1]
    link(clouds,c,'Color',density,'Fac')
    bump = node(clouds, 'ShaderNodeBump')
    bump.inputs['Strength'].default_value = .2
    bump.inputs['Distance'].default_value = .007
    link(clouds, c, 'Color', bump, 'Height')
    link(clouds, bump, 'Normal', cp, 'Normal')
    trans = node(clouds, 'ShaderNodeBsdfTransparent')
    mix = node(clouds, 'ShaderNodeMixShader')
    link(clouds, density, 'Color', mix, 0)
    link(clouds, trans, 'BSDF', mix, 1)
    link(clouds, cp, 'BSDF', mix, 2)
    link(clouds, mix, 'Shader', clouds.node_tree.nodes.get('Material Output'), 'Surface')
    shell=sphere('Raised cloud shell', 1.01, clouds, parent)
    shell.rotation_euler=surface.rotation_euler
    atmosphere(parent, 1.017, (.055,.32,.9))


core = group('Daylight Earth without a monogram')
ocean(core, True, CORE_ORIENTATION, cloud_range=CORE_CLOUD_RANGE)


amber = group('Saturn with layered ring geometry')
m,p = material('Saturn atmospheric bands', (.5,.33,.15), rough=.62)
# Stretched fractal noise gives unequal atmospheric zones instead of a repeated
# sine-wave stripe pattern. Both atmosphere and ring plane share the same axis.
coordinates=node(m,'ShaderNodeTexCoord')
latitude=node(m,'ShaderNodeVectorMath');latitude.operation='MULTIPLY'
latitude.inputs[1].default_value=(.08,.08,6)
link(m,coordinates,'Generated',latitude,0)
zones=noise(m,6,4,.2)
link(m,latitude,'Vector',zones,'Vector')
band_colors = ([(.2, linear_color('#733914')), (.4, linear_color('#C28035')),
                (.55, linear_color('#FFDF9B')), (.8, linear_color('#D3A56A'))]
               if opts.vivid_satellites else
               [(.2,(.32,.22,.12)),(.4,(.54,.4,.24)),(.55,(.8,.69,.48)),(.8,(.65,.49,.27))])
r = ramp(m, zones, band_colors)
link(m,r,'Color',p,'Base Color')
saturn=sphere('Banded gas giant',1,m,amber)
saturn.rotation_euler=(math.radians(66),math.radians(-20),math.radians(18))
rg = random.Random(39)
for j in range(34):
    inner = 1.22+j*.023
    if j in (12,13,24):
        continue
    outer=inner+rg.uniform(.01,.022)
    zone_color = ((.34,.28,.2) if j < 8 else
                  (.86,.78,.6) if j < 19 else
                  (.5,.41,.29) if j < 25 else (.72,.63,.46))
    if opts.vivid_satellites:
        zone_color = linear_color('#9B6635' if j < 8 else '#FFDDA1' if j < 19 else
                                  '#B58450' if j < 25 else '#E8B26B')
    variation = .92 + .12 * math.sin(j * 2.4)
    ringmat, rp = material('Icy ring band ' + str(j),
                           tuple(c * variation for c in zone_color), rough=.58)
    verts=[]
    for k in range(256):
        a=2*math.pi*k/256
        for radius in (inner,outer):
            verts.append((radius*math.cos(a),radius*math.sin(a),0))
    faces=[(2*k,2*k+1,(2*k+3)%512,(2*k+2)%512) for k in range(256)]
    mesh=bpy.data.meshes.new('Ring annulus'); mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new('Ring band '+str(j),mesh);scene.collection.objects.link(obj)
    obj.parent=amber; obj.rotation_euler=(math.radians(66),math.radians(-20),math.radians(18))
    mesh.materials.append(ringmat)

moon=group('Cratered mineral moon')
m,p=material('Lunar regolith from LROC',(.36,.4,.43),rough=.86)
color=image_texture(m,'moon-color.jpg')
neutral = node(m, 'ShaderNodeHueSaturation')
neutral.inputs['Saturation'].default_value = .35
neutral.inputs['Value'].default_value = 1.04
link(m, color, 'Color', neutral, 'Color');link(m, neutral, 'Color', p, 'Base Color')
if opts.vivid_satellites:
    tint = node(m, 'ShaderNodeMixRGB')
    tint.blend_type = 'MULTIPLY'
    tint.inputs[0].default_value = .72
    tint.inputs[2].default_value = (*linear_color('#B8A1EE'), 1)
    link(m, neutral, 'Color', tint, 1);link(m, tint, 'Color', p, 'Base Color')
p.inputs['Specular IOR Level'].default_value = .18
height=image_texture(m,'moon-height.jpg',True)
bump=node(m,'ShaderNodeBump');bump.inputs['Strength'].default_value=.55;bump.inputs['Distance'].default_value=.055
link(m,height,'Color',bump,'Height');link(m,bump,'Normal',p,'Normal')
obj=sphere('Impact basin mesh',1,m,moon)
obj.rotation_euler=(math.radians(90),0,math.radians(20))
dem=bpy.data.textures.new('LOLA displacement','IMAGE');dem.image=height.image
modifier=obj.modifiers.new('Measured lunar terrain','DISPLACE');modifier.texture=dem
modifier.texture_coords='UV';modifier.strength=.035;modifier.mid_level=.5

earth=group('Turquoise cloud satellite' if opts.vivid_satellites else 'Cobalt ocean satellite')
if opts.vivid_satellites:
    cloud_world(earth, WORLD_PALETTES['turquoise'], (.04, .5, .65), (74, 0, -20))
else:
    ocean(earth)
groups=[core,amber,moon,earth]
camera_data=bpy.data.cameras.new('Orthographic sprite camera')
camera=bpy.data.objects.new('Camera',camera_data);scene.collection.objects.link(camera)
camera.location=(0,0,7);camera.rotation_euler=(0,0,0)
camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler()
camera_data.type='ORTHO';scene.camera=camera
for name,position,power,size,color in [
    ('Daylight key',(-3.5,4.5,5),600,3,(1,.97,.92)),
    ('Cool soft fill',(3,-1,3),85,4,(.52,.7,1)),
    ('Blue atmosphere rim',(2,3,-2),600,1.8,(.28,.58,1)),
    ('Soft warm bounce',(-4,-1,1),70,3,(1,.92,.8)),
]:
    light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;light.color=color
    obj=bpy.data.objects.new(name,light);scene.collection.objects.link(obj);obj.location=position
    obj.rotation_euler=(-obj.location).to_track_quat('-Z','Y').to_euler()

def hide_group(g, hidden):
    for obj in [g,*g.children_recursive]:
        obj.hide_render=hidden

for g,name,scale in [(core,'core',2.42),(amber,'amber',4.18),(moon,'moon',2.22),(earth,'ocean',2.28)]:
    if opts.sprite and name != opts.sprite:
        continue
    for other in groups:
        hide_group(other,other!=g)
    camera_data.ortho_scale=scale
    size = opts.size if name == 'core' else opts.satellite_size or opts.size
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.filepath=str(out/(name+'.png'))
    bpy.ops.render.render(write_still=True)
for other in groups:
    hide_group(other,other!=core)
camera_data.ortho_scale=2.42
scene.render.resolution_x = scene.render.resolution_y = opts.size
for mat in list(bpy.data.materials):
    if not mat.users:
        bpy.data.materials.remove(mat)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'profile-planets.blend'))
manifest = {
    'blender': bpy.app.version_string,
    'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'engine': 'CYCLES',
    'device': [d.name for d in selected] or ['CPU'],
    'samples': opts.samples,
    'seed': 42,
    'size': opts.size,
    'satellite_size': opts.satellite_size or opts.size,
    'png_compression': 100,
    'view_transform': 'AgX',
    'packed_textures': [p.name for p in sorted(TEXTURES.glob('*.jpg'))],
    'vivid_satellites': opts.vivid_satellites,
    'core': {'subject': 'daylight Earth', 'monogram': False, 'city_lights': False,
             'orientation_degrees': CORE_ORIENTATION,
             'cloud_range': CORE_CLOUD_RANGE},
    'rendered_sprites': [opts.sprite] if opts.sprite else ['core', 'amber', 'moon', 'ocean'],
}
(out/'render-manifest.json').write_text(
    json.dumps(manifest, indent=2)+'\n', encoding='utf-8', newline='\n')
if opts.asset_out:
    assets = Path(opts.asset_out)
    assets.mkdir(parents=True, exist_ok=True)
    for name in [*(sprite + '.png' for sprite in manifest['rendered_sprites']),
                 'render-manifest.json']:
        pending = assets / (name + '.tmp')
        pending.write_bytes((out / name).read_bytes())
        pending.replace(assets / name)
