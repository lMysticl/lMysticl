"""Build and render the original Aster spacecraft with Blender 5.2/Cycles.

Four swept split foils and four engine pods follow the user's X-wing reference;
all geometry and materials are authored here without imported model assets.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils import Quaternion, Vector
from bpy_extras.object_utils import world_to_camera_view

sys.path.insert(0, str(Path(__file__).resolve().parent))
from profile_flight import VIEW_TIMES, view_pose


def material(name, color, metal=0, rough=.35, emission=0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metal
    shader.inputs['Roughness'].default_value = rough
    if emission:
        shader.inputs['Emission Color'].default_value = (*color, 1)
        shader.inputs['Emission Strength'].default_value = emission
    return mat


def mesh(name, vertices, faces, mat, bevel=.018):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    obj = bpy.data.objects.new(name, data)
    SHIP.objects.link(obj)
    data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Manufactured edge bevel', 'BEVEL')
        mod.width, mod.segments = bevel, 2
        mod.harden_normals = True
    return obj


def box(name, center, size, mat, bevel=.018):
    c, s = Vector(center), Vector(size)/2
    vertices = [tuple(c+Vector((x*s.x,y*s.y,z*s.z)))
                for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),
                              (1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
    return mesh(name, vertices, [(0,4,6,2),(1,3,7,5),(0,1,5,4),
                               (2,6,7,3),(0,2,3,1),(4,5,7,6)], mat, bevel)


def cylinder(name, start, end, radius, mat, sides=24, bevel=.007):
    a,b = Vector(start),Vector(end)
    axis = (b-a).normalized()
    u = axis.cross(Vector((0,0,1)) if abs(axis.z)<.9 else Vector((0,1,0))).normalized()
    v = axis.cross(u)
    vertices = [tuple(p+radius*(math.cos(i*math.tau/sides)*u+math.sin(i*math.tau/sides)*v))
                for p in (a,b) for i in range(sides)]
    faces = [(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)]
    faces.extend([tuple(reversed(range(sides))),tuple(range(sides,2*sides))])
    obj = mesh(name,vertices,faces,mat,bevel)
    for p in obj.data.polygons:
        p.use_smooth = p.index < sides
    return obj


def tube(name, x0,x1,y,z,outer,inner,mat,steps=32):
    vertices = [(x,y+radius*math.cos(i*math.tau/steps),z+radius*math.sin(i*math.tau/steps))
                for x,radius in [(x0,outer),(x1,outer),(x0,inner),(x1,inner)] for i in range(steps)]
    faces=[]
    for i in range(steps):
        j=(i+1)%steps
        faces.extend([(i,j,j+steps,i+steps),(i+2*steps,i+3*steps,j+3*steps,j+2*steps),
                      (i,i+2*steps,j+2*steps,j),(i+steps,j+steps,j+3*steps,i+3*steps)])
    return mesh(name,vertices,faces,mat,.004)


def wing_panel(name, points, normal, mat, thickness=.07):
    n=Vector(normal)*thickness/2
    vertices=[tuple(Vector(p)+n*sign) for sign in (-1,1) for p in points]
    return mesh(name,vertices,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),
                              (2,3,7,6),(3,0,4,7)],mat,.012)


def build_ship(detail):
    stations=[(-1.6,.44,.33),(-1.1,.59,.4),(.15,.5,.34),(1.65,.23,.19),(3.1,.065,.055)]
    vertices=[(x,w*math.cos(i*math.tau/8),h*math.sin(i*math.tau/8))
              for x,w,h in stations for i in range(8)]
    faces=[tuple(reversed(range(8))),tuple(range(32,40))]
    faces += [(s*8+i,s*8+(i+1)%8,(s+1)*8+(i+1)%8,(s+1)*8+i)
              for s in range(4) for i in range(8)]
    mesh('Hull | angular long prow',vertices,faces,MATS['ivory'],.025)
    canopy=[(-.9,-.33,.29),(-.9,.33,.29),(1.25,.19,.25),(1.25,-.19,.25),
            (-.62,-.285,.79),(-.62,.285,.79),(.77,.17,.62),(.77,-.17,.62)]
    mesh('Cockpit | faceted blue canopy',canopy,[(0,1,5,4),(1,2,6,5),(2,3,7,6),
         (3,0,4,7),(4,5,6,7),(0,3,2,1)],MATS['glass'],.022)
    for i,(a,b) in enumerate([(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]):
        cylinder(f'Canopy frame {i}',canopy[a],canopy[b],.022,MATS['metal'],12,.003)
    for side in (-1,1):
        box(f'Prow orange accent {side}',(1.02,side*.265,.12),(1.24,.027,.055),MATS['orange'],.005)
        if detail:
            wing_panel(f'Layered cheek armor {side}',[(-1.03,side*.53,.2),(-.25,side*.51,.22),
                (.1,side*.46,-.05),(-.86,side*.58,-.08)],(0,side,0),MATS['panel'],.038)
            for i in range(5):
                box(f'Hull side vent {side}:{i}',(-.77+i*.11,side*.515,.13),(.053,.026,.16),MATS['graphite'],.003)
                box(f'Side vent surround {side}:{i}',(-.77+i*.11,side*.543,.13),(.021,.012,.1),MATS['metal'],.002)
    if detail:
        for i in range(4):
            x0,x1=1.35+i*.39,1.35+i*.39+.35
            def prow_point(x,sign):
                u=(x-1.35)/(3.1-1.35)
                return (x,sign*(.193-.132*u),.244-.18*u)
            wing_panel(f'Prow armor segment {i}',[prow_point(x0,-1),prow_point(x1,-1),
                prow_point(x1,1),prow_point(x0,1)],(0,0,1),MATS['ivory'],.012)
            for sign in (-1,1):
                px,py,pz=prow_point(x0+.09,sign)
                cylinder(f'Prow fastener {i}:{sign}',(px,py*.73,pz+.005),(px,py*.73,pz+.021),.013,MATS['metal'],10,.002)
    for side in (-1,1):
        for upper in (-1,1):
            ident=f'{"port" if side<0 else "starboard"}-{ "upper" if upper>0 else "lower"}'
            ry,rz,ty,tz=.53*side,.19*upper,3.0*side,1.02*upper
            normal=Vector((0,-(tz-rz)/(ty-ry),1)).normalized()
            points=[(.65,ry,rz),(-.55,ty,tz),(-1.55,ty,tz),(-1.55,ry,rz)]
            wing_panel('Wing foil | '+ident,points,normal,MATS['ivory'])
            def panel_point(f,offset):
                return tuple(Vector((.65-1.2*f-offset,ry+(ty-ry)*f,rz+(tz-rz)*f))+normal*.052)
            wing_panel('Wing orange stripe | '+ident,[panel_point(.16,.11),panel_point(.96,.11),
                panel_point(.96,.29),panel_point(.16,.29)],normal,MATS['orange'],.009)
            if detail:
                wing_panel('Wing graphite inset | '+ident,[panel_point(.28,.4),panel_point(.84,.4),
                    panel_point(.84,.86),panel_point(.28,1.1)],normal,MATS['graphite'],.012)
                for i in range(4):
                    f=.35+i*.11
                    a,b=panel_point(f,.43),panel_point(f,.75)
                    cylinder(f'Wing radiator rail {ident}:{i}',a,b,.013,MATS['metal'],8,.002)
                for f in (.3,.55,.8):
                    for offset in (.32,.87):
                        p=Vector(panel_point(f,offset))
                        cylinder(f'Foil recessed fastener {ident}:{f}:{offset}',p+normal*.005,p+normal*.023,.017,MATS['metal'],10,.002)
            cylinder('Foil actuator | '+ident,(-1.1,side*.3,upper*.16),(-1.1,side*.9,upper*.49),.074,MATS['graphite'])
            y,z=.89*side,.46*upper
            cylinder('Engine pressure casing | '+ident,(-1.55,y,z),(-.08,y,z),.235,MATS['metal'])
            cylinder('Engine forward collar | '+ident,(-.36,y,z),(-.13,y,z),.253,MATS['graphite'])
            tube('Engine open nozzle | '+ident,-1.84,-1.54,y,z,.269,.175,MATS['metal'])
            tube('Engine throat | '+ident,-1.81,-1.6,y,z,.177,.138,MATS['graphite'])
            cylinder('Engine luminous core | '+ident,(-1.806,y,z),(-1.8,y,z),.137,MATS['blue'],32,0)
            cylinder('Engine white hot center | '+ident,(-1.81,y,z),(-1.806,y,z),.068,MATS['hot'],24,0)
            ENGINE_CENTERS.append(Vector((-1.845,y,z)))
            if detail:
                for i in range(12):
                    theta=i*math.tau/12
                    yy,zz=y+.239*math.cos(theta),z+.239*math.sin(theta)
                    cylinder(f'Engine cooling rib {ident}:{i}',(-1.42,yy,zz),(-.47,yy,zz),.013,MATS['graphite'],8,.002)
                for x in (-1.45,-.48):
                    tube(f'Engine casing band {ident}:{x}',x-.028,x+.028,y,z,.25,.231,MATS['ivory'],24)
                for i in range(12):
                    theta=i*math.tau/12
                    yy,zz=y+.219*math.cos(theta),z+.219*math.sin(theta)
                    cylinder(f'Nozzle flange bolt {ident}:{i}',(-1.854,yy,zz),(-1.838,yy,zz),.014,MATS['panel'],10,.002)
                for i in range(6):
                    theta=i*math.tau/6
                    cylinder(f'Thruster radial stator {ident}:{i}',(-1.83,y+.07*math.cos(theta),z+.07*math.sin(theta)),
                        (-1.83,y+.135*math.cos(theta),z+.135*math.sin(theta)),.012,MATS['graphite'],8,.002)
                route=[(-1.21,y,z+.13),(-.99,y-side*.13,z+.19),(-.78,side*.57,upper*.26),(-.47,side*.48,upper*.23)]
                for i in range(len(route)-1):
                    cylinder(f'Engine feed conduit {ident}:{i}',route[i],route[i+1],.023,MATS['warmmetal'],12,.004)
                cylinder('Foil actuator joint | '+ident,(-1.15,side*.83,upper*.45),(-1.04,side*.83,upper*.45),.12,MATS['metal'],20,.009)
            cylinder('Wingtip boom | '+ident,(-1.97,ty,tz),(.94,ty,tz),.054,MATS['metal'],16)
            cylinder('Wingtip boom collar | '+ident,(-1.6,ty,tz),(-.89,ty,tz),.116,MATS['graphite'])
            tube('Wingtip hollow muzzle | '+ident,.88,1.04,ty,tz,.084,.046,MATS['metal'],16)
            MUZZLE_CENTERS.append(Vector((1.05,ty,tz)))
    if detail:
        box('Dorsal reactor housing',(-1.16,0,.43),(.48,.38,.22),MATS['graphite'],.027)
        for i in range(7):
            box(f'Dorsal radiator vane {i}',(-1.35+i*.057,0,.563),(.021,.3,.025),MATS['metal'],.004)
        cylinder('Dorsal sensor mast',(-1.3,0,.57),(-1.64,0,.86),.025,MATS['metal'],12)
        for side in (-1,1):
            box(f'Aft service plate {side}',(-1.59,side*.23,.14),(.026,.23,.21),MATS['graphite'],.005)
            for i in range(3):
                cylinder(f'Service fastener {side}:{i}',(-1.61,side*.23,.075+i*.063),(-1.63,side*.23,.075+i*.063),.018,MATS['metal'],12,.002)
            box(f'Canopy sill service panel {side}',(-.45,side*.34,.4),(.36,.038,.071),MATS['ivory'],.011)
            cylinder(f'Canopy sill conduit {side}',(-.73,side*.362,.402),(-.08,side*.328,.4),.014,MATS['warmmetal'],10,.003)


def build_interceptor(detail):
    # Compact faceted cockpit and two vertical radiator shields distinguish it
    # from Aster's long prow and four split foils. Its forward axis is -X.
    cylinder('Cockpit | armored faceted capsule',(-.55,0,0),(.47,0,0),.54,MATS['metal'],12,.028)
    tube('Cockpit | dark forward rim',-.68,-.5,0,0,.43,.32,MATS['graphite'],24)
    cylinder('Cockpit | forward blue window',(-.65,0,0),(-.64,0,0),.32,MATS['glass'],24,0)
    for i in range(8):
        theta=i*math.tau/8
        cylinder(f'Cockpit radial frame {i}',(-.674,0,0),(-.674,.32*math.cos(theta),.32*math.sin(theta)),.016,MATS['metal'],8,.002)
    for side in (-1,1):
        cylinder(f'Radiator structural spar {side}',(0,0,0),(0,side*1.19,0),.135,MATS['metal'])
        y=side*1.27
        # Six-sided silhouette from the film reference, with the original
        # authored cell, fastener and conduit detail retained.
        outline=[(-.65,y,1.21),(.65,y,1.21),(1.2,y,0),(.65,y,-1.21),
                 (-.65,y,-1.21),(-1.2,y,0)]
        sides=len(outline)
        vertices=[tuple(Vector(p)+Vector((0,d,0))) for d in (-.045,.045) for p in outline]
        faces=[tuple(reversed(range(sides))),tuple(range(sides,sides*2))]+[
            (i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)]
        mesh(f'Radiator shield | {side}',vertices,faces,MATS['graphite'],.022)
        for i in range(sides):
            cylinder(f'Shield perimeter beam {side}:{i}',outline[i],outline[(i+1)%sides],.044,MATS['metal'],12,.005)
        if detail:
            for face in (-1,1):
                for col in range(3):
                    for row in range(5):
                        box(f'Shield recessed cell {side}:{face}:{col}:{row}',
                            (-.57+col*.39,y+face*.053,-.82+row*.41),(.347,.023,.357),MATS['radiator'],.009)
                for i in range(sides):
                    p=Vector(outline[i])*.91
                    p.y=y+face*.053
                    cylinder(f'Shield rim fastener {side}:{face}:{i}',p,p+Vector((0,face*.017,0)),.019,MATS['warmmetal'],10,.002)
            for z in [-.86,-.56,-.26,.04,.34,.64,.94]:
                cylinder(f'Shield panel seam {side}:{z}',(-.83,y+side*.052,z),(.62,y+side*.052,z),.013,MATS['metal'],8,.002)
            for x in [-.48,-.1,.28]:
                cylinder(f'Shield brace {side}:{x}',(x,y+side*.06,-1.03),(x,y+side*.06,1.02),.014,MATS['metal'],8,.002)
            cylinder(f'Shield upper bus bar {side}',(-.57,y+side*.058,1.17),(.57,y+side*.058,1.17),.029,MATS['metal'],12,.002)
        cylinder(f'Aft engine housing {side}',(.34,side*.24,.14),(.83,side*.24,.14),.16,MATS['graphite'])
        tube(f'Aft open nozzle {side}',.73,.9,side*.24,.14,.17,.117,MATS['metal'],24)
        cylinder(f'Aft blue core {side}',(.89,side*.24,.14),(.896,side*.24,.14),.116,MATS['blue'],24,0)
        ENGINE_CENTERS.append(Vector((.91,side*.24,.14)))
        cylinder(f'Forward blaster barrel {side}',(-.48,side*.22,-.25),(-.95,side*.22,-.25),.051,MATS['metal'],16,.005)
        tube(f'Forward blaster muzzle {side}',-.99,-.92,side*.22,-.25,.064,.035,MATS['graphite'],16)
        if detail:
            cylinder(f'Blaster emitter {side}',(-.994,side*.22,-.25),(-.988,side*.22,-.25),.029,MATS['amber'],16,0)
            route=[(.23,side*.42,.32),(.04,side*.6,.28),(-.2,side*.91,.14),(0,side*1.14,0)]
            for i in range(len(route)-1):
                cylinder(f'Shield coolant conduit {side}:{i}',route[i],route[i+1],.025,MATS['warmmetal'],12,.003)
            for i in range(4):
                box(f'Cockpit shoulder vent {side}:{i}',(.17+i*.065,side*.44,.31),(.025,.046,.09),MATS['graphite'],.004)
        MUZZLE_CENTERS.append(Vector((-1.0,side*.22,-.25)))
    if detail:
        tube('Cockpit armor collar',-.12,.01,0,0,.555,.52,MATS['panel'],24)
        box('Dorsal sensor housing',(.12,0,.55),(.37,.21,.11),MATS['graphite'],.015)
        for i in range(5):
            box(f'Dorsal sensor cooling slot {i}',(-.01+i*.057,0,.614),(.022,.17,.022),MATS['metal'],.004)
        cylinder('Sensor antenna',(.13,0,.59),(.34,0,.89),.021,MATS['metal'],12,.002)


def light(name,position,power,color,size):
    data=bpy.data.lights.new(name,'AREA')
    data.energy,data.color,data.shape,data.size=power,color,'DISK',size
    obj=bpy.data.objects.new(name,data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location=position
    obj.rotation_euler=(-obj.location).to_track_quat('-Z','Y').to_euler()


def run(args):
    global SHIP,MATS,ENGINE_CENTERS,MUZZLE_CENTERS
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    model_name='Aster | original split-wing spacecraft' if args.model=='aster' else 'Vesper | original radiator-shield interceptor'
    stem='aster-ship' if args.model=='aster' else 'vesper-interceptor'
    SHIP=bpy.data.collections.new(model_name)
    scene.collection.children.link(SHIP)
    ENGINE_CENTERS=[]
    MUZZLE_CENTERS=[]
    MATS={name:material(name,*values) for name,values in {
        'ivory':((.72,.75,.78),.52,.3), 'metal':((.32,.39,.46),.8,.27),
        'graphite':((.028,.046,.07),.58,.39), 'orange':((.65,.035,.055),.35,.3),
        'panel':((.17,.23,.29),.67,.32), 'radiator':((.105,.165,.22),.58,.36),
        'warmmetal':((.42,.27,.13),.73,.3), 'amber':((1,.39,.085),0,.28,1.2),
        'glass':((.016,.027,.042),.3,.18),
        'blue':(((.95,.055,.12) if args.model=='aster' else (.08,.75,.38)),.1,.25,3),
        'hot':(((1,.58,.65) if args.model=='aster' else (.55,1,.7)),0,.2,4)}.items()}
    (build_ship if args.model=='aster' else build_interceptor)(not args.blockout)
    data=bpy.data.cameras.new('Rear three-quarter orthographic camera')
    cam=bpy.data.objects.new('Camera',data)
    scene.collection.objects.link(cam)
    cam.location=(-9,-13,10)
    cam.rotation_euler=(Vector((.12,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
    data.type,data.ortho_scale='ORTHO',8.3 if args.model=='aster' else 4.65
    scene.camera=cam
    scene.render.engine='CYCLES'
    prefs=bpy.context.preferences.addons['cycles'].preferences
    if args.backend != 'CPU':
        prefs.compute_device_type=args.backend
        prefs.get_devices()
        for d in prefs.devices: d.use=d.type==args.backend and args.device_name.lower() in d.name.lower()
        selected=[d.name for d in prefs.devices if d.use]
        if not selected: raise RuntimeError('Requested GPU was not enumerated')
        scene.cycles.device='GPU'
    else:
        scene.cycles.device='CPU'
        selected=['CPU']
    scene.cycles.samples=args.samples
    scene.cycles.seed=42
    scene.cycles.use_denoising=True
    scene.render.resolution_x=args.width
    scene.render.resolution_y=round(args.width*.75)
    scene.render.resolution_percentage=100
    scene.render.film_transparent=True
    scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGBA'
    scene.render.image_settings.color_depth='8'
    scene.render.image_settings.compression=100
    scene.view_settings.view_transform='AgX'
    scene.view_settings.exposure=.35
    world=bpy.data.worlds.new('Cool studio environment')
    world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.1,.15,.22,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
    scene.world=world
    light('Neutral key | readable upper panels',(3,-6,9),1000,(1,.94,.86),6)
    light('Blue fill | separated lower foils',(-2,6,3),550,(.65,.8,1),5)
    light('Cool rim | wing edges',(-6,-3,5),850,(.69,.84,1),4)
    light('Warm bounce | aft metal',(1,6,-3),210,(1,.77,.5),4)
    if args.flight:
        render_flight(args,scene,cam,stem,model_name,selected)
        return
    bpy.context.view_layer.update()
    # Keep intentional camera angle; expand only if the chosen silhouette crops.
    for _ in range(3):
        projected=[world_to_camera_view(scene,cam,o.matrix_world@v.co) for o in SHIP.objects for v in o.data.vertices]
        extent=max(max(abs(p.x-.5),abs(p.y-.5)) for p in projected)
        if extent <= .45: break
        data.ortho_scale *= extent/.45
    projected=[world_to_camera_view(scene,cam,o.matrix_world@v.co) for o in SHIP.objects for v in o.data.vertices]
    assert all(.035<p.x<.965 and .035<p.y<.965 for p in projected),'Ship silhouette is cropped'
    args.out.mkdir(parents=True,exist_ok=False)
    image=args.out/(stem+'.png')
    scene.render.filepath=str(image)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.out/(stem+'.blend')),check_existing=False)
    bpy.ops.render.render(write_still=True)
    origins=[world_to_camera_view(scene,cam,p) for p in ENGINE_CENTERS]
    muzzles=[world_to_camera_view(scene,cam,p) for p in MUZZLE_CENTERS]
    axis=1 if args.model=='aster' else -1
    nose,center=[world_to_camera_view(scene,cam,p) for p in [Vector((axis,0,0)),Vector((0,0,0))]]
    manifest={'model':model_name,'blender':bpy.app.version_string,
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'engine':'CYCLES','backend':args.backend,'devices':selected,'samples':args.samples,'seed':42,
        'view_transform':'AgX','exposure':.35,'width':args.width,'height':scene.render.resolution_y,
        'mesh_objects':len(SHIP.objects),'materials':list(MATS),'external_assets':[],
        'engine_uv':[[p.x,p.y] for p in origins],
        'muzzle_uv':[[p.x,p.y] for p in muzzles],
        'nose_angle_degrees':math.degrees(math.atan2(-(nose.y-center.y)*scene.render.resolution_y,(nose.x-center.x)*args.width)),
        'silhouette_bounds_uv':[min(p.x for p in projected),min(p.y for p in projected),max(p.x for p in projected),max(p.y for p in projected)],
        'png_sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'blockout':args.blockout}
    (args.out/'render-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    if args.asset_out:
        args.asset_out.mkdir(parents=True,exist_ok=True)
        for name,target in [(stem+'.png',stem+'.png'),('render-manifest.json',stem+'.json')]:
            pending=args.asset_out/(target+'.tmp')
            pending.write_bytes((args.out/name).read_bytes())
            pending.replace(args.asset_out/target)
    print('SHIP_RENDER_COMPLETE '+json.dumps(manifest))


def render_flight(args,scene,cam,stem,model_name,devices):
    """Render actual rotating geometry into a compact, camera-stable view set."""
    args.out.mkdir(parents=True,exist_ok=False)
    rig=bpy.data.objects.new('Flight attitude | bank and camera-depth pitch',None)
    scene.collection.objects.link(rig)
    for obj in SHIP.objects: obj.parent=rig
    rig.rotation_mode='QUATERNION'
    axis=1 if args.model=='aster' else -1
    cam.location=(0,0,12)
    cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=9.5 if args.model=='aster' else 4.4
    scene.render.fps=12
    scene.frame_start=1
    scene.frame_end=len(VIEW_TIMES)

    def attitude(time):
        bank,pitch=view_pose(args.model,time)
        forward=Vector((math.cos(math.radians(pitch)),0,math.sin(math.radians(pitch))))
        orient=forward.to_track_quat('X','Z')
        if axis<0: orient=orient@Quaternion((0,0,1),math.pi)
        rig.rotation_quaternion=orient@Quaternion((1,0,0),math.radians(axis*bank))
        bpy.context.view_layer.update()
        return bank,pitch

    # A single framing for every view prevents a camera zoom masquerading as
    # a maneuver. Check all attitudes before rendering, then keep it fixed.
    extent=0
    for time in VIEW_TIMES:
        attitude(time)
        for obj in SHIP.objects:
            for vertex in obj.data.vertices:
                p=world_to_camera_view(scene,cam,obj.matrix_world@vertex.co)
                extent=max(extent,abs(p.x-.5),abs(p.y-.5))
    if extent>.445: cam.data.ortho_scale*=extent/.445

    frames=[]
    for index,time in enumerate(VIEW_TIMES):
        scene.frame_set(index+1)
        bank,pitch=attitude(time)
        rig.keyframe_insert(data_path='rotation_quaternion',frame=index+1)
        image=args.out/f'view-{index:03}.png'
        scene.render.filepath=str(image)
        bpy.ops.render.render(write_still=True)
        project=lambda p:world_to_camera_view(scene,cam,rig.matrix_world@p)
        nose,center=project(Vector((axis,0,0))),project(Vector((0,0,0)))
        frames.append({'time':time,'file':image.name,'bank':bank,'pitch':pitch,
            'engine_uv':[[p.x,p.y] for p in map(project,ENGINE_CENTERS)],
            'muzzle_uv':[[p.x,p.y] for p in map(project,MUZZLE_CENTERS)],
            'nose_angle_degrees':math.degrees(math.atan2(-(nose.y-center.y)*scene.render.resolution_y,(nose.x-center.x)*args.width)),
            'png_sha256':hashlib.sha256(image.read_bytes()).hexdigest()})
    scene.frame_set(31)
    scene.render.filepath=str(args.out/'attitude-preview.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(args.out/(stem+'.blend')),check_existing=False)
    manifest={'schema_version':2,'model':model_name,'blender':bpy.app.version_string,
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'flight_source_sha256':hashlib.sha256(Path(__file__).with_name('profile_flight.py').read_bytes()).hexdigest(),
        'engine':'CYCLES','backend':args.backend,'devices':devices,'samples':args.samples,
        'seed':42,'view_transform':'AgX','exposure':.35,'width':args.width,
        'height':scene.render.resolution_y,'mesh_objects':len(SHIP.objects),
        'external_assets':[],'materials':list(MATS),'framing':'fixed orthographic +X heading',
        'ortho_scale':cam.data.ortho_scale,'frames':frames,'blockout':args.blockout}
    (args.out/'render-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print('FLIGHT_RENDER_COMPLETE '+json.dumps({'model':args.model,'frames':len(frames),'devices':devices}))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--asset-out',type=Path)
    parser.add_argument('--width',type=int,default=384)
    parser.add_argument('--samples',type=int,default=48)
    parser.add_argument('--blockout',action='store_true')
    parser.add_argument('--flight',action='store_true',help='Render changing 3D attitudes, for build_flight_atlas.py')
    parser.add_argument('--model',choices=['aster','interceptor'],default='aster')
    parser.add_argument('--backend',choices=['HIP','CUDA','OPTIX','METAL','CPU'],default='HIP')
    parser.add_argument('--device-name',default='6950')
    run(parser.parse_args(sys.argv[sys.argv.index('--')+1:]))
