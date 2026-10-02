"""Two mirrored six-second stories: arrival, three-second duel, victory, escape.

Native cubic paths and the offline renderer share exact geometry and arc
length. The two small real-view atlases and the accepted planet/sky stay intact.
"""
import bisect
import math
from functools import lru_cache

LOOP = 12
PASS = 6
ARRIVAL_END = .8
BATTLE_END = 3.8
HIT_TIME = 3.8
EXIT_END = 4.75
FIGHTERS = ('aster', 'interceptor')
COLORS = {'aster': '#FF677F', 'interceptor': '#74F8AB'}
SHOT_DURATION = .20
SHOT_SPEED = 900
VIEW_KNOTS = (0,.8,.99,1.18,1.37,1.56,1.75,1.94,2.13,2.50,2.90,3.30,3.8,6)
VIEW_ORDER = (0,0,1,2,3,4,5,6,7,6,5,4,4,4)
LOCAL_TIMES = tuple(sorted({i/15 for i in range(91)} | set(VIEW_KNOTS) |
                          {i/30 for i in range(25)} |
                          {BATTLE_END+i/60 for i in range(58)} |
                          {.065,3.72,3.8,3.9,4.13,4.55,4.75,4.9}))
SAMPLE_TIMES = tuple(sorted({w*PASS+p for w in range(2) for p in LOCAL_TIMES}))


def smooth(u):
    u=max(0,min(1,u))
    return u*u*(3-2*u)


def sign(model):
    return 1 if model == 'aster' else -1


def phase(time):
    t=time % LOOP
    return int(t/PASS),t % PASS


def remap(x,y,mobile):
    return (x*.70-183,y*.55+29) if mobile else (x,y)


def mirror(point,wave,mobile=False):
    if not wave:return point
    cx,cy=remap(-38,-15,mobile)
    return 2*cx-point[0],2*cy-point[1]


def cubic(segment,u):
    a,b,c,d=segment
    p=tuple((1-u)**3*a[i]+3*(1-u)**2*u*b[i]+3*(1-u)*u*u*c[i]+u**3*d[i] for i in (0,1))
    v=tuple(3*(1-u)**2*(b[i]-a[i])+6*(1-u)*u*(c[i]-b[i])+3*u*u*(d[i]-c[i]) for i in (0,1))
    return p,v


@lru_cache(maxsize=4)
def course(model,mobile=False):
    rx,ry=(168,116) if model=='aster' else (186,132)
    theta=-math.pi/2+sign(model)*.24
    k=4/3*math.tan(math.pi/8)
    segments=[]
    for i in range(4):
        a,b=theta+i*math.pi/2,theta+(i+1)*math.pi/2
        p=(-38+rx*math.cos(a),-15+ry*math.sin(a))
        q=(-38+rx*math.cos(b),-15+ry*math.sin(b))
        c=(p[0]-k*rx*math.sin(a),p[1]+k*ry*math.cos(a))
        d=(q[0]+k*rx*math.sin(b),q[1]-k*ry*math.cos(b))
        segments.append(tuple(remap(*v,mobile) for v in (p,c,d,q)))
    distances,parameters=[0],[0]
    previous=segments[0][0]
    for i,segment in enumerate(segments):
        for j in range(1,257):
            p,_=cubic(segment,j/256)
            distances.append(distances[-1]+math.dist(previous,p))
            parameters.append(i+j/256)
            previous=p
    return segments,distances,parameters


def fight_progress(model,p):
    t=max(0,min(3,p-ARRIVAL_END))
    return t/4-sign(model)*.082*smooth(t/1.4)


def course_parameter(model,fraction,mobile=False):
    _,distances,parameters=course(model,mobile)
    distance=max(0,min(1,fraction))*distances[-1]
    i=min(len(distances)-1,max(1,bisect.bisect_right(distances,distance)))
    u=(distance-distances[i-1])/(distances[i]-distances[i-1])
    return parameters[i-1]*(1-u)+parameters[i]*u


def course_point(model,fraction,mobile=False):
    segments,_,_=course(model,mobile)
    parameter=course_parameter(model,fraction,mobile)
    i=min(3,int(parameter))
    p,v=cubic(segments[i],parameter-i)
    return p,math.degrees(math.atan2(v[1],v[0]))


def exit_duration(model):
    return EXIT_END-BATTLE_END if model=='aster' else .33


def entry_remaining(model,p,mobile=False):
    u=max(0,min(1,p/ARRIVAL_END))
    speed=course(model,mobile)[1][-1]/4
    return 120*(.70 if mobile else 1)*(1-u)**3+speed*ARRIVAL_END*(1-u)


def exit_distance(model,p,mobile=False):
    d=max(0,min(exit_duration(model),p-BATTLE_END))
    speed=course(model,mobile)[1][-1]/4
    return speed*d+(220*(.70 if mobile else 1)*(d/exit_duration(model))**3 if model=='aster' else 0)


def location(model,wave,p,mobile=False):
    fraction=fight_progress(model,p)
    (x,y),angle=course_point(model,fraction,mobile)
    if p<ARRIVAL_END:
        distance=-entry_remaining(model,p,mobile)
    elif p>BATTLE_END:
        distance=exit_distance(model,p,mobile)
    else:
        distance=0
    r=math.radians(angle)
    x,y=mirror((x+distance*math.cos(r),y+distance*math.sin(r)),wave,mobile)
    scale=(.48 if model=='aster' else .62)+.045*math.sin(2*math.pi*fraction)
    if p>BATTLE_END:
        scale*=1-(.7 if model=='aster' else .8)*smooth((p-BATTLE_END)/exit_duration(model))
    opacity=smooth(p/.065)
    end=4.55 if model=='aster' else BATTLE_END
    opacity*=1-smooth((p-end)/(.20 if model=='aster' else .33))
    return x,y,scale,angle+wave*180,opacity


def pose(model,time,mobile=False):
    wave,p=phase(time)
    return location(model,wave,p,mobile)


def position(model,time,mobile=False):
    return pose(model,time,mobile)[:3]


def stretch(model,time):
    _,p=phase(time)
    if p<ARRIVAL_END:return 1+2.6*(1-p/ARRIVAL_END)**3
    if model=='aster' and p>BATTLE_END:return 1+2.8*smooth((p-4.05)/.7)
    return 1


def jump_intensity(model,p):
    arrival=max(0,1-p/ARRIVAL_END)**2
    departure=smooth((p-3.9)/.4)*(1-smooth((p-4.55)/.2)) if model=='aster' else 0
    return max(arrival,departure)


def view_indices(time):
    _,p=phase(time)
    i=min(len(VIEW_KNOTS)-2,max(0,bisect.bisect_right(VIEW_KNOTS,p)-1))
    u=(p-VIEW_KNOTS[i])/(VIEW_KNOTS[i+1]-VIEW_KNOTS[i])
    return VIEW_ORDER[i],VIEW_ORDER[i+1],u if VIEW_ORDER[i]!=VIEW_ORDER[i+1] else 0


def view_events():
    return sorted({0,LOOP,*[w*PASS+p for w in range(2) for p in VIEW_KNOTS]})


def split_prefix(segment,u):
    mix=lambda a,b:tuple((1-u)*a[i]+u*b[i] for i in (0,1))
    a,b,c,d=segment
    ab,bc,cd=mix(a,b),mix(b,c),mix(c,d)
    abc,bcd=mix(ab,bc),mix(bc,cd)
    return a,ab,abc,mix(abc,bcd)


@lru_cache(maxsize=8)
def geometry(model,wave,mobile=False):
    segments,distances,_=course(model,mobile)
    p,angle=course_point(model,0,mobile)
    r=math.radians(angle);unit=(math.cos(r),math.sin(r))
    speed=distances[-1]/4
    offset=lambda d:(p[0]-d*unit[0],p[1]-d*unit[1])
    entry=(offset(entry_remaining(model,0,mobile)),offset(2*speed*ARRIVAL_END/3),offset(speed*ARRIVAL_END/3),p)
    parameter=course_parameter(model,fight_progress(model,BATTLE_END),mobile)
    index=min(3,int(parameter))
    middle=[*segments[:index],split_prefix(segments[index],parameter-index)]
    last,angle=course_point(model,fight_progress(model,BATTLE_END),mobile)
    r=math.radians(angle);unit=(math.cos(r),math.sin(r))
    duration=exit_duration(model)
    end=exit_distance(model,BATTLE_END+duration,mobile)
    shift=lambda d:(last[0]+d*unit[0],last[1]+d*unit[1])
    escape=(last,shift(speed*duration/3),shift(2*speed*duration/3),shift(end))
    return [tuple(mirror(p,wave,mobile) for p in s) for s in [entry,*middle,escape]]


def path(model,wave,mobile=False):
    segments=geometry(model,wave,mobile)
    fmt=lambda v:f'{v:.4f}'.rstrip('0').rstrip('.')
    pair=lambda p:' '.join(fmt(v) for v in p)
    return 'M '+pair(segments[0][0])+' '+' '.join('C '+' '.join(pair(p) for p in s[1:]) for s in segments)


def motion_fraction(model,p,mobile=False):
    length=course(model,mobile)[1][-1]
    entry=entry_remaining(model,0,mobile)
    combat=fight_progress(model,BATTLE_END)*length
    escape=exit_distance(model,BATTLE_END+exit_duration(model),mobile)
    distance=(entry-entry_remaining(model,p,mobile) if p<ARRIVAL_END else
              entry+fight_progress(model,p)*length+(exit_distance(model,p,mobile) if p>BATTLE_END else 0))
    return distance/(entry+combat+escape)


SHOTS=tuple((owner,w*PASS+p,'#FF4B62' if owner=='aster' else '#62EE92')
            for w in range(2) for owner,points in
            [('interceptor',(1.00,1.14)),('aster',(2.05,2.19,2.33,2.85,2.99,3.13,3.72))]
            for p in points)
