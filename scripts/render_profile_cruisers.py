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


def cruiser(name, variant, blockout=False):
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
        frames.append({'model':name,'mesh_objects':len(col.objects),'file':dest.name,
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
