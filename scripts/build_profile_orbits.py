"""Rebuild the cover's vector orbital scene, preserving the surrounding layout.

The scene uses a perspective projection of three 3D orbital planes. Synchronized
front/back copies let SVG/SMIL occlude each satellite behind the central sphere
without JavaScript, external images, or a GIF rasterization step.
"""

from dataclasses import dataclass
from pathlib import Path
import math
import re
import xml.etree.ElementTree as ET


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

PALETTES = {
    'amber': ('#F6BE72', '#AF652C'),
    'moon': ('#C7B4F2', '#8470B1'),
    'ocean': ('#75D6DF', '#288795'),
}


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
    color = PALETTES[orbit.body][0 if dark else 1]
    ref = f'orbital-trail-{orbit.body}' + ('' if animated else '-still')
    return f'''    <g class="orbital-trail" data-body="{orbit.body}" clip-path="url(#orbital-{orbit.body}-{side})" fill="{color}" stroke="{color}" stroke-linejoin="round" opacity="{'1' if front else '.5'}">
      <use href="#{ref}" stroke-width="8" opacity=".035"/>
      <use href="#{ref}" stroke-width="3.5" opacity=".12"/>
      <use href="#{ref}" stroke-width=".25" opacity=".85"/>
    </g>'''


def definitions(accent):
    return f'''  <!-- orbital-definitions:start -->
    <radialGradient id="orbital-aura"><stop stop-color="{accent}" stop-opacity=".19"/><stop offset=".58" stop-color="{accent}" stop-opacity=".06"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
    <radialGradient id="orbital-shadow"><stop stop-color="#03070D" stop-opacity=".7"/><stop offset="1" stop-color="#03070D" stop-opacity="0"/></radialGradient>
    <radialGradient id="orbital-core" cx=".28" cy=".22" r=".85"><stop stop-color="#8C877B"/><stop offset=".2" stop-color="#55585A"/><stop offset=".52" stop-color="#252C34"/><stop offset=".8" stop-color="#10161F"/><stop offset="1" stop-color="#060B13"/></radialGradient>
    <radialGradient id="orbital-specular" cx=".35" cy=".25"><stop stop-color="#FFF1DA" stop-opacity=".45"/><stop offset="1" stop-color="#FFF1DA" stop-opacity="0"/></radialGradient>
    <linearGradient id="orbital-rim" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#FFF0C9"/><stop offset=".24" stop-color="#B88C59"/><stop offset=".56" stop-color="#303943"/><stop offset=".83" stop-color="#0B1018"/><stop offset="1" stop-color="#837467"/></linearGradient>
    <linearGradient id="orbital-gold" x1="0" y1="0" x2=".8" y2="1"><stop stop-color="#FFF1CE"/><stop offset=".3" stop-color="#DDB57B"/><stop offset=".6" stop-color="#9E6E3D"/><stop offset=".83" stop-color="#D6AA6C"/><stop offset="1" stop-color="#80532F"/></linearGradient>
    <radialGradient id="orbital-amber" cx=".28" cy=".22" r=".82"><stop stop-color="#FFE7B1"/><stop offset=".35" stop-color="#D5A061"/><stop offset=".64" stop-color="#986039"/><stop offset=".84" stop-color="#4B3027"/><stop offset="1" stop-color="#1A1920"/></radialGradient>
    <radialGradient id="orbital-moon" cx=".25" cy=".2" r=".82"><stop stop-color="#FFF3D7"/><stop offset=".4" stop-color="#C3C1B6"/><stop offset=".68" stop-color="#7E8587"/><stop offset="1" stop-color="#252E39"/></radialGradient>
    <radialGradient id="orbital-ocean" cx=".28" cy=".2" r=".83"><stop stop-color="#B4ECDE"/><stop offset=".25" stop-color="#4F9C9C"/><stop offset=".6" stop-color="#20545F"/><stop offset=".86" stop-color="#0C293D"/><stop offset="1" stop-color="#07101F"/></radialGradient>
    <radialGradient id="orbital-terminator" cx=".28" cy=".2" r=".83"><stop offset=".28" stop-color="#030A15" stop-opacity="0"/><stop offset=".66" stop-color="#030A15" stop-opacity=".08"/><stop offset=".86" stop-color="#030A15" stop-opacity=".45"/><stop offset="1" stop-color="#030A15" stop-opacity=".8"/></radialGradient>
    <linearGradient id="orbital-rings" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#735846"/><stop offset=".45" stop-color="#D3B88C"/><stop offset=".7" stop-color="#F4D6A1"/><stop offset="1" stop-color="#9F784F"/></linearGradient>
    <clipPath id="orbital-core-clip"><circle r="82"/></clipPath>
    <clipPath id="orbital-amber-clip"><circle r="17"/></clipPath>
    <clipPath id="orbital-moon-clip"><circle r="13"/></clipPath>
    <clipPath id="orbital-ocean-clip"><circle r="12"/></clipPath>
    <text id="orbital-letter" class="monogram" x="-53" y="54" font-size="154" font-style="italic">P</text>
    <g id="orbital-nucleus">
      <circle cx="8" cy="10" r="101" fill="url(#orbital-shadow)"/>
      <circle r="82" fill="url(#orbital-core)" stroke="url(#orbital-rim)" stroke-width="1.5"/>
      <g clip-path="url(#orbital-core-clip)">
        <ellipse cx="-22" cy="-40" rx="58" ry="35" transform="rotate(-26)" fill="url(#orbital-specular)"/>
        <path d="M -76 -26 C -40 -53 25 -39 78 -7 M -78 -13 C -31 -39 36 -18 81 13 M -69 41 C -22 57 31 69 62 48" fill="none" stroke="#D4C7AC" stroke-opacity=".08" stroke-width=".75"/>
        <path d="M -41 -71 C -69 -34 -72 20 -38 70 M 17 -79 C -14 -37 -22 20 12 81" fill="none" stroke="#C5BBA8" stroke-opacity=".065" stroke-width=".7"/>
        <path d="M -70 -29 A 76 76 0 0 1 -26 -71" fill="none" stroke="#FFF0CF" stroke-opacity=".5" stroke-width="1.4" stroke-linecap="round"/>
        <path d="M 29 75 A 80 80 0 0 0 75 29" fill="none" stroke="#799BA4" stroke-opacity=".2" stroke-width="1"/>
        <use href="#orbital-letter" transform="translate(5 6)" fill="#040810" opacity=".85"/>
        <use href="#orbital-letter" transform="translate(3 4)" fill="#5B3E28"/>
        <use href="#orbital-letter" transform="translate(1.5 2)" fill="#997047"/>
        <use href="#orbital-letter" fill="url(#orbital-gold)" stroke="#FFE7B5" stroke-opacity=".38" stroke-width=".65"/>
      </g>
    </g>
    <g id="orbital-body-amber">
      <g transform="rotate(-24)"><ellipse rx="30" ry="8" fill="none" stroke="#201E23" stroke-opacity=".45" stroke-width="6"/><ellipse rx="28" ry="7.4" fill="none" stroke="url(#orbital-rings)" stroke-width="4.2"/><ellipse rx="31" ry="8.7" fill="none" stroke="#BFA17A" stroke-opacity=".7" stroke-width=".8"/></g>
      <circle r="17" fill="url(#orbital-amber)"/>
      <g clip-path="url(#orbital-amber-clip)" transform="rotate(-12)">
        <path d="M -20 -9 Q 0 -3 19 -8 M -20 -2 Q 1 6 20 0 M -20 8 Q 1 13 20 8" fill="none" stroke="#765137" stroke-opacity=".45" stroke-width="2.6"/>
        <path d="M -18 -12 Q -1 -7 18 -11 M -20 3 Q 0 10 20 4" fill="none" stroke="#FFE3AD" stroke-opacity=".55" stroke-width="1.1"/>
        <ellipse cx="6" cy="2" rx="4" ry="1.6" fill="#BF7845" opacity=".65"/>
        <path d="M -20 2 Q 0 -2 20 -9" fill="none" stroke="#1C1820" stroke-opacity=".32" stroke-width="2.4"/>
      </g>
      <circle r="17" fill="url(#orbital-terminator)"/>
      <g transform="rotate(-24)"><path d="M -28 0 A 28 7.4 0 0 0 28 0" fill="none" stroke="url(#orbital-rings)" stroke-width="4.2"/><path d="M -31 0 A 31 8.7 0 0 0 31 0" fill="none" stroke="#EFD6A8" stroke-opacity=".8" stroke-width=".8"/><path d="M -25 0 A 25 6.5 0 0 0 25 0" fill="none" stroke="#6C523C" stroke-opacity=".75" stroke-width=".75"/></g>
      <path d="M -13 -7 A 14 14 0 0 1 -6 -13" fill="none" stroke="#FFF2CE" stroke-opacity=".8" stroke-width="1" stroke-linecap="round"/>
    </g>
    <g id="orbital-body-moon">
      <circle r="13" fill="url(#orbital-moon)"/>
      <g clip-path="url(#orbital-moon-clip)">
        <ellipse cx="-4" cy="-3" rx="3.4" ry="3" fill="#777C78" opacity=".65"/>
        <path d="M -7 -3 A 3.2 2.9 0 0 0 -1 -2" fill="none" stroke="#EEE8CF" stroke-opacity=".8" stroke-width=".9"/>
        <ellipse cx="4.7" cy="4.8" rx="3.2" ry="2.4" transform="rotate(-20 4.7 4.8)" fill="#646D73" opacity=".55"/>
        <path d="M 2 5 Q 4.8 8.5 8 4.5" fill="none" stroke="#DAD8C8" stroke-opacity=".7" stroke-width=".8"/>
        <circle cx="3.7" cy="-6.3" r="1.8" fill="#737C7A" opacity=".55"/>
        <path d="M 2 -6.5 Q 3.8 -3.7 5.3 -6.3" fill="none" stroke="#F0E8CF" stroke-opacity=".75" stroke-width=".65"/>
        <circle cx="-6" cy="5" r="1.3" fill="#697375" opacity=".6"/><circle cx="-1" cy="8.7" r=".7" fill="#EDE5CF" opacity=".5"/><circle cx="7.4" cy="-1.7" r=".8" fill="#687579" opacity=".7"/>
      </g>
      <circle r="13" fill="url(#orbital-terminator)"/>
      <path d="M -10 -6 A 11.5 11.5 0 0 1 -4 -11" fill="none" stroke="#FFF5DC" stroke-opacity=".7" stroke-width=".75"/>
    </g>
    <g id="orbital-body-ocean">
      <circle r="12" fill="url(#orbital-ocean)" stroke="#89BFC1" stroke-opacity=".3" stroke-width=".65"/>
      <g clip-path="url(#orbital-ocean-clip)">
        <path d="M -8 -10 L -3 -8 -4 -4 0 -2 -2 2 -5 1 -7 4 -10 2 -10 -3 Z M 4 0 L 9 -2 12 2 9 7 5 9 2 6 3 3 Z" fill="#8AA99A" opacity=".6"/>
        <path d="M -13 -4 Q -6 -8 1 -4 T 14 -5 M -13 3 Q -7 0 0 4 T 14 4" fill="none" stroke="#E2ECE0" stroke-opacity=".53" stroke-width="1.2"/>
        <path d="M -6 -10 Q -1 -7 6 -8 M -9 9 Q -2 5 4 9" fill="none" stroke="#E7EEE0" stroke-opacity=".38" stroke-width=".8"/>
      </g>
      <circle r="12" fill="url(#orbital-terminator)"/>
      <path d="M -10 -4 A 10.8 10.8 0 0 1 -4 -10" fill="none" stroke="#C4F4EB" stroke-opacity=".85" stroke-width=".9" stroke-linecap="round"/>
    </g>
  <!-- orbital-definitions:end -->'''


def track(orbit, front, dark):
    start = 0 if front else 180
    points = [project(orbit, start + 180 * i / 64) for i in range(65)]
    d = 'M ' + ' L '.join(f'{number(x)} {number(y)}' for x, y, _, _ in points)
    color = PALETTES[orbit.body][0 if dark else 1]
    if not front:
        return f'    <path d="{d}" fill="none" stroke="{color}" stroke-opacity=".15" stroke-width=".7"/>'
    return f'''    <path d="{d}" transform="translate(.4 .7)" fill="none" stroke="#050A12" stroke-opacity=".36" stroke-width="2.1"/>
    <path d="{d}" fill="none" stroke="{color}" stroke-opacity=".3" stroke-width=".7"/>'''


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
    placement = 'translate(508 442) scale(.56)' if mobile else 'translate(995 209)'
    parts = [f'  <!-- orbital-scene:start -->\n  <g id="orbital-monogram" transform="{placement}">',
             '  <defs>', *(trail_definitions(o, animated) for o in ORBITS), '  </defs>',
             '    <circle r="188" fill="url(#orbital-aura)"/>']
    if animated:
        parts.append('''    <circle class="motion" r="175" fill="url(#orbital-aura)" opacity=".45">
      <animate attributeName="opacity" values=".45;.7;.45" keyTimes="0;.5;1" calcMode="spline" keySplines=".42 0 .58 1;.42 0 .58 1" dur="8s" repeatCount="indefinite"/>
    </circle>''')
    for front in (False, True):
        if front:
            parts.append('    <circle r="83" fill="none" stroke="#EABE80" stroke-width="6" opacity=".035"/>')
            parts.append('    <circle r="83" fill="none" stroke="#EABE80" stroke-width="2.5" opacity=".12"/>')
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
    accent = '#E9B47A' if dark else '#9E562E'
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
