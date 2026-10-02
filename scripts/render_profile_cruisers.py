"""Author two original layered capital ships, Cycles HIP, transparent web views.

Uses the project's already validated Blender 5.2 modeling/light helpers. No
imported meshes or textures. The full editable scene and inspection plate stay
outside Git; only compact RGBA views and their producer manifest enter assets.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
import render_profile_ship as h


def capsule(name, center, length, radius_y, radius_z, mat):
    """A smooth original ellipsoidal hull, constructed without imported meshes."""
    cx,cy,cz=center
    rings=12;steps=24
    vertices=[]
    for ring in range(rings+1):
        a=math.pi*(.018+.964*ring/rings)
        x=cx-math.cos(a)*length/2
        for i in range(steps):
            t=i*math.tau/steps
            vertices.append((x,cy+math.sin(a)*radius_y*math.cos(t),cz+math.sin(a)*radius_z*math.sin(t)))
    faces=[tuple(reversed(range(steps))),tuple(range(rings*steps,(rings+1)*steps))]
    faces.extend((r*steps+i,r*steps+(i+1)%steps,(r+1)*steps+(i+1)%steps,(r+1)*steps+i)
                 for r in range(rings) for i in range(steps))
    obj=h.mesh(name,vertices,faces,mat,0)
    for p in obj.data.polygons:p.use_smooth=p.index>1
    return obj


def rounded_cruiser(name,blockout):
    h.SHIP=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(h.SHIP)
    hull=h.material(name+' | warm ceramic alloy',(.46,.40,.31),.48,.36)
    ribs=h.material(name+' | champagne ribs',(.29,.27,.23),.7,.33)
    dark=h.material(name+' | recessed conduits',(.035,.042,.045),.55,.4)
    glow=h.material(name+' | amber engine cores',(1,.40,.12),.1,.23,3)
    window=h.material(name+' | warm observation windows',(1,.48,.18),.1,.28,.8)
    capsule(name+' | organic elongated hull',(0,0,0),7.0,1.0,.60,hull)
    capsule(name+' | raised command pod',(-.85,0,.64),1.8,.52,.50,hull)
    capsule(name+' | dorsal sensor blister',(.92,0,.52),1.3,.27,.22,ribs)
    for side in (-1,1):
        for i,(x,l,w) in enumerate([(-2.15,1.7,.34),(-.8,1.85,.36),(.82,1.9,.39),(2.05,1.15,.27)]):
            capsule(name+f' | side gondola {side}:{i}',(x,side*.9,.08),l,w,.26,hull)
            h.cylinder(name+f' | gondola spine {side}:{i}',(x-l*.3,side*.98,.29),(x+l*.3,side*.98,.29),.018,ribs,12,.002)
        if not blockout:
            for i in range(18):
                x=-2.7+i*.3
                y=side*math.sqrt(max(.01,1-(x/3.5)**2))*.84
                h.box(name+f' | observation port {side}:{i}',(x,y,.29),(.055,.019,.025),window,.003)
            for i in range(6):
                x=-1.75+i*.58
                capsule(name+f' | recessed service blister {side}:{i}',(x,side*.5,.51),.34,.10,.075,dark)
                h.cylinder(name+f' | turret pedestal {side}:{i}',(x,side*.73,.35),(x,side*.73,.43),.072,ribs,16)
                h.cylinder(name+f' | slim turret barrel {side}:{i}',(x,side*.73,.44),(x+.19,side*.73,.44),.014,ribs,10,.002)
    for i,y in enumerate((-.42,0,.42)):
        h.tube(name+f' | circular engine nozzle {i}',-3.62,-3.24,y,0,.21,.15,ribs,24)
        h.cylinder(name+f' | amber engine core {i}',(-3.61,y,0),(-3.59,y,0),.147,glow,24,.002)
    if not blockout:
        for i in range(13):
            a=i*math.tau/13
            h.box(name+f' | command pod viewport {i}',(-.85+.68*math.cos(a),.39*math.sin(a),.83),(.065,.035,.035),window,.003)
        for i in range(10):
            x=-2.4+i*.48
            h.box(name+f' | segmented dorsal armor {i}',(x,0,.59),(.22,.18,.025),ribs,.006)
    return h.SHIP


def cruiser(name, variant, blockout=False):
    if variant:return rounded_cruiser(name,blockout)
    h.SHIP=bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(h.SHIP)
    metal=h.material(name+' | pale titanium',(.34,.41,.49),.62,.38)
    edge=h.material(name+' | deck plates',(.19,.25,.33),.68,.34)
    dark=h.material(name+' | recessed machinery',(.025,.044,.067),.5,.42)
    glow=h.material(name+' | blue engine',(.2,.62,1),.15,.26,2.8)
    glass=h.material(name+' | bridge windows',(.1,.34,.55),.3,.24,1)
    prow=4.1 if variant==0 else 3.3
    stern=-3.1
    # Broad layered wedge, a split prow on the second capital ship.
    shape=[(stern,-1.55,-.22),(stern,1.55,-.22),(prow,0,-.22),
           (stern,-1.55,.22),(stern,1.55,.22),(prow,0,.02)]
    h.mesh(name+' | wedge hull',shape,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],metal,.035)
    for deck in range(3):
        length=5.2-deck*.92
        w=1.12-deck*.25
        x=stern+.5+deck*.18
        h.wing_panel(name+f' | raised deck {deck}',[(x,-w,.31+deck*.12),(x,w,.31+deck*.12),
                       (x+length,0,.31+deck*.12),(x+length-.45,-w*.15,.31+deck*.12)],(0,0,1),edge,.1)
    h.box(name+' | bridge pedestal',(-1.85,0,.85),(1.0,.62,.52),metal,.025)
    h.box(name+' | bridge command deck',(-1.9,0,1.14),(.74,1.28,.24),edge,.025)
    h.box(name+' | observation slit',(-1.50,0,1.16),(.016,1.08,.05),glass,.002)
    for side in (-1,1):
        h.cylinder(name+f' | sensor mast {side}',(-1.96,side*.44,1.27),(-1.96,side*.44,1.57),.022,edge,12)
        h.box(name+f' | sensor array {side}',(-1.96,side*.44,1.57),(.2,.22,.055),metal,.008)
        if variant:
            h.box(name+f' | outrigger {side}',(-.25,side*.92,.22),(2.8,.24,.18),metal,.025)
    for j,y in enumerate((-.97,-.49,0,.49,.97)):
        h.tube(name+f' | engine nozzle {j}',-3.5,-3.15,y,0,.16,.11,edge,24)
        h.cylinder(name+f' | blue engine core {j}',(-3.48,y,0),(-3.46,y,0),.107,glow,24,.002)
    if not blockout:
        for side in (-1,1):
            for i in range(15):
                x=-2.6+i*.34
                w=1.30*(prow-x)/(prow+2.6)
                h.box(name+f' | armor seam {side}:{i}',(x,side*w*.82,.28),(.012,w*.26,.016),dark,.002)
                h.box(name+f' | hull window {side}:{i}',(x,side*w,-.015),(.075,.018,.035),glass,.002)
            for i in range(6):
                x=-2.45+i*.55
                h.box(name+f' | machinery terrace {side}:{i}',(x,side*.38,.72),(.28,.16,.065),metal,.012)
                h.box(name+f' | cooling grille {side}:{i}',(x,side*.38,.76),(.16,.12,.017),dark,.003)
                h.cylinder(name+f' | turret {side}:{i}',(x,side*.69,.38),(x,side*.69,.45),.09,edge,16)
                h.cylinder(name+f' | turret barrel {side}:{i}',(x,side*.69,.46),(x+.22,side*.69,.46),.018,metal,10,.002)
    return h.SHIP


def run(args):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='HIP';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='HIP' and '6950' in d.name
    devices=[d.name for d in prefs.devices if d.use]
    assert devices,'Named HIP GPU is absent'
    scene.cycles.device='GPU';scene.cycles.samples=8 if args.blockout else 48
    scene.cycles.seed=42;scene.cycles.use_denoising=True
    scene.render.film_transparent=True
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.25
    world=bpy.data.worlds.new('Distant cool space light');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.25;scene.world=world
    h.light('Neutral distant key',(2,-4,10),1000,(.86,.92,1),7)
    h.light('Cool deck rim',(-5,6,4),850,(.4,.64,1),6)
    h.light('Stern fill',(-6,-3,2),280,(.62,.76,1),5)
    data=bpy.data.cameras.new('Capital ship inspection camera');cam=bpy.data.objects.new('Camera',data)
    scene.collection.objects.link(cam);scene.camera=cam;data.type='ORTHO';data.ortho_scale=8.6
    cam.location=(0,-7,10);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler()
    args.out.mkdir(parents=True,exist_ok=True)
    collections=[cruiser(name,i,args.blockout) for i,name in enumerate(('aurora','vanguard'))]
    frames=[]
    for i,col in enumerate(collections):
        for c in collections:c.hide_render=c!=col
        scene.render.resolution_x=128 if args.blockout else 320;scene.render.resolution_y=round(scene.render.resolution_x*.75)
        name=col.name;dest=args.out/(name+('-blockout' if args.blockout else '')+'.png')
        scene.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
        center,nose=[world_to_camera_view(scene,cam,Vector(p)) for p in [(0,0,0),(1,0,0)]]
        frames.append({'model':name,'type':'rounded gondola cruiser' if i else 'angular wedge destroyer','mesh_objects':len(col.objects),'file':dest.name,
                       'nose_angle_degrees':math.degrees(math.atan2(-(nose.y-center.y),nose.x-center.x)),
                       'png_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    if args.blockout:
        print('CRUISER_SMOKE_PASS '+json.dumps({'devices':devices,'frames':frames}));return
    for i,col in enumerate(collections):
        col.hide_render=False
        for obj in col.objects:obj.location.y += 2.3 if i else -2.3
    data.ortho_scale=11.5;cam.location=(-1,-9,13);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.filepath=str(args.out/'cruisers-detail.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(args.out/'cruisers.blend'),check_existing=False)
    bpy.ops.render.render(write_still=True)
    manifest={'schema_version':1,'blender':bpy.app.version_string,'engine':'CYCLES','backend':'HIP','devices':devices,
              'samples':48,'seed':42,'external_assets':[],'frames':frames,
              'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'helper_sha256':hashlib.sha256(Path(h.__file__).read_bytes()).hexdigest()}
    (args.out/'cruisers.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print('CRUISERS_RENDER_PASS '+json.dumps({'devices':devices,'objects':[f['mesh_objects'] for f in frames]}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--blockout',action='store_true')
    run(p.parse_args(sys.argv[sys.argv.index('--')+1:]))
