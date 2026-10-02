"""Four linked fleet passes, reusing the retained real Blender attitude atlas.

The original profile_flight module remains the immutable atlas pose producer.
This consumer maps each pass onto those views and carries the same ships through
short hyperspace handoffs. All clocks divide the existing 48-second sky loop.
"""
import math
from functools import lru_cache
from profile_flight import curve, view_indices as atlas_indices

LOOP = 48
INTRO_OFFSET = 4
PASS = 12
ANGLES = (0, 180, -12, 168)
FIGHTERS = ('aster', 'interceptor')
CRUISERS = ('aurora', 'vanguard')
FLEET = (*CRUISERS, *FIGHTERS)
COLORS = {'aster':'#FF677F', 'interceptor':'#74F8AB',
          'aurora':'#8FCBFF', 'vanguard':'#ABB8FF'}
SHOT_DURATION = .24
SHOT_SPEED = 950
SHOTS = tuple((owner, wave*PASS+p, '#FF4B62' if owner=='aster' else '#62EE92')
              for wave in range(4) for owner, phases in
              [('aster',(3.35,3.55,3.75)),('interceptor',(3.42,3.62,3.82))]
              for p in phases)
SAMPLE_TIMES = tuple(sorted({i/12 for i in range(48*12+1)} |
                           {w*PASS+p for w in range(4) for p in
                            (0,.08,.16,.24,.4,.65,.8,10.2,10.6,10.85,11.1,11.4,11.5,11.7,11.9)}))


def smooth(u):
    u = max(0, min(1, u))
    return u*u*(3-2*u)


def phase(time):
    t = time % LOOP
    return int(t/PASS), t % PASS


def source_time(time):
    """Fast jump braking, steady combat, then increasing escape velocity."""
    _, p = phase(time)
    if p < .8:
        u = p/.8
        return 3.4 + .7*(1-(1-u)**3)
    if p < 10.2:
        return 4.1+(p-.8)*4.6/9.4
    u = min(1, (p-10.2)/1.2)
    # The starting derivative agrees with the steady flight segment.
    return 8.7 + .75*(.783*u + .217*u*u*u)


def remap(x, y, mobile):
    return (x*.8-194, y*.68+39) if mobile else (x, y)


def location(model, wave, p, mobile=False):
    if model in FIGHTERS:
        x, y, depth = curve(model, source_time(wave*PASS+min(11.4,p)))
        x, y = x*.55, y*.28
        scale = 600/(600-depth)
    else:
        side = 1 if model=='aurora' else -1
        # Capital ships move in the distant plane, with a brief escape burn.
        travel = p*3 + 155*smooth((p-10.2)/1.2)
        x = side*(-115+travel)
        y = -5 if model=='aurora' else -29
        scale = .67 - .11*smooth((p-10.2)/1.2)
    angle=math.radians(ANGLES[wave % 4])
    x,y = x*math.cos(angle)-y*math.sin(angle)-30, x*math.sin(angle)+y*math.cos(angle)-125
    x,y = remap(x,y,mobile)
    return x,y,scale


def position(model,time,mobile=False):
    wave,p=phase(time)
    return location(model,wave,p,mobile)


def pose(model,time,mobile=False):
    wave,p=phase(time)
    x,y,scale=location(model,wave,p,mobile)
    a,b=location(model,wave,max(0,p-.002),mobile),location(model,wave,min(11.399,p+.002),mobile)
    if p >=11.399: a,b=location(model,wave,11.39,mobile),location(model,wave,11.399,mobile)
    angle=math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]))
    opacity=smooth(p/.16)*(1-smooth((p-11.10)/.30))
    if model in CRUISERS: opacity *= .64
    return x,y,scale,angle,opacity


def stretch(time):
    _,p=phase(time)
    return 1+2.8*(1-smooth(p/.42))+3.6*smooth((p-10.85)/.55)


def view_indices(time):
    return atlas_indices(source_time(time))


@lru_cache(maxsize=1)
def view_events():
    from profile_flight import VIEW_TIMES
    events={0,LOOP}
    for wave in range(4):
        events.update((wave*PASS,wave*PASS+11.4,(wave+1)*PASS))
        for source in VIEW_TIMES:
            if not 3.4 < source < 9.45: continue
            lo,hi=0,11.4
            for _ in range(40):
                mid=(lo+hi)/2
                if source_time(mid)<source:lo=mid
                else:hi=mid
            events.add(wave*PASS+(lo+hi)/2)
    return sorted(events)


def jump_intensity(time):
    _,p=phase(time)
    return max(1-smooth(p/.65), smooth((p-10.6)/.5)*(1-smooth((p-11.4)/.6)))


def transfer(model,wave,u,mobile=False):
    """A visible light pulse joins this exit to that craft's next entrance."""
    a=location(model,wave,11.4,mobile)
    b=location(model,(wave+1)%4,0,mobile)
    # Arc above the fleet avoids the Earth and the professional copy.
    control_y=min(a[1],b[1])-(18 if mobile else 25)
    x=(1-u)*a[0]+u*b[0]
    y=(1-u)**2*a[1]+2*(1-u)*u*control_y+u*u*b[1]
    return x,y
