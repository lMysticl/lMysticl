"""Continuous pursuit; native cubic motion and offline sampling share one course."""
import bisect
import math
from functools import lru_cache

LOOP = 48
INTRO_END = 1.05
LAP = 12
FIGHTERS = ('aster', 'interceptor')
COLORS = {'aster': '#FF677F', 'interceptor': '#74F8AB'}
SHOT_DURATION = .20
SHOT_SPEED = 900
SAMPLE_TIMES = tuple(i*.75 for i in range(65))
VIEW_SEQUENCE = (*range(8), *range(6, 0, -1), 0)


def sign(model):
    return 1 if model == 'aster' else -1


def remap(x, y, mobile):
    return (x*.70-183, y*.55+29) if mobile else (x, y)


def cubic(segment, u):
    a, b, c, d = segment
    p = tuple((1-u)**3*a[i]+3*(1-u)**2*u*b[i]+3*(1-u)*u*u*c[i]+u**3*d[i] for i in (0, 1))
    v = tuple(3*(1-u)**2*(b[i]-a[i])+6*(1-u)*u*(c[i]-b[i])+3*u*u*(d[i]-c[i]) for i in (0, 1))
    return p, v


@lru_cache(maxsize=4)
def course(model, mobile=False):
    rx, ry = (168, 116) if model == 'aster' else (186, 132)
    theta = -math.pi/2+sign(model)*.24
    k = 4/3*math.tan(math.pi/8)
    segments = []
    for i in range(4):
        a, b = theta+i*math.pi/2, theta+(i+1)*math.pi/2
        p = (-38+rx*math.cos(a), -15+ry*math.sin(a))
        q = (-38+rx*math.cos(b), -15+ry*math.sin(b))
        c = (p[0]-k*rx*math.sin(a), p[1]+k*ry*math.cos(a))
        d = (q[0]+k*rx*math.sin(b), q[1]-k*ry*math.cos(b))
        segments.append(tuple(remap(*v, mobile) for v in (p, c, d, q)))
    distances, parameters = [0], [0]
    previous = segments[0][0]
    for i, segment in enumerate(segments):
        for j in range(1, 257):
            u = j/256
            p, _ = cubic(segment, u)
            distances.append(distances[-1]+math.dist(previous, p))
            parameters.append(i+u)
            previous = p
    return segments, distances, parameters


def travel(model, time):
    """Four laps; positive speed and matching end position/velocity."""
    return time/LAP+sign(model)*.041*(math.cos(2*math.pi*time/LOOP)-1)


def position_heading(model, time, mobile=False):
    segments, distances, parameters = course(model, mobile)
    distance = (travel(model, time) % 1)*distances[-1]
    i = min(len(distances)-1, max(1, bisect.bisect_right(distances, distance)))
    u = (distance-distances[i-1])/(distances[i]-distances[i-1])
    parameter = parameters[i-1]*(1-u)+parameters[i]*u
    segment = min(3, int(parameter))
    p, v = cubic(segments[segment], parameter-segment)
    return p[0], p[1], math.degrees(math.atan2(v[1], v[0]))


def pose(model, time, mobile=False):
    x, y, angle = position_heading(model, time, mobile)
    scale = (.48 if model == 'aster' else .62)+.045*math.sin(2*math.pi*travel(model, time))
    return x, y, scale, angle, 1


def position(model, time, mobile=False):
    x, y, scale, _, _ = pose(model, time, mobile)
    return x, y, scale


def intro_pose(model, time, mobile=False):
    x, y, scale, angle, _ = pose(model, 0, mobile)
    u = max(0, min(1, time/INTRO_END))
    length = course(model, mobile)[1][-1]
    remaining = 120*(.70 if mobile else 1)*(1-u)**3+length/LAP*INTRO_END*(1-u)
    r = math.radians(angle)
    return x-remaining*math.cos(r), y-remaining*math.sin(r), scale, angle, min(1, u/.13)


def stretch(time):
    return 1+2.6*max(0, 1-time/INTRO_END)**3


def view_indices(time):
    progress = (time % LAP)/LAP*(len(VIEW_SEQUENCE)-1)
    index = int(progress)
    return VIEW_SEQUENCE[index], VIEW_SEQUENCE[index+1], progress-index


def view_events():
    return [i*LAP/(len(VIEW_SEQUENCE)-1) for i in range(4*(len(VIEW_SEQUENCE)-1)+1)]


def path(model, mobile=False):
    segments, _, _ = course(model, mobile)
    fmt = lambda v: f'{v:.4f}'.rstrip('0').rstrip('.')
    pair = lambda p: ' '.join(fmt(v) for v in p)
    return 'M '+pair(segments[0][0])+' '+' '.join('C '+' '.join(pair(p) for p in s[1:]) for _ in range(4) for s in segments)


def shots():
    """Find forward firing opportunities without aiming the hull backwards."""
    result = []
    for center in (1.5, 5, 8.5, 14, 17.5, 21, 25.5, 29, 32.5, 38, 41.5, 45):
        candidates = []
        for j in range(-12, 13):
            t = center+j*.055
            for owner in FIGHTERS:
                enemy = FIGHTERS[1-FIGHTERS.index(owner)]
                x, y, _, angle, _ = pose(owner, t)
                tx, ty, _ = position(enemy, t+.085)
                r = math.radians(angle)
                ahead = (tx-x)*math.cos(r)+(ty-y)*math.sin(r)
                cross = abs(-(tx-x)*math.sin(r)+(ty-y)*math.cos(r))
                if 40 < ahead < 155:
                    candidates.append((cross/ahead+abs(t-center)*.06, owner, t))
        if candidates:
            _, owner, t = min(candidates)
            result.extend((owner, t+i*.14, '#FF4B62' if owner=='aster' else '#62EE92') for i in range(3))
    return tuple(sorted(result, key=lambda shot: shot[1]))


SHOTS = shots()
