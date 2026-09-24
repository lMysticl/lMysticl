"""Render original Cycles planetary sprites; run with Blender --background --python.

The SVG compositor owns trajectories, text and full-banner sky. The saved .blend
owns sphere geometry, crater relief, ring gaps, metallic P and physical lighting.
"""
from pathlib import Path
import argparse
import json
import math
import random
import re
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
from profile_materials import LETTER
TEXTURES = Path(__file__).resolve().parents[1] / 'assets' / 'planets-3d' / 'textures'

args = argparse.ArgumentParser()
args.add_argument('--out', required=True)
args.add_argument('--size', type=int, default=640)
args.add_argument('--samples', type=int, default=48)
args.add_argument('--backend', choices=['HIP', 'CUDA', 'OPTIX', 'METAL', 'CPU'], default='HIP')
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
    selected = [d for d in prefs.devices if d.type == opts.backend]
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
    emission.inputs['Strength'].default_value = 2
    weight = node(m, 'ShaderNodeLayerWeight')
    weight.inputs['Blend'].default_value = .12
    mix = node(m, 'ShaderNodeMixShader')
    link(m, weight, 'Fresnel', mix, 0)
    link(m, trans, 'BSDF', mix, 1)
    link(m, emission, 'Emission', mix, 2)
    link(m, mix, 'Shader', n.get('Material Output'), 'Surface')
    sphere('Thin blue atmospheric scattering', radius, m, parent)


def ocean(parent, continents=False):
    m, p = material('Deep cobalt ocean', (.006, .038, .11), rough=.68)
    p.inputs['Specular IOR Level'].default_value = .2
    t = noise(m, 4.4, 8, .65)
    colors = ([(.28, (.004,.014,.045)),(.52,(.008,.075,.2)),
               (.57,(.075,.14,.078)),(.68,(.21,.23,.12))] if continents else
              [(.28,(.002,.011,.036)),(.53,(.005,.038,.115)),(.73,(.02,.12,.25))])
    r = ramp(m, t, colors)
    link(m, r, 'Color', p, 'Base Color')
    micro = noise(m, 110, 3)
    bump = node(m, 'ShaderNodeBump')
    bump.inputs['Strength'].default_value = .13
    bump.inputs['Distance'].default_value = .008
    link(m, micro, 'Fac', bump, 'Height')
    link(m, bump, 'Normal', p, 'Normal')
    if continents:
        land=image_texture(m,'earth-color.jpg')
        link(m,land,'Color',p,'Base Color')
    surface=sphere('Ocean surface', 1, m, parent)
    surface.rotation_euler=(math.radians(74),0,math.radians(-20))
    clouds, cp = material('Volumetric-looking layered cloud deck', (.79,.86,.94), rough=.77)
    c=image_texture(clouds,'earth-clouds.jpg',True)
    density=node(clouds,'ShaderNodeValToRGB')
    density.color_ramp.elements[0].position=.17
    density.color_ramp.elements[1].position=.84
    link(clouds,c,'Color',density,'Fac')
    bump = node(clouds, 'ShaderNodeBump')
    bump.inputs['Strength'].default_value = .3
    bump.inputs['Distance'].default_value = .007
    link(clouds, c, 'Color', bump, 'Height')
    link(clouds, bump, 'Normal', cp, 'Normal')
    trans = node(clouds, 'ShaderNodeBsdfTransparent')
    mix = node(clouds, 'ShaderNodeMixShader')
    link(clouds, density, 'Color', mix, 0)
    link(clouds, trans, 'BSDF', mix, 1)
    link(clouds, cp, 'BSDF', mix, 2)
    link(clouds, mix, 'Shader', clouds.node_tree.nodes.get('Material Output'), 'Surface')
    shell=sphere('Raised cloud shell', 1.014, clouds, parent)
    shell.rotation_euler=surface.rotation_euler
    atmosphere(parent, 1.017, (.07,.36,1))


def letter_polygons(path):
    tokens = re.findall(r'[MLHCZ]|-?\d+(?:\.\d+)?', path)
    i = 0
    current = (0, 0)
    loops, points = [], []
    while i < len(tokens):
        command = tokens[i]
        i += 1
        if command in ('M', 'L'):
            current = tuple(map(float, tokens[i:i+2])); i += 2
            points.append(current)
        elif command == 'H':
            current = (float(tokens[i]), current[1]); i += 1
            points.append(current)
        elif command == 'C':
            p0 = current
            p1,p2,p3 = [tuple(map(float,tokens[i+j:i+j+2])) for j in (0,2,4)]
            i += 6
            for step in range(1, 25):
                t = step / 24; u = 1-t
                points.append(tuple(u**3*p0[k]+3*u*u*t*p1[k]+3*u*t*t*p2[k]+t**3*p3[k] for k in (0,1)))
            current = p3
        elif command == 'Z':
            loops.append(points); points = []
        else:
            raise ValueError(command)
    return loops


core = group('Core and centered sculpted P')
ocean(core)
gold, gp = material('Satin champagne gold', (.9,.68,.32), metallic=1, rough=.21)
gp.inputs['Anisotropic'].default_value = .35
gc = node(gold, 'ShaderNodeTexCoord')
gm = node(gold, 'ShaderNodeVectorMath'); gm.operation = 'MULTIPLY'
gm.inputs[1].default_value = (1, 65, 4)
link(gold, gc, 'Generated', gm, 0)
grain = noise(gold, 65, 2)
link(gold, gm, 'Vector', grain, 'Vector')
gb = node(gold, 'ShaderNodeBump')
gb.inputs['Strength'].default_value = .04
gb.inputs['Distance'].default_value = .00035
link(gold, grain, 'Fac', gb, 'Height')
link(gold, gb, 'Normal', gp, 'Normal')
curve = bpy.data.curves.new('Original P outline with open counter', 'CURVE')
curve.dimensions = '2D'
curve.fill_mode = 'BOTH'
curve.extrude = .14
curve.bevel_depth = .042
curve.bevel_resolution = 7
for loop in letter_polygons(LETTER):
    spline = curve.splines.new('POLY')
    spline.points.add(len(loop)-1)
    for point, (x,y) in zip(spline.points, loop):
        point.co = ((x-8.5)*.0119, -(y+1)*.0119, 0, 1)
    spline.use_cyclic_u = True
letter = bpy.data.objects.new('P, real extrusion and rounded bevel', curve)
scene.collection.objects.link(letter)
letter.parent = core
letter.location = (0,0,1.035)
letter.rotation_euler = (math.radians(-10),math.radians(-19),0)
curve.materials.append(gold)
# Center the evaluated solid, including bevel and depth, in the image plane.
bpy.context.view_layer.update()
evaluated = letter.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh = evaluated.to_mesh()
points = [letter.matrix_world @ v.co for v in mesh.vertices]
center = [(min(p[k] for p in points)+max(p[k] for p in points))/2 for k in (0,1)]
letter.location.x -= center[0]
letter.location.y -= center[1]
evaluated.to_mesh_clear()
center_proof = {'before_xy': center, 'translation_xy': [-v for v in center], 'after_xy': [0,0]}

amber = group('Saturn with layered ring geometry')
m,p = material('Saturn atmospheric bands', (.5,.33,.15), rough=.66)
# Stretched fractal noise gives unequal atmospheric zones instead of a repeated
# sine-wave stripe pattern. Both atmosphere and ring plane share the same axis.
coordinates=node(m,'ShaderNodeTexCoord')
latitude=node(m,'ShaderNodeVectorMath');latitude.operation='MULTIPLY'
latitude.inputs[1].default_value=(.08,.08,6)
link(m,coordinates,'Generated',latitude,0)
zones=noise(m,6,4,.2)
link(m,latitude,'Vector',zones,'Vector')
r = ramp(m,zones,[(.2,(.4,.3,.18)),(.4,(.54,.43,.29)),(.55,(.7,.61,.44)),(.8,(.61,.48,.3))])
link(m,r,'Color',p,'Base Color')
saturn=sphere('Banded gas giant',1,m,amber)
saturn.rotation_euler=(math.radians(66),math.radians(-20),math.radians(18))
ringmat,rp = material('Icy ring particles',(.88,.78,.55),rough=.72)
rg = random.Random(39)
for j in range(34):
    inner = 1.22+j*.023
    if j in (12,13,24):
        continue
    outer=inner+rg.uniform(.01,.022)
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
color=image_texture(m,'moon-color.jpg');link(m,color,'Color',p,'Base Color')
height=image_texture(m,'moon-height.jpg',True)
bump=node(m,'ShaderNodeBump');bump.inputs['Strength'].default_value=.65;bump.inputs['Distance'].default_value=.045
link(m,height,'Color',bump,'Height');link(m,bump,'Normal',p,'Normal')
obj=sphere('Impact basin mesh',1,m,moon)
obj.rotation_euler=(math.radians(90),0,math.radians(20))
dem=bpy.data.textures.new('LOLA displacement','IMAGE');dem.image=height.image
modifier=obj.modifiers.new('Measured lunar terrain','DISPLACE');modifier.texture=dem
modifier.texture_coords='UV';modifier.strength=.035;modifier.mid_level=.5

earth=group('Ocean and continents satellite')
ocean(earth,True)
groups=[core,amber,moon,earth]
camera_data=bpy.data.cameras.new('Orthographic sprite camera')
camera=bpy.data.objects.new('Camera',camera_data);scene.collection.objects.link(camera)
camera.location=(0,0,7);camera.rotation_euler=(0,0,0)
camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler()
camera_data.type='ORTHO';scene.camera=camera
for name,position,power,size,color in [
    ('Warm broad key',(-3,4,2),500,3,(1,.93,.8)),
    ('Cool soft fill',(3,1,4),55,3,(.6,.78,1)),
    ('Blue atmosphere rim',(2,3,-2),750,2,(.28,.58,1)),
    ('Gold edge reflector',(-3,0,1),240,2,(1,.76,.42)),
]:
    light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;light.color=color
    obj=bpy.data.objects.new(name,light);scene.collection.objects.link(obj);obj.location=position
    obj.rotation_euler=(-obj.location).to_track_quat('-Z','Y').to_euler()

# Off-camera luminous studio cards produce long photographic reflections in gold.
for j,(x,y,w,h,power) in enumerate([(-1.1,1.1,2.2,.52,5),(1,-.7,1.8,.32,3),(0,-1.1,4,1,8)]):
    bpy.ops.mesh.primitive_plane_add(size=2,location=(x,y,3.2))
    card=bpy.context.object;card.name='Gold reflection card '+str(j)
    card.scale=(w/2,h/2,1);card.rotation_euler=(0,0,math.radians(32))
    card.visible_camera=False;card.visible_shadow=False;card.visible_diffuse=False
    cm=bpy.data.materials.new(card.name);cm.use_nodes=True
    cn=cm.node_tree.nodes;cn.clear()
    ce=cn.new('ShaderNodeEmission');ce.inputs['Color'].default_value=(1,.91,.72,1);ce.inputs['Strength'].default_value=power
    co=cn.new('ShaderNodeOutputMaterial');cm.node_tree.links.new(ce.outputs['Emission'],co.inputs['Surface'])
    card.data.materials.append(cm)

def hide_group(g, hidden):
    for obj in [g,*g.children_recursive]:
        obj.hide_render=hidden

for g,name,scale in [(core,'core',2.42),(amber,'amber',4.18),(moon,'moon',2.22),(earth,'ocean',2.28)]:
    for other in groups:
        hide_group(other,other!=g)
    camera_data.ortho_scale=scale
    scene.render.filepath=str(out/(name+'.png'))
    bpy.ops.render.render(write_still=True)
for other in groups:
    hide_group(other,other!=core)
camera_data.ortho_scale=2.42
for mat in list(bpy.data.materials):
    if not mat.users:
        bpy.data.materials.remove(mat)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'profile-planets.blend'))
(out/'render-manifest.json').write_text(json.dumps({'blender':bpy.app.version_string,'engine':'CYCLES','device':[d.name for d in selected] or ['CPU'],'samples':opts.samples,'seed':42,'size':opts.size,'view_transform':'AgX','packed_textures':[p.name for p in sorted(TEXTURES.glob('*.jpg'))],'source_outline':'profile_materials.LETTER','letter_centering':center_proof,'sprites':['core','amber','moon','ocean']},indent=2)+'\n',encoding='utf-8',newline='\n')
print('SPRITES_COMPLETE',out)
