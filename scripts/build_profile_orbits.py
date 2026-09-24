"""Rebuild the cover's animated orbital scene, preserving the surrounding layout.

The scene uses a perspective projection of three 3D orbital planes. Synchronized
front/back copies let SVG/SMIL occlude each satellite behind the central sphere
without JavaScript, external images, or a GIF rasterization step.
"""

from dataclasses import dataclass
from pathlib import Path
import math
import re
import xml.etree.ElementTree as ET

from profile_materials import CORE_RADIUS, ORBIT_COLORS, definitions
from profile_sky import sky


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = 144
CAMERA_DISTANCE = 500
LOOP_SECONDS = 48
TRAIL_DEGREES = 100
TRAIL_STEPS = 14


@dataclass(frozen=True)
class Orbit:
    body: str
    radius: float
    tilt: float
    roll: float
    phase: float
    period: float
    direction: int


ORBITS = (
    Orbit('amber', 135, 68, -23, 15, LOOP_SECONDS / 2, 1),
    Orbit('moon', 145, 59, 39, 195, LOOP_SECONDS / 3, -1),
    Orbit('ocean', 145, 75, 91, 315, LOOP_SECONDS / 4, 1),
)



def number(value):
    if abs(value) < .0005:
        value = 0
    return f'{value:.3f}'.rstrip('0').rstrip('.')


def project(orbit, angle):
    theta, tilt, roll = map(math.radians, (angle, orbit.tilt, orbit.roll))
    x = orbit.radius * math.cos(theta)
    y = orbit.radius * math.sin(theta) * math.cos(tilt)
    z = orbit.radius * math.sin(theta) * math.sin(tilt)
    scale = CAMERA_DISTANCE / (CAMERA_DISTANCE - z)
    return (
        scale * (x * math.cos(roll) - y * math.sin(roll)),
        scale * (x * math.sin(roll) + y * math.cos(roll)),
        z,
        scale,
    )


def key_times():
    return ';'.join(f'{i / SAMPLES:.6f}'.rstrip('0').rstrip('.') or '0'
                    for i in range(SAMPLES + 1))


def ribbon(orbit, angle):
    """Tapered trail, sampled from the same 3D trajectory as its planet."""
    left, right = [], []
    for i in range(TRAIL_STEPS + 1):
        progress = i / TRAIL_STEPS
        theta = angle - orbit.direction * TRAIL_DEGREES * (1 - progress)
        x, y, _, scale = project(orbit, theta)
        ax, ay, _, _ = project(orbit, theta - .1)
        bx, by, _, _ = project(orbit, theta + .1)
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy)
        half_width = (.08 + 1.8 * progress ** 1.3) * scale
        nx, ny = -dy / length * half_width, dx / length * half_width
        left.append((x + nx, y + ny))
        right.append((x - nx, y - ny))
    return 'M ' + ' L '.join(f'{number(x)} {number(y)}'
                             for x, y in left + list(reversed(right))) + ' Z'


def trail_definitions(orbit, animated):
    body = orbit.body
    parts = [f'''    <clipPath id="orbital-{body}-front"><path d="M -400 0 H 400 V 400 H -400 Z" transform="rotate({orbit.roll})"/></clipPath>
    <clipPath id="orbital-{body}-back"><path d="M -400 0 H 400 V -400 H -400 Z" transform="rotate({orbit.roll})"/></clipPath>
    <path id="orbital-trail-{body}-still" d="{ribbon(orbit, orbit.phase)}"/>''']
    if animated:
        values = ';'.join(ribbon(orbit, orbit.phase + orbit.direction * 360 * i / SAMPLES)
                          for i in range(SAMPLES + 1))
        parts.append(f'''    <path id="orbital-trail-{body}" d="{ribbon(orbit, orbit.phase)}">
      <animate attributeName="d" values="{values}" keyTimes="{key_times()}" dur="{number(orbit.period)}s" repeatCount="indefinite"/>
    </path>''')
    return '\n'.join(parts)


def trail(orbit, front, animated, dark):
    side = 'front' if front else 'back'
    color = ORBIT_COLORS[orbit.body][0]
    ref = f'orbital-trail-{orbit.body}' + ('' if animated else '-still')
    return f'''    <g class="orbital-trail" data-body="{orbit.body}" clip-path="url(#orbital-{orbit.body}-{side})" fill="{color}" stroke="{color}" stroke-linejoin="round" opacity="{'1' if front else '.5'}">
      <use href="#{ref}" stroke-width="8" opacity=".035"/>
      <use href="#{ref}" stroke-width="3.5" opacity=".12"/>
      <use href="#{ref}" stroke-width=".25" opacity=".85"/>
    </g>'''



def track(orbit, front, dark):
    start = 0 if front else 180
    points = [project(orbit, start + 180 * i / 64) for i in range(65)]
    d = 'M ' + ' L '.join(f'{number(x)} {number(y)}' for x, y, _, _ in points)
    color = ORBIT_COLORS[orbit.body][0]
    if not front:
        return f'    <path d="{d}" fill="none" stroke="{color}" stroke-opacity=".24" stroke-width=".8"/>'
    return f'''    <path d="{d}" transform="translate(.4 .7)" fill="none" stroke="#050A12" stroke-opacity=".36" stroke-width="2.1"/>
    <path d="{d}" fill="none" stroke="{color}" stroke-opacity=".58" stroke-width=".9"/>'''


def satellite(orbit, front, animated):
    samples = [project(orbit, orbit.phase + orbit.direction * 360 * i / SAMPLES) for i in range(SAMPLES + 1)]
    x, y, z, scale = samples[0]
    visible = (z >= 0) == front
    if not animated:
        if not visible:
            return ''
        return f'    <g class="satellite-static" data-body="{orbit.body}" transform="translate({number(x)} {number(y)}) scale({number(scale)})"><use href="#orbital-body-{orbit.body}"/></g>'
    keys = key_times()
    positions = ';'.join(f'{number(x)} {number(y)}' for x, y, _, _ in samples)
    scales = ';'.join(number(s) for _, _, _, s in samples)
    visibility = ';'.join('visible' if (depth >= -1e-9) == front else 'hidden' for _, _, depth, _ in samples)
    max_depth = orbit.radius * math.sin(math.radians(orbit.tilt))
    light = ';'.join(number(.86 + .14 * depth / max_depth) for _, _, depth, _ in samples)
    timing = f'keyTimes="{keys}" dur="{orbit.period}s" repeatCount="indefinite"'
    return f'''    <g class="satellite-layer" data-body="{orbit.body}" data-layer="{'front' if front else 'back'}" visibility="{'visible' if visible else 'hidden'}">
      <animate attributeName="visibility" values="{visibility}" calcMode="discrete" {timing}/>
      <g class="satellite-position" transform="translate({number(x)} {number(y)})">
        <animateTransform attributeName="transform" type="translate" values="{positions}" {timing}/>
        <g class="satellite-depth" transform="scale({number(scale)})">
          <animateTransform attributeName="transform" type="scale" values="{scales}" {timing}/>
          <animate attributeName="opacity" values="{light}" {timing}/>
          <use href="#orbital-body-{orbit.body}"/>
        </g>
      </g>
    </g>'''


def scene(mobile, animated, dark):
    placement = 'translate(508 442) scale(.56)' if mobile else 'translate(995 203)'
    parts = [f'  <!-- orbital-scene:start -->\n  <g id="orbital-monogram" transform="{placement}">',
             '  <defs>', *(trail_definitions(o, animated) for o in ORBITS), '  </defs>',
             '    <circle r="188" fill="url(#orbital-aura)"/>']
    if animated:
        parts.append('''    <circle class="motion" r="175" fill="url(#orbital-aura)" opacity=".45">
      <animate attributeName="opacity" values=".45;.7;.45" keyTimes="0;.5;1" calcMode="spline" keySplines=".42 0 .58 1;.42 0 .58 1" dur="8s" repeatCount="indefinite"/>
    </circle>''')
    for front in (False, True):
        if front:
            parts.append(f'    <circle r="{CORE_RADIUS + 1}" fill="none" stroke="#EABE80" stroke-width="6" opacity=".035"/>')
            parts.append(f'    <circle r="{CORE_RADIUS + 1}" fill="none" stroke="#EABE80" stroke-width="2.5" opacity=".12"/>')
            parts.append('    <use id="orbital-core-instance" href="#orbital-nucleus"/>')
        parts.append(f'  <g class="orbit-{"front" if front else "back"}">')
        parts.extend(track(orbit, front, dark) for orbit in ORBITS)
        parts.append('  </g>')
        parts.append('  <g class="orbit-still">' if animated else '  <g class="orbit-stationary">')
        parts.extend(trail(orbit, front, False, dark) for orbit in ORBITS)
        parts.extend(satellite(orbit, front, False) for orbit in ORBITS)
        parts.append('  </g>')
        if animated:
            parts.append('  <g class="motion">')
            parts.extend(trail(orbit, front, True, dark) for orbit in ORBITS)
            parts.extend(satellite(orbit, front, True) for orbit in ORBITS)
            parts.append('  </g>')
    parts.append('  </g>\n  <!-- orbital-scene:end -->\n')
    return '\n'.join(part for part in parts if part)


def rebuild(path):
    source = path.read_text(encoding='utf-8')
    mobile, animated, dark = ('mobile' in path.name, 'animated' in path.name, 'dark' in path.name)
    accent = '#E9B47A'
    # A night sky spans both theme variants; adjust light-theme ink for contrast.
    for old,new in {'#9E562E':'#E9B47A','#202124':'#F8F5EF','#4E4D49':'#D5D0C7',
                    '#64635E':'#A9AAA8','#D8D0C5':'#373B41'}.items():
        source=source.replace(old,new)
    if '<!-- profile-sky:start -->' in source:
        source=re.sub(r'  <!-- profile-sky:start -->.*?  <!-- profile-sky:end -->',sky(mobile),source,count=1,flags=re.S)
    else:
        source=re.sub(r'\n  <circle cx="(?:997|500)"[^\n]*fill="url\(#glow\)"/>','',source)
        source=source.replace('  <!-- orbital-scene:start -->',sky(mobile)+'\n  <!-- orbital-scene:start -->',1)
    if '<!-- orbital-definitions:start -->' in source:
        source = re.sub(r'  <!-- orbital-definitions:start -->.*?  <!-- orbital-definitions:end -->', definitions(accent), source, count=1, flags=re.S)
    else:
        source = re.sub(r'    <radialGradient id="planet(?:-halo)?"[^\n]+\n', '', source)
        source = source.replace('    <style>', definitions(accent) + '\n    <style>', 1)
    pattern = (r'  <!-- orbital-scene:start -->.*?  <!-- orbital-scene:end -->\n'
               if '<!-- orbital-scene:start -->' in source
               else r'  <g id="orbital-monogram".*?(?=  <rect x="(?:34|60)" y="(?:39|47)")')
    source, count = re.subn(pattern, scene(mobile, animated, dark), source, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f'Expected one orbital artwork block in {path}')
    source = source.replace(' text.monogram { font-family: Georgia, "Times New Roman", serif; }', '')
    # The existing divider accent shares the aura's eight-second rhythm.
    source = source.replace('dur="9s"', 'dur="8s"')
    if mobile:
        source = source.replace('x2="586" y2="491"', 'x2="390" y2="491"')
        source = source.replace('values="34;496;496"', 'values="34;300;300"')
    ET.fromstring(source)
    pending = path.with_suffix('.svg.tmp')
    pending.write_text(source, encoding='utf-8', newline='\n')
    pending.replace(path)
    return len(source.encode('utf-8'))


if __name__ == '__main__':
    for asset in sorted((ROOT / 'assets').glob('profile-cover-2026-*.svg')):
        print(f'{asset.name}: {rebuild(asset)} bytes')
