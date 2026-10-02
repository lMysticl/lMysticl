"""Small SVG compositor: one arrival followed by a continuous two-ship chase.

Eight lossless Blender views replace each full 85-view atlas. Native cubic
motion supplies exact tangent headings without per-frame JavaScript.
"""
import base64
import json
import math
from functools import lru_cache
from pathlib import Path

from profile_battle import (INTRO_END, LOOP, SHOTS, SHOT_DURATION, SHOT_SPEED,
    SAMPLE_TIMES, FIGHTERS, COLORS, pose, view_indices, view_events, stretch,
    intro_pose, path, travel)

ASSETS = Path(__file__).resolve().parents[1]/'assets'/'web'
MODELS = {'aster': ('aster-ship',156), 'interceptor': ('vesper-interceptor',104)}
STILL_TIME = 2.7


def n(value):
    return f'{value:.4f}'.rstrip('0').rstrip('.') if abs(value)>.00005 else '0'


def timing(times):
    return f'keyTimes="{";".join(n(t/LOOP) for t in times)}" begin="{INTRO_END}s" dur="{LOOP}s" repeatCount="indefinite"'


@lru_cache(maxsize=2)
def metadata(model):
    return json.loads((ASSETS/(MODELS[model][0]+'.json')).read_text(encoding='utf-8'))


def ports(model, time, name):
    a, b, u = view_indices(time)
    frames = metadata(model)['frames']
    return [(p[0]*(1-u)+q[0]*u, p[1]*(1-u)+q[1]*u) for p,q in zip(frames[a][name],frames[b][name])]


def point(model, time, uv, mobile=False):
    x, y, scale, rotation, _ = pose(model,time,mobile)
    width = MODELS[model][1]
    sx, sy = (uv[0]-.5)*width, (.5-uv[1])*width*.75
    a = math.radians(rotation)
    return x+scale*(sx*math.cos(a)-sy*math.sin(a)), y+scale*(sx*math.sin(a)+sy*math.cos(a))


def definitions():
    parts = []
    for model,(stem,_) in MODELS.items():
        manifest = metadata(model)
        data = base64.b64encode((ASSETS/(stem+'.webp')).read_bytes()).decode('ascii')
        parts.append(f'<image id="ship-atlas-{model}" width="{manifest["width"]}" height="{manifest["height"]}" href="data:image/webp;base64,{data}"/>')
    return '\n'.join(parts)


def viewbox(model,index):
    return ' '.join(str(v) for v in metadata(model)['frames'][index]['tile'])


def hull(model,animated,time):
    width = MODELS[model][1]
    first,second,fraction = view_indices(time)
    times = view_events()
    parts = []
    for layer,index,opacity in [('base',first,1),('next',second,fraction)]:
        ident = f'spacecraft-window-{model}-{layer}'
        target = f' id="{ident}"' if animated else ''
        parts.append(f'<svg{target} class="spacecraft-view-{layer}" x="{-width/2}" y="{-width*.375}" width="{width}" height="{width*.75}" viewBox="{viewbox(model,index)}" overflow="hidden" opacity="{n(opacity)}"><use href="#ship-atlas-{model}"/></svg>')
        if animated:
            indices = [view_indices(t+.000001)[0 if layer=='base' else 1] for t in times]
            parts.append(f'<animate href="#{ident}" attributeName="viewBox" calcMode="discrete" values="{";".join(viewbox(model,i) for i in indices)}" {timing(times)}/>')
            if layer == 'next':
                keys,values = [0],['0']
                for t in times[1:]:
                    keys.extend((t,t)); values.extend(('1','0'))
                parts.append(f'<animate href="#{ident}" attributeName="opacity" values="{";".join(values)}" {timing(keys)}/>')
    return '\n'.join(parts)


def actor(model,animated,frame_time=None,mobile=False):
    time = STILL_TIME if frame_time is None else max(0,frame_time-INTRO_END) % LOOP
    x,y,scale,rotation,opacity = pose(model,time,mobile)
    arriving = frame_time is not None and frame_time < INTRO_END
    if not animated:
        if arriving:
            x,y,scale,rotation,opacity = intro_pose(model,frame_time,mobile)
        return f'<g class="spacecraft-static" data-ship="{model}" transform="translate({n(x)} {n(y)}) rotate({n(rotation)}) scale({n(scale)})" opacity="{n(opacity)}"><g transform="scale({n(stretch(frame_time) if arriving else 1)} 1)">{hull(model,False,0 if arriving else time)}</g></g>'
    _,_,scale,_,_ = pose(model,0,mobile)
    clock = timing(SAMPLE_TIMES)
    return f'''<g id="spacecraft-{model}" class="spacecraft-flight" data-ship="{model}" opacity="0">
      <set attributeName="opacity" to="1" begin="{INTRO_END}s" fill="freeze"/>
      <g class="spacecraft-position">
        <animateMotion path="{path(model,mobile)}" rotate="auto" calcMode="linear" keyPoints="{";".join(n(travel(model,t)/4) for t in SAMPLE_TIMES)}" {clock}/>
        <g class="spacecraft-depth" transform="scale({n(scale)})">
          <animateTransform attributeName="transform" type="scale" values="{";".join(n(pose(model,t,mobile)[2]) for t in SAMPLE_TIMES)}" {clock}/>
          {hull(model,True,0)}
        </g>
      </g>
    </g>'''


def arrival(model,animated,frame_time=None,mobile=False):
    time = frame_time or 0
    if not animated and (frame_time is None or time >= INTRO_END):
        return ''
    x,y,scale,angle,opacity = intro_pose(model,time,mobile)
    clock = f'begin="0s" dur="{INTRO_END}s" fill="freeze"'
    times = [i*INTRO_END/24 for i in range(25)]
    poses = [intro_pose(model,t,mobile) for t in times]
    parts = [f'<g class="hyperspace-arrival" data-arrival="{model}" opacity="{n(opacity)}">']
    if animated:
        parts.append(f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.13;.999;1" {clock}/>')
    parts.append(f'<g transform="translate({n(x)} {n(y)})">')
    if animated:
        parts.append(f'<animateTransform attributeName="transform" type="translate" values="{";".join(n(p[0])+" "+n(p[1]) for p in poses)}" {clock}/>')
    parts.append(f'<g transform="rotate({n(angle)})">')
    parts.append(f'<g class="hyperspace-wake" opacity="{n(max(0,1-time/INTRO_END)**2)}">')
    if animated:
        parts.append(f'<animate attributeName="opacity" values="1;.45;0" keyTimes="0;.4;1" {clock}/>')
    for y0,length in [(-10,63),(-5,91),(0,120),(5,88),(10,59)]:
        parts.append(f'<path d="M -{length} {y0} L 12 {y0*.18}" stroke="{COLORS[model]}" stroke-width=".9" opacity=".7"/>')
    parts.append('</g>')
    parts.append(f'<g transform="scale({n(scale)})"><g transform="scale({n(stretch(time))} 1)">')
    if animated:
        parts.append(f'<animateTransform attributeName="transform" type="scale" values="{";".join(n(stretch(t))+" 1" for t in times)}" {clock}/>')
    parts.extend((hull(model,False,0),'</g></g></g></g></g>'))
    return '\n'.join(parts)


def shot_vector(owner,launch,mobile=False):
    a = math.radians(pose(owner,launch,mobile)[3])
    return math.cos(a),math.sin(a)


def volley(index,owner,launch,color,animated,frame_time=None,mobile=False):
    ux,uy = shot_vector(owner,launch,mobile)
    speed = SHOT_SPEED*(.70 if mobile else 1)
    muzzles = [point(owner,launch,p,mobile) for p in ports(owner,launch,'muzzle_uv')]
    time = STILL_TIME if frame_time is None else (frame_time-INTRO_END) % LOOP
    progress = max(0,min(SHOT_DURATION,time-launch))
    opacity = max(0,min(1,(time-launch)/.008,(launch+SHOT_DURATION-time)/.04))
    if not animated and (opacity<=0 or (frame_time is not None and frame_time<INTRO_END)):
        return ''
    ident = f'laser-volley-{index}'+('' if animated else '-still')
    parts = [f'<g id="{ident}" class="laser-volley" data-owner="{owner}" data-launch="{n(launch)}" transform="translate({n(ux*speed*progress)} {n(uy*speed*progress)})" opacity="{0 if animated else n(opacity)}">']
    if animated:
        times = [0,launch,launch+.008,launch+SHOT_DURATION-.04,launch+SHOT_DURATION,LOOP]
        positions = [f'{n(ux*speed*max(0,min(SHOT_DURATION,t-launch)))} {n(uy*speed*max(0,min(SHOT_DURATION,t-launch)))}' for t in times]
        parts.append(f'<animateTransform attributeName="transform" type="translate" values="{";".join(positions)}" {timing(times)}/>')
        parts.append(f'<animate attributeName="opacity" values="0;0;1;1;0;0" {timing(times)}/>')
    if owner == 'aster':
        muzzles = muzzles[(index//2)%2::2]
    for px,py in muzzles:
        d = f'M {n(px-ux*14)} {n(py-uy*14)} L {n(px)} {n(py)}'
        parts.append(f'<path class="laser-bolt" d="{d}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/>')
        parts.append(f'<path d="{d}" fill="none" stroke="#FFF9F5" stroke-width=".6" stroke-linecap="round" opacity=".95"/>')
    parts.append('</g>')
    return '\n'.join(parts)


def scene(mobile,animated,frame_time=None):
    bounds = (-407,-93,608,225) if mobile else (-265,-191,468,355)
    rect = ' '.join(f'{name}="{n(value)}"' for name,value in zip(['x','y','width','height'],bounds))
    parts = [f'<defs><clipPath id="spacecraft-frame"><rect {rect}/></clipPath></defs>',
             '<g id="spacecraft-scene" clip-path="url(#spacecraft-frame)">']
    if animated:
        parts.append('<g class="ship-still">')
        parts.extend(actor(model,False,mobile=mobile) for model in FIGHTERS)
        parts.append('</g><g class="motion">')
    if animated:
        parts.extend(arrival(model,True,mobile=mobile) for model in FIGHTERS)
    if not animated and frame_time is not None and frame_time < INTRO_END:
        # The arrival draws the hull too; do not double it in offline previews.
        parts.extend(arrival(model,False,frame_time,mobile) for model in FIGHTERS)
    else:
        parts.extend(actor(model,animated,frame_time,mobile) for model in FIGHTERS)
    parts.extend(volley(i,*shot,animated,frame_time,mobile) for i,shot in enumerate(SHOTS))
    if animated:
        parts.append('</g>')
    parts.append('</g>')
    return '\n'.join(p for p in parts if p)
