"""Canonical two-ship flyby and cannon-bound laser volleys for native SVG.

Rendered PNGs contain original 3D geometry. SVG moves their single shared image
definitions, tiny engine plumes and four volley groups; no runtime JavaScript.
The preview exporter samples these same poses and firing schedules.
"""
import base64
import json
import math
from functools import lru_cache
from pathlib import Path

ASSETS=Path(__file__).resolve().parents[1]/'assets'/'spacecraft-3d'
LOOP=48
INTRO_OFFSET=4
MODELS={'aster':('aster-ship',140),'interceptor':('vesper-interceptor',100)}
KEYS={
 'aster':[(0,-285,-145,.7),(3,-255,-133,.7),(5.5,-150,-120,.8),
          (8,-78,-140,.88),(9.7,-20,-15,.88),(11.2,95,80,1),
          (13.5,270,155,.94),(15,350,170,.9),(48,350,170,.9)],
 'interceptor':[(0,275,-172,.6),(3,238,-155,.65),(5.5,148,-149,.76),
                (8,107,-139,.81),(9.8,170,-170,.78),(11.7,260,-237,.65),
                (13,320,-260,.6),(48,320,-260,.6)],
}
SHOTS=(('aster',5.8,'#70E3FF'),('interceptor',6.2,'#FFD29A'),
       ('aster',7.0,'#70E3FF'),('interceptor',7.3,'#FFD29A'))
SHOT_DURATION=.95


def n(value):
    return f'{value:.3f}'.rstrip('0').rstrip('.') if abs(value)>.0005 else '0'


@lru_cache(maxsize=2)
def metadata(model):
    stem,_=MODELS[model]
    return json.loads((ASSETS/(stem+'.json')).read_text(encoding='utf-8'))


def key(t):
    return f'{t/LOOP:.6f}'.rstrip('0').rstrip('.') or '0'


def position(model,time,mobile=False):
    """Cubic interpolation through the authored approach, duel and exit points."""
    keys=KEYS[model]
    t=max(0,min(LOOP,time))
    i=next((i for i in range(len(keys)-1) if keys[i][0]<=t<=keys[i+1][0]),len(keys)-2)
    a,b=keys[i],keys[i+1]
    before,after=keys[max(0,i-1)],keys[min(len(keys)-1,i+2)]
    u=(t-a[0])/(b[0]-a[0])
    h00,h10,h01,h11=2*u**3-3*u**2+1,u**3-2*u**2+u,-2*u**3+3*u**2,u**3-u**2
    result=[]
    for dim in (1,2,3):
        m0=(b[dim]-before[dim])/(b[0]-before[0])
        m1=(after[dim]-a[dim])/(after[0]-a[0])
        result.append(h00*a[dim]+h10*(b[0]-a[0])*m0+h01*b[dim]+h11*(b[0]-a[0])*m1)
    if mobile:
        # The mobile heading occupies the upper half of the card. Stage the
        # duel left of Earth, below both copy lines, with both hulls visible.
        result[0]=result[0]*.65-210
        result[1]+=68
    return tuple(result)


def aim(model,time,mobile=False):
    other='interceptor' if model=='aster' else 'aster'
    x,y,_=position(model,time,mobile)
    tx,ty,_=position(other,time,mobile)
    return math.degrees(math.atan2(ty-y,tx-x))


def pose(model,time,mobile=False):
    t=time%LOOP
    x,y,scale=position(model,t,mobile)
    end=15 if model=='aster' else 13
    opacity=max(0,min(1,(t-3)/.4,(end-t)/.4))
    a,b=position(model,max(0,t-.03),mobile),position(model,min(47.99,t+.03),mobile)
    heading=math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]))
    if 4.9<=t<=7.8:
        heading=aim(model,t,mobile)
    elif 7.8<t<9.8:
        start=aim(model,7.8,mobile)
        pa,pb=position(model,9.77,mobile),position(model,9.83,mobile)
        finish=math.degrees(math.atan2(pb[1]-pa[1],pb[0]-pa[0]))
        delta=(finish-start+180)%360-180
        u=(t-7.8)/2
        heading=start+delta*u*u*(3-2*u)
    rotation=heading-metadata(model)['nose_angle_degrees']
    return x,y,scale,rotation,opacity


def point(model,time,uv,mobile=False):
    x,y,scale,rotation,_=pose(model,time,mobile)
    _,width=MODELS[model]
    sx,sy=(uv[0]-.5)*width,(.5-uv[1])*width*.75
    angle=math.radians(rotation)
    return (x+scale*(sx*math.cos(angle)-sy*math.sin(angle)),
            y+scale*(sx*math.sin(angle)+sy*math.cos(angle)))


def definitions():
    parts=['<linearGradient id="ship-exhaust"><stop stop-color="#B4F4FF" stop-opacity=".85"/>'
           '<stop offset=".2" stop-color="#45C4FF" stop-opacity=".48"/>'
           '<stop offset="1" stop-color="#2875CC" stop-opacity="0"/></linearGradient>']
    for model,(stem,width) in MODELS.items():
        data=base64.b64encode((ASSETS/(stem+'.png')).read_bytes()).decode('ascii')
        parts.append(f'<image id="ship-image-{model}" x="{-width/2}" y="{-width*.375}" '
                     f'width="{width}" height="{width*.75}" href="data:image/png;base64,{data}"/>')
        parts.append(f'<g id="ship-model-{model}">')
        manifest=metadata(model)
        aft_angle=manifest['nose_angle_degrees']+180
        for u,v in manifest['engine_uv']:
            px,py=(u-.5)*width,(.5-v)*width*.75
            parts.append(f'<path transform="translate({n(px)} {n(py)}) rotate({n(aft_angle)})" '
                         'd="M 0 -1.35 Q 9 -2 25 0 Q 9 2 0 1.35 Z" fill="url(#ship-exhaust)" opacity=".75"/>')
        parts.append(f'<use href="#ship-image-{model}"/></g>')
    return '\n'.join(parts)


def actor(model,animated,frame_time=None,mobile=False):
    time=6.5 if frame_time is None and not animated else ((frame_time or 0)+INTRO_OFFSET)%LOOP
    x,y,scale,rotation,opacity=pose(model,time,mobile)
    if not animated:
        if frame_time is None: opacity=1
        if opacity<=0: return ''
        return f'<g class="spacecraft-static" data-ship="{model}" transform="translate({n(x)} {n(y)}) rotate({n(rotation)}) scale({n(scale)})" opacity="{n(opacity)}"><use href="#ship-model-{model}"/></g>'
    times=sorted(set([0,3,13,15,48]+[3+i*.125 for i in range(97)]))
    poses=[pose(model,t,mobile) for t in times]
    rotations=[]
    for p in poses:
        angle=p[3]
        if rotations: angle=rotations[-1]+(angle-rotations[-1]+180)%360-180
        rotations.append(angle)
    timing=f'keyTimes="{";".join(key(t) for t in times)}" begin="-4s" dur="48s" repeatCount="indefinite"'
    positions=';'.join(f'{n(p[0])} {n(p[1])}' for p in poses)
    return f'''<g id="spacecraft-{model}" class="spacecraft-flight" data-ship="{model}" opacity="0">
      <animate attributeName="opacity" values="{';'.join(n(p[4]) for p in poses)}" {timing}/>
      <g class="spacecraft-position" transform="translate({n(x)} {n(y)})">
        <animateTransform attributeName="transform" type="translate" values="{positions}" {timing}/>
        <g class="spacecraft-bank" transform="rotate({n(rotation)})">
          <animateTransform attributeName="transform" type="rotate" values="{';'.join(n(a) for a in rotations)}" {timing}/>
          <g class="spacecraft-depth" transform="scale({n(scale)})">
            <animateTransform attributeName="transform" type="scale" values="{';'.join(n(p[2]) for p in poses)}" {timing}/>
            <use href="#ship-model-{model}"/>
          </g>
        </g>
      </g>
    </g>'''


def volley(index,owner,launch,color,animated,frame_time=None,mobile=False):
    other='interceptor' if owner=='aster' else 'aster'
    x,y,_=position(owner,launch,mobile)
    tx,ty,_=position(other,launch+.4,mobile)
    length=math.hypot(tx-x,ty-y)
    ux,uy=(tx-x)/length,(ty-y)/length
    distance=length*.86
    ports=[point(owner,launch,p,mobile) for p in metadata(owner)['muzzle_uv']]
    time=6.5 if frame_time is None else (frame_time+INTRO_OFFSET)%LOOP
    progress=max(0,min(1,(time-launch)/SHOT_DURATION))
    opacity=max(0,min(1,(time-launch)/.07,(launch+SHOT_DURATION-time)/.1))
    if not animated and opacity<=0: return ''
    ident=f'laser-volley-{index}'+('' if animated else '-still')
    parts=[f'<g id="{ident}" class="laser-volley" data-owner="{owner}" data-launch="{launch}" '
           f'transform="translate({n(ux*distance*progress)} {n(uy*distance*progress)})" opacity="{0 if animated else n(opacity)}">']
    if animated:
        timing='begin="-4s" dur="48s" repeatCount="indefinite"'
        keys=[0,launch,launch+.07,launch+SHOT_DURATION-.1,launch+SHOT_DURATION,48]
        positions=['0 0','0 0',f'{n(ux*distance*.07/SHOT_DURATION)} {n(uy*distance*.07/SHOT_DURATION)}',
                   f'{n(ux*distance*(SHOT_DURATION-.1)/SHOT_DURATION)} {n(uy*distance*(SHOT_DURATION-.1)/SHOT_DURATION)}',
                   f'{n(ux*distance)} {n(uy*distance)}',f'{n(ux*distance)} {n(uy*distance)}']
        key_times=';'.join(key(t) for t in keys)
        parts.append(f'<animateTransform attributeName="transform" type="translate" values="{";".join(positions)}" keyTimes="{key_times}" {timing}/>')
        parts.append(f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{key_times}" {timing}/>')
    for px,py in ports:
        d=f'M {n(px-ux*17)} {n(py-uy*17)} L {n(px)} {n(py)}'
        parts.append(f'<path class="laser-bolt" d="{d}" fill="none" stroke="{color}" stroke-width="2.4" stroke-linecap="round"/>')
        parts.append(f'<path d="{d}" fill="none" stroke="#F1FBFF" stroke-width=".7" stroke-linecap="round" opacity=".9"/>')
    parts.append('</g>')
    return '\n'.join(parts)


def scene(mobile,animated,frame_time=None):
    # This local clip maps to the existing sky region after the artwork's
    # desktop/mobile placement, keeping both ships and shots clear of copy.
    bounds=(-407,-93,608,225) if mobile else (-265,-191,468,355)
    rect=' '.join(f'{key}="{n(value)}"' for key,value in zip(['x','y','width','height'],bounds))
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
