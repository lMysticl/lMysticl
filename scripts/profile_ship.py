"""Native SVG compositor for the shared cinematic 3D flight choreography.

Two compact atlases contain actual Blender views. Continuous native transforms
move the hulls while an opaque base view and a fading next view interpolate
attitude. Laser impulses leave the current cannon and keep their launch vector.
The offline movie samples these same tracks and views; no runtime JavaScript.
"""
import base64
import json
import math
from functools import lru_cache
from pathlib import Path

from profile_flight import (INTRO_OFFSET, LOOP, SHOTS, SHOT_DURATION, SHOT_SPEED,
                            VIEW_TIMES, pose, position, view_indices)

ASSETS=Path(__file__).resolve().parents[1]/'assets'/'spacecraft-3d'
MODELS={'aster':('aster-ship',156),'interceptor':('vesper-interceptor',104)}
STILL_TIME=5.30


def n(value):
    return f'{value:.3f}'.rstrip('0').rstrip('.') if abs(value)>.0005 else '0'


def key(time):
    return f'{time/LOOP:.7f}'.rstrip('0').rstrip('.') or '0'


def timing(times):
    return f'keyTimes="{";".join(key(t) for t in times)}" begin="-{INTRO_OFFSET}s" dur="{LOOP}s" repeatCount="indefinite"'


@lru_cache(maxsize=2)
def metadata(model):
    return json.loads((ASSETS/(MODELS[model][0]+'.json')).read_text(encoding='utf-8'))


def ports(model,time,name):
    a,b,u=view_indices(time)
    frames=metadata(model)['frames']
    return [(p[0]*(1-u)+q[0]*u,p[1]*(1-u)+q[1]*u)
            for p,q in zip(frames[a][name],frames[b][name])]


def point(model,time,uv,mobile=False):
    x,y,scale,rotation,_=pose(model,time,mobile)
    width=MODELS[model][1]
    sx,sy=(uv[0]-.5)*width,(.5-uv[1])*width*.75
    angle=math.radians(rotation)
    return x+scale*(sx*math.cos(angle)-sy*math.sin(angle)),y+scale*(sx*math.sin(angle)+sy*math.cos(angle))


def definitions():
    parts=[]
    for model,(stem,_) in MODELS.items():
        manifest=metadata(model)
        data=base64.b64encode((ASSETS/(stem+'.png')).read_bytes()).decode('ascii')
        parts.append(f'<image id="ship-atlas-{model}" width="{manifest["width"]}" height="{manifest["height"]}" href="data:image/png;base64,{data}"/>')
    return '\n'.join(parts)


def viewbox(model,index):
    return ' '.join(str(v) for v in metadata(model)['frames'][index]['tile'])


def hull(model,animated,time):
    width=MODELS[model][1]
    first,second,fraction=view_indices(time)
    times=[0,*VIEW_TIMES,LOOP]
    indices=[0,*range(len(VIEW_TIMES)),len(VIEW_TIMES)-1]
    parts=[]
    for layer,index,opacity in [('base',first,1),('next',second,fraction)]:
        ident=f'spacecraft-window-{model}-{layer}'
        target=f' id="{ident}"' if animated else ''
        parts.append(f'<svg{target} class="spacecraft-view-{layer}" x="{-width/2}" y="{-width*.375}" width="{width}" height="{width*.75}" viewBox="{viewbox(model,index)}" overflow="hidden" opacity="{n(opacity)}"><use href="#ship-atlas-{model}"/></svg>')
        if animated:
            frame_indices=[min(i+(layer=='next'),len(VIEW_TIMES)-1) for i in indices]
            # A sibling animation targets the nested viewport explicitly.
            # This keeps attitude on the same parent SMIL clock as flight;
            # an animation inside the viewport would own a separate timeline.
            parts.append(f'<animate href="#{ident}" attributeName="viewBox" calcMode="discrete" values="{";".join(viewbox(model,i) for i in frame_indices)}" {timing(times)}/>')
            if layer=='next':
                # At each tile boundary the base becomes the previous next
                # frame. The next layer resets to transparent without a
                # silhouette pop or the alpha loss of a two-sided dissolve.
                blend_times=[0,VIEW_TIMES[0]]
                values=['0','0']
                for t in VIEW_TIMES[1:]:
                    # Equal keyTimes make an instantaneous opacity reset on
                    # the very same boundary as the discrete view change.
                    # A tiny finite reset interval would expose the previous
                    # view at an exactly sought frame boundary.
                    blend_times.extend([t,t])
                    values.extend(['1','0'])
                blend_times.append(LOOP)
                values.append('0')
                parts.append(f'<animate href="#{ident}" attributeName="opacity" values="{";".join(values)}" {timing(blend_times)}/>')
    return '\n'.join(parts)


def actor(model,animated,frame_time=None,mobile=False):
    time=STILL_TIME if frame_time is None and not animated else ((frame_time or 0)+INTRO_OFFSET)%LOOP
    x,y,scale,rotation,opacity=pose(model,time,mobile)
    if not animated:
        if frame_time is None: opacity=1
        if opacity<=0: return ''
        return f'<g class="spacecraft-static" data-ship="{model}" transform="translate({n(x)} {n(y)}) rotate({n(rotation)}) scale({n(scale)})" opacity="{n(opacity)}">{hull(model,False,time)}</g>'
    times=[0,*VIEW_TIMES,10.2,12,48]
    poses=[pose(model,t,mobile) for t in times]
    rotations=[]
    for p in poses:
        angle=p[3]
        if rotations: angle=rotations[-1]+(angle-rotations[-1]+180)%360-180
        rotations.append(angle)
    clock=timing(times)
    positions=';'.join(f'{n(p[0])} {n(p[1])}' for p in poses)
    return f'''<g id="spacecraft-{model}" class="spacecraft-flight" data-ship="{model}" opacity="0">
      <animate attributeName="opacity" values="{';'.join(n(p[4]) for p in poses)}" {clock}/>
      <g class="spacecraft-position" transform="translate({n(x)} {n(y)})">
        <animateTransform attributeName="transform" type="translate" values="{positions}" {clock}/>
        <g class="spacecraft-heading" transform="rotate({n(rotation)})">
          <animateTransform attributeName="transform" type="rotate" values="{';'.join(n(a) for a in rotations)}" {clock}/>
          <g class="spacecraft-depth" transform="scale({n(scale)})">
            <animateTransform attributeName="transform" type="scale" values="{';'.join(n(p[2]) for p in poses)}" {clock}/>
            {hull(model,True,time)}
          </g>
        </g>
      </g>
    </g>'''


def shot_vector(owner,launch,mobile=False):
    angle=math.radians(pose(owner,launch,mobile)[3])
    return math.cos(angle),math.sin(angle)


def volley(index,owner,launch,color,animated,frame_time=None,mobile=False):
    ux,uy=shot_vector(owner,launch,mobile)
    speed=SHOT_SPEED*(.65 if mobile else 1)
    distance=speed*SHOT_DURATION
    muzzles=[point(owner,launch,p,mobile) for p in ports(owner,launch,'muzzle_uv')]
    time=STILL_TIME if frame_time is None else (frame_time+INTRO_OFFSET)%LOOP
    progress=max(0,min(1,(time-launch)/SHOT_DURATION))
    opacity=max(0,min(1,(time-launch)/.008,(launch+SHOT_DURATION-time)/.04))
    if not animated and opacity<=0: return ''
    ident=f'laser-volley-{index}'+('' if animated else '-still')
    parts=[f'<g id="{ident}" class="laser-volley" data-owner="{owner}" data-launch="{launch}" transform="translate({n(ux*distance*progress)} {n(uy*distance*progress)})" opacity="{0 if animated else n(opacity)}">']
    if animated:
        times=[0,launch,launch+.008,launch+SHOT_DURATION-.04,launch+SHOT_DURATION,48]
        positions=[f'{n(ux*speed*max(0,min(SHOT_DURATION,t-launch)))} {n(uy*speed*max(0,min(SHOT_DURATION,t-launch)))}' for t in times]
        parts.append(f'<animateTransform attributeName="transform" type="translate" values="{";".join(positions)}" {timing(times)}/>')
        parts.append(f'<animate attributeName="opacity" values="0;0;1;1;0;0" {timing(times)}/>')
    # Alternating wingtip cannon pairs make compact, readable film-like bursts.
    if owner=='aster': muzzles=muzzles[(index//2)%2::2]
    for px,py in muzzles:
        d=f'M {n(px-ux*14)} {n(py-uy*14)} L {n(px)} {n(py)}'
        parts.append(f'<path class="laser-bolt" d="{d}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
        parts.append(f'<path d="{d}" fill="none" stroke="#FFF9F5" stroke-width=".65" stroke-linecap="round" opacity=".95"/>')
    parts.append('</g>')
    return '\n'.join(parts)


def scene(mobile,animated,frame_time=None):
    bounds=(-407,-93,608,225) if mobile else (-265,-191,468,355)
    rect=' '.join(f'{name}="{n(value)}"' for name,value in zip(['x','y','width','height'],bounds))
    parts=[f'<defs><clipPath id="spacecraft-frame"><rect {rect}/></clipPath></defs>',
           '<g id="spacecraft-scene" clip-path="url(#spacecraft-frame)">']
    if animated:
        parts.append('<g class="ship-still">')
        parts.extend(actor(model,False,mobile=mobile) for model in MODELS)
        parts.extend(volley(i,*shot,False,mobile=mobile) for i,shot in enumerate(SHOTS))
        parts.append('</g><g class="motion">')
    parts.extend(actor(model,animated,frame_time,mobile) for model in MODELS)
    parts.extend(volley(i,*shot,animated,frame_time,mobile) for i,shot in enumerate(SHOTS))
    if animated: parts.append('</g>')
    parts.append('</g>')
    return '\n'.join(p for p in parts if p)
