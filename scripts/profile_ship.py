"""Compact real 3D views and native paths for two mirrored victory stories."""
import base64
import json
import math
from functools import lru_cache
from pathlib import Path
from profile_battle import (LOOP,PASS,HIT_TIME,EXIT_END,IMPACT_DURATION,exit_duration,
    SHOTS,SHOT_DURATION,SHOT_SPEED,FIGHTERS,COLORS,pose,location,
    view_indices,view_events,stretch,path,motion_fraction,jump_intensity,phase,SAMPLE_TIMES)

ASSETS=Path(__file__).resolve().parents[1]/'assets'/'web'
MODELS={'aster':('aster-ship',156),'interceptor':('vesper-interceptor',104)}
STILL_TIME=3.01


def n(value):
    return f'{value:.5f}'.rstrip('0').rstrip('.') if abs(value)>.000005 else '0'


def timing(times):
    return f'keyTimes="{";".join(f"{t/LOOP:.7f}" for t in times)}" begin="0s" dur="{LOOP}s" repeatCount="indefinite"'


@lru_cache(maxsize=2)
def metadata(model):
    return json.loads((ASSETS/(MODELS[model][0]+'.json')).read_text(encoding='utf-8'))


def ports(model,time,name):
    a,b,u=view_indices(time)
    frames=metadata(model)['frames']
    return [(p[0]*(1-u)+q[0]*u,p[1]*(1-u)+q[1]*u) for p,q in zip(frames[a][name],frames[b][name])]


def point(model,time,uv,mobile=False):
    x,y,scale,rotation,_=pose(model,time,mobile)
    width=MODELS[model][1]
    sx,sy=(uv[0]-.5)*width*stretch(model,time),(.5-uv[1])*width*.75
    a=math.radians(rotation)
    return x+scale*(sx*math.cos(a)-sy*math.sin(a)),y+scale*(sx*math.sin(a)+sy*math.cos(a))


def definitions():
    parts=[]
    for model,(stem,_) in MODELS.items():
        manifest=metadata(model)
        data=base64.b64encode((ASSETS/(stem+'.webp')).read_bytes()).decode('ascii')
        parts.append(f'<image id="ship-atlas-{model}" width="{manifest["width"]}" height="{manifest["height"]}" href="data:image/webp;base64,{data}"/>')
    return '\n'.join(parts)


def viewbox(model,index):
    return ' '.join(str(v) for v in metadata(model)['frames'][index]['tile'])


def hull(model,animated,time,wave=0):
    width=MODELS[model][1]
    first,second,fraction=view_indices(time)
    times=view_events()
    parts=[]
    for layer,index,opacity in [('base',first,1),('next',second,fraction)]:
        ident=f'spacecraft-window-{model}-{wave}-{layer}'
        target=f' id="{ident}"' if animated else ''
        parts.append(f'<svg{target} class="spacecraft-view-{layer}" x="{-width/2}" y="{-width*.375}" width="{width}" height="{width*.75}" viewBox="{viewbox(model,index)}" overflow="hidden" opacity="{n(opacity)}"><use href="#ship-atlas-{model}"/></svg>')
        if animated:
            indices=[view_indices(t+.0000001)[0 if layer=='base' else 1] for t in times]
            parts.append(f'<animate href="#{ident}" attributeName="viewBox" calcMode="discrete" values="{";".join(viewbox(model,i) for i in indices)}" {timing(times)}/>')
            if layer=='next':
                keys,values=[0],['0']
                for t in times[1:]:
                    keys.extend((t,t));values.extend((n(view_indices(t-.0000001)[2]),'0'))
                parts.append(f'<animate href="#{ident}" attributeName="opacity" values="{";".join(values)}" {timing(keys)}/>')
    return '\n'.join(parts)


def wake(model,animated,time,times=None):
    _,p=phase(time)
    opacity=jump_intensity(model,p)
    parts=[f'<g class="hyperspace-wake" opacity="{n(opacity)}">']
    if animated:
        values=[jump_intensity(model,phase(t)[1]) for t in times]
        parts.append(f'<animate attributeName="opacity" values="{";".join(n(v) for v in values)}" {timing(times)}/>')
    for y,length in [(-10,63),(-5,92),(0,125),(5,92),(10,63)]:
        parts.append(f'<path d="M -{length} {y} L 6 {y*.15}" fill="none" stroke="{COLORS[model]}" stroke-width=".85" opacity=".6"/>')
    parts.append('<ellipse cx="-8" rx="1.7" ry="11" fill="none" stroke="#ECF6FF" stroke-width="1" opacity=".85"/></g>')
    return '\n'.join(parts)


def actor(model,animated,frame_time=None,mobile=False):
    time=STILL_TIME if frame_time is None else frame_time % LOOP
    x,y,scale,rotation,opacity=pose(model,time,mobile)
    if not animated:
        if opacity<=0:return ''
        return f'<g class="spacecraft-static" data-ship="{model}" transform="translate({n(x)} {n(y)}) rotate({n(rotation)}) scale({n(scale)})" opacity="{n(opacity)}">{wake(model,False,time)}<g transform="scale({n(stretch(model,time))} 1)">{hull(model,False,time)}</g></g>'
    times=SAMPLE_TIMES
    poses=[pose(model,t,mobile) for t in times]
    opacities=[p[4] for p in poses]
    # Disjoint SVG subpaths switch sides while this pair is invisible. Keeping
    # one actor per fighter avoids animating an idle duplicate pair each frame.
    route=path(model,0,mobile)+' '+path(model,1,mobile)
    points=[1 if t==LOOP else (phase(t)[0]+motion_fraction(model,phase(t)[1],mobile))/2 for t in times]
    clock=timing(times)
    visible_until=EXIT_END if model=='aster' else HIT_TIME+exit_duration(model)
    visibility=timing([0,visible_until,PASS,PASS+visible_until,LOOP])
    parts=[f'<g id="spacecraft-{model}" class="spacecraft-flight" data-ship="{model}" data-wave="alternating" opacity="0">',
        f'<animate attributeName="display" calcMode="discrete" values="inline;none;inline;none;inline" {visibility}/>',
        f'<animate attributeName="opacity" values="{";".join(n(v) for v in opacities)}" {clock}/>',
        '<g class="spacecraft-position">',
        f'<animateMotion path="{route}" rotate="auto" calcMode="linear" keyPoints="{";".join(f"{p:.7f}" for p in points)}" {clock}/>',
        f'<g class="spacecraft-depth" transform="scale({n(poses[0][2])})">',
        f'<animateTransform attributeName="transform" type="scale" values="{";".join(n(p[2]) for p in poses)}" {clock}/>',
        wake(model,True,0,times),
        '<g class="spacecraft-stretch">',
        f'<animateTransform attributeName="transform" type="scale" values="{";".join(n(stretch(model,t))+" 1" for t in times)}" {clock}/>',
        hull(model,True,0),'</g></g></g></g>']
    return '\n'.join(parts)


def impact(wave,animated,frame_time=None,mobile=False):
    time=frame_time or 0
    start=wave*PASS+HIT_TIME
    u=max(0,min(1,(time-start)/IMPACT_DURATION))
    opacity=max(0,min(1,(time-start)/.055,(start+IMPACT_DURATION-time)/.30))
    if not animated and opacity<=0:return ''
    x,y,_,_,_=location('interceptor',wave,HIT_TIME,mobile)
    parts=[f'<g class="victory-impact" data-winner="aster" data-defeated="interceptor" data-wave="{wave}" transform="translate({n(x)} {n(y)})" opacity="{0 if animated else n(opacity)}">']
    times=[0,start,start+.055,start+.24,start+IMPACT_DURATION,LOOP]
    if animated:
        parts.append(f'<animate attributeName="opacity" values="0;0;1;1;0;0" {timing(times)}/>')
    parts.append(f'<g class="impact-spread" transform="scale({n(1+1.4*u)})">')
    if animated:
        parts.append(f'<animateTransform attributeName="transform" type="scale" values="1;1;1.08;1.57;2.4;2.4" {timing(times)}/>')
    parts.append('<circle r="4" fill="#FFA449" opacity=".8"/><circle r="1.8" fill="#FFF9E9"/><circle r="7.5" fill="none" stroke="#FFD698" stroke-width=".65" opacity=".7"/>')
    for i in range(6):
        angle=i*60+17
        parts.append(f'<g transform="rotate({angle})"><path d="M 5 -.6 L 8 -1.1 L 7 1 Z" fill="{"#D9E3EE" if i%2 else "#FFD49E"}"/><path d="M 8 0 L 11.5 0" stroke="#FFBB73" stroke-width=".55"/></g>')
    parts.append('</g></g>')
    return '\n'.join(parts)


def shot_vector(owner,launch,mobile=False):
    a=math.radians(pose(owner,launch,mobile)[3])
    return math.cos(a),math.sin(a)


def volley(index,owner,launch,color,animated,frame_time=None,mobile=False):
    ux,uy=shot_vector(owner,launch,mobile)
    speed=SHOT_SPEED*(.70 if mobile else 1)
    muzzles=[point(owner,launch,p,mobile) for p in ports(owner,launch,'muzzle_uv')]
    time=STILL_TIME if frame_time is None else frame_time % LOOP
    progress=max(0,min(SHOT_DURATION,time-launch))
    opacity=max(0,min(1,(time-launch)/.008,(launch+SHOT_DURATION-time)/.04))
    if not animated and opacity<=0:return ''
    ident=f'laser-volley-{index}'+('' if animated else '-still')
    parts=[f'<g id="{ident}" class="laser-volley" data-owner="{owner}" data-launch="{n(launch)}" transform="translate({n(ux*speed*progress)} {n(uy*speed*progress)})" opacity="{0 if animated else n(opacity)}">']
    if animated:
        times=[0,launch,launch+.008,launch+SHOT_DURATION-.04,launch+SHOT_DURATION,LOOP]
        values=[f'{n(ux*speed*max(0,min(SHOT_DURATION,t-launch)))} {n(uy*speed*max(0,min(SHOT_DURATION,t-launch)))}' for t in times]
        parts.append(f'<animateTransform attributeName="transform" type="translate" values="{";".join(values)}" {timing(times)}/>')
        parts.append(f'<animate attributeName="opacity" values="0;0;1;1;0;0" {timing(times)}/>')
    if owner=='aster':
        # The final forward volley uses the wing pair that meets the target.
        pair=1 if phase(launch)[1]>HIT_TIME-.3 else (index//2)%2
        muzzles=muzzles[pair::2]
    for px,py in muzzles:
        d=f'M {n(px-ux*14)} {n(py-uy*14)} L {n(px)} {n(py)}'
        parts.append(f'<path class="laser-bolt" d="{d}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/><path d="{d}" fill="none" stroke="#FFF9F5" stroke-width=".6" stroke-linecap="round" opacity=".95"/>')
    parts.append('</g>')
    return '\n'.join(parts)


def scene(mobile,animated,frame_time=None):
    bounds=(-407,-93,608,225) if mobile else (-265,-191,468,355)
    rect=' '.join(f'{name}="{n(value)}"' for name,value in zip(['x','y','width','height'],bounds))
    parts=[f'<defs><clipPath id="spacecraft-frame"><rect {rect}/></clipPath></defs>',
           '<g id="spacecraft-scene" clip-path="url(#spacecraft-frame)">']
    if animated:
        parts.append('<g class="ship-still">')
        parts.extend(actor(m,False,mobile=mobile) for m in FIGHTERS)
        parts.append('</g><g class="motion">')
        parts.extend(actor(m,True,mobile=mobile) for m in FIGHTERS)
    else:
        parts.extend(actor(m,False,frame_time,mobile) for m in FIGHTERS)
    if animated or frame_time is not None:
        parts.extend(impact(w,animated,frame_time,mobile) for w in range(2))
    parts.extend(volley(i,*shot,animated,frame_time,mobile) for i,shot in enumerate(SHOTS))
    if animated:parts.append('</g>')
    parts.append('</g>')
    return '\n'.join(p for p in parts if p)
