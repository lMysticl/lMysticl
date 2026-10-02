"""Camera-space choreography shared by Blender and the GitHub SVG compositor.

Screen tracks are continuous cubic Hermite curves. The third coordinate is
camera depth; a fixed 600-unit focal distance determines apparent size. Hull
heading follows the projected velocity, never the opponent. Bank anticipates
curvature and depth pitch uses the reconstructed world-space velocity.
"""
import math

LOOP = 48
INTRO_OFFSET = 4
VIEW_FPS = 12
VIEW_TIMES = tuple(3 + i / VIEW_FPS for i in range(85))
KEYS = {
    'aster': ((3, -345, -149, -140), (5.8, -65, -128, -170),
              (7.5, 80, -21, -350), (9.3, 207, 100, -1050),
              (12, 335, 147, -2350)),
    'interceptor': ((3, 295, -154, -290), (5.8, 50, -136, -140),
                    (7, -71, -168, -330), (8.5, -210, -173, -890),
                    (12, -340, -183, -2600)),
}
SHOTS = (('aster', 5.10, '#FF4B62'), ('interceptor', 5.18, '#62EE92'),
         ('aster', 5.25, '#FF4B62'), ('interceptor', 5.33, '#62EE92'),
         ('aster', 5.40, '#FF4B62'), ('interceptor', 5.48, '#62EE92'))
SHOT_DURATION = .24
SHOT_SPEED = 1180


def curve(model, time):
    keys = KEYS[model]
    t = max(keys[0][0], min(keys[-1][0], time))
    i = next((i for i in range(len(keys)-1)
              if keys[i][0] <= t <= keys[i+1][0]), len(keys)-2)
    a, b = keys[i], keys[i+1]
    before, after = keys[max(0, i-1)], keys[min(len(keys)-1, i+2)]
    dt = b[0] - a[0]
    u = (t-a[0]) / dt
    result = []
    for dimension in (1, 2, 3):
        m0 = (b[dimension]-before[dimension])/(b[0]-before[0])
        m1 = (after[dimension]-a[dimension])/(after[0]-a[0])
        result.append((2*u**3-3*u**2+1)*a[dimension]
                      + (u**3-2*u**2+u)*dt*m0
                      + (-2*u**3+3*u**2)*b[dimension]
                      + (u**3-u**2)*dt*m1)
    return tuple(result)


def position(model, time, mobile=False):
    x, y, depth = curve(model, time)
    if mobile:
        # Keep the entire duel below the two description lines and left of
        # the central Earth in the accepted 620 x 580 mobile composition.
        x = x*.65 - 210
        y = y*.5 + 35
    return x, y, 600/(600-depth)


def velocity(model, time, mobile=False):
    a, b = position(model, time-.005, mobile), position(model, time+.005, mobile)
    return (b[0]-a[0])/.01, (b[1]-a[1])/.01


def heading(model, time, mobile=False):
    vx, vy = velocity(model, time, mobile)
    return math.degrees(math.atan2(vy, vx))


def view_pose(model, time):
    """True 3D roll and pitch, with heading normalized to the atlas's +X axis."""
    t = max(3.02, min(11.98, time))
    a, b = curve(model, t-.01), curve(model, t+.01)
    sa, sb = 600/(600-a[2]), 600/(600-b[2])
    vx, vy = (b[0]/sb-a[0]/sa)/.02, (b[1]/sb-a[1]/sa)/.02
    vz = (b[2]-a[2])/.02
    pitch = math.degrees(math.atan2(vz, math.hypot(vx, vy)))
    turn = (heading(model, t+.22)-heading(model, t-.22)+180) % 360 - 180
    bank = 25 + max(-46, min(46, turn*2.5))
    return bank, pitch


def pose(model, time, mobile=False):
    t = time % LOOP
    x, y, scale = position(model, t, mobile)
    opacity = max(0, min(1, (t-3)/.45, (10.2-t)/.45))
    angle = heading(model, max(3.02, min(11.98, t)), mobile)
    return x, y, scale, angle, opacity


def view_indices(time):
    t = max(VIEW_TIMES[0], min(VIEW_TIMES[-1], time))
    index = min(len(VIEW_TIMES)-2, int((t-VIEW_TIMES[0])*VIEW_FPS+1e-8))
    fraction = max(0, min(1, (t-VIEW_TIMES[index])*VIEW_FPS))
    return index, index+1, fraction
