"""The selected dark Fullstack banner, with eight real spacecraft sprites."""
import base64
from dataclasses import dataclass
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADLINE = 'Fullstack Java Developer'
SAMPLES = 96
CAMERA = 900
EARTH_X, EARTH_Y, EARTH_RADIUS = 921, 202, 117
SCENE_X, SCENE_Y = EARTH_X, EARTH_Y
LOOP_SECONDS = 192


@dataclass(frozen=True)
class Satellite:
    ident: str
    label: tuple
    sprite: str
    color: str
    radius: float
    tilt: float
    roll: float
    phase: float
    period: int
    extent: int


SATELLITES = (
    Satellite('apis', ('APIs',), 'purple', '#BFA5EE', 151, 50, 27, 197, 64, 48),
    Satellite('services', ('Services',), 'gold', '#EAC46B', 153, 58, -22, 26, 64, 48),
    Satellite('data', ('Data',), 'teal', '#74D9DE', 159, 22, 70, 65, 64, 48),
    Satellite('java', ('Java 21',), 'gold', '#EAC46B', 167, 18, 0, -95, 96, 36),
    Satellite('spring', ('Spring Boot',), 'teal', '#82D7AE', 167, 18, 0, -38, 96, 36),
    Satellite('postgres', ('PostgreSQL',), 'purple', '#85C3F4', 167, 18, 0, 45, 96, 36),
    Satellite('kafka', ('Kafka',), 'purple', '#BFA5EE', 167, 18, 0, 98, 96, 36),
    Satellite('frontend', ('React / TypeScript',), 'teal', '#74D9DE', 167, 18, 0, 172, 96, 36),
)


def number(value):
    return f'{0 if abs(value) < .0005 else value:.3f}'.rstrip('0').rstrip('.')


def project(satellite, time):
    theta = math.radians(satellite.phase + 360 * time / satellite.period)
    tilt, roll = map(math.radians, (satellite.tilt, satellite.roll))
    x = satellite.radius * math.cos(theta)
    y = satellite.radius * math.sin(theta) * math.cos(tilt)
    z = satellite.radius * math.sin(theta) * math.sin(tilt)
    scale = CAMERA / (CAMERA - z)
    return (scale * (x * math.cos(roll) - y * math.sin(roll)),
            scale * (x * math.sin(roll) + y * math.cos(roll)), z, scale)


def caption_opacity(satellite, sample):
    """Fade a complete back-side caption before Earth can clip its letters."""
    x, y, depth, _ = sample
    if depth >= 0:
        return 1
    widths = {'apis': 34, 'services': 59, 'data': 33, 'java': 50,
              'spring': 75, 'postgres': 77, 'kafka': 37, 'frontend': 110}
    font = 15 if satellite.period == 64 else 14
    first = -34 if satellite.period == 64 else (-28 if len(satellite.label) == 1 else -44)
    first += caption_y_offset(satellite, sample)
    left, right = x - widths[satellite.ident] / 2, x + widths[satellite.ident] / 2
    top, bottom = y + first - font - 1, y + first + (len(satellite.label) - 1) * 16 + 4
    cx, cy = EARTH_X - SCENE_X, EARTH_Y - SCENE_Y
    dx, dy = max(left - cx, cx - right, 0), max(top - cy, cy - bottom, 0)
    clearance = math.hypot(dx, dy) - EARTH_RADIUS
    return max(0, min(1, (clearance - 6) / 8))


def caption_y_offset(satellite, sample):
    """Keep an upright caption in-frame when its orbit crosses the top pole."""
    font = 15 if satellite.period == 64 else 14
    first = -34 if satellite.period == 64 else (-28 if len(satellite.label) == 1 else -44)
    top = SCENE_Y + sample[1] + first - font - 1
    return max(0, 6 - top)


def definitions(mobile):
    files = [('business-background', 'business-background.webp')]
    files.extend((f'satellite-{name}', f'satellite-{name}.webp')
                 for name in ('purple', 'gold', 'teal'))
    parts = []
    for ident, filename in files:
        encoded = base64.b64encode((ROOT / 'assets' / 'web' / filename).read_bytes()).decode('ascii')
        geometry = 'x="0" y="0" width="1200" height="430"' if ident == 'business-background' else 'x="-50" y="-50" width="100" height="100"'
        parts.append(f'<image id="{ident}" {geometry} href="data:image/webp;base64,{encoded}"/>')
    parts.append(f'<clipPath id="earth-occlusion"><circle cx="{EARTH_X}" cy="{EARTH_Y}" r="{EARTH_RADIUS}"/></clipPath>')
    if mobile:
        parts.extend(['<clipPath id="mobile-copy"><rect width="640" height="310"/></clipPath>',
                      '<clipPath id="mobile-scene"><rect x="90" y="290" width="510" height="410"/></clipPath>'])
    return '\n'.join(parts)


def spacecraft(satellite, front, animated):
    samples = [project(satellite, satellite.period * i / SAMPLES) for i in range(SAMPLES + 1)]
    samples[-1] = samples[0]
    x, y, z, scale = samples[0]
    is_front = z >= 0
    if not animated and is_front != front:
        return ''
    keys = ';'.join(f'{i / SAMPLES:.6f}'.rstrip('0').rstrip('.') or '0'
                    for i in range(SAMPLES + 1))
    timing = f'keyTimes="{keys}" dur="{satellite.period}s" repeatCount="indefinite"'
    visibility = 'visible' if is_front == front else 'hidden'
    parts = [f'<g class="satellite-layer" data-satellite="{satellite.ident}" data-layer="{"front" if front else "back"}" visibility="{visibility}">']
    if animated:
        visible = ';'.join('visible' if (p[2] >= 0) == front else 'hidden' for p in samples)
        parts.append(f'<animate attributeName="visibility" values="{visible}" calcMode="discrete" {timing}/>')
    parts.append(f'<g class="satellite-position" transform="translate({number(x)} {number(y)})">')
    if animated:
        positions = ';'.join(f'{number(p[0])} {number(p[1])}' for p in samples)
        parts.append(f'<animateTransform attributeName="transform" type="translate" values="{positions}" {timing}/>')
    parts.append(f'<g class="satellite-depth" transform="scale({number(scale)})">')
    if animated:
        scales = ';'.join(number(p[3]) for p in samples)
        parts.append(f'<animateTransform attributeName="transform" type="scale" values="{scales}" {timing}/>')
    parts.append(f'<use href="#satellite-{satellite.sprite}" transform="scale({satellite.extent / 100})"/>')
    parts.append('</g>')
    font = 15 if satellite.period == 64 else 14
    first_y = -34 if satellite.period == 64 else (-28 if len(satellite.label) == 1 else -44)
    parts.append(f'<g class="satellite-caption" fill="{satellite.color}" color="{satellite.color}" opacity="{number(caption_opacity(satellite, samples[0]))}" transform="translate(0 {number(caption_y_offset(satellite, samples[0]))})">')
    if animated:
        opacities = ';'.join(number(caption_opacity(satellite, p)) for p in samples)
        parts.append(f'<animate attributeName="opacity" values="{opacities}" {timing}/>')
        offsets = ';'.join(f'0 {number(caption_y_offset(satellite, p))}' for p in samples)
        parts.append(f'<animateTransform attributeName="transform" type="translate" values="{offsets}" {timing}/>')
    parts.append('<path d="M 5 -9 L 10 -16 H 17" fill="none" stroke="currentColor" stroke-width=".8" opacity=".8"/>')
    for i, text in enumerate(satellite.label):
        parts.append(f'<text x="0" y="{first_y + i * 16}" text-anchor="middle" font-size="{font}">{text}</text>')
    parts.extend(['</g>', '</g>', '</g>'])
    return '\n'.join(parts)


def orbital_scene(animated):
    parts = []
    for front in (False, True):
        if front:
            parts.append('<use href="#business-background" clip-path="url(#earth-occlusion)"/>')
        parts.append(f'<g class="orbit-{"front" if front else "back"}" transform="translate({SCENE_X} {SCENE_Y})">')
        if animated:
            parts.append('<g class="orbit-still">')
            parts.extend(spacecraft(s, front, False) for s in SATELLITES)
            parts.append('</g><g class="motion">')
        parts.extend(spacecraft(s, front, animated) for s in SATELLITES)
        if animated:
            parts.append('</g>')
        parts.append('</g>')
    return '\n'.join(parts)


def cover(mobile, animated):
    width, height = (640, 700) if mobile else (1200, 430)
    css = '.orbit-still { display:none; } @media (prefers-reduced-motion:reduce) { .motion { display:none; } .orbit-still { display:inline; } }' if animated else '/* Static composition. */'
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="cover-title cover-desc" data-profile-style="business-dark">',
             f'<title id="cover-title">{HEADLINE}</title>',
             '<desc id="cover-desc">Reliable backend systems. Payments · Document processing · APIs. Java 21 · Spring Boot · PostgreSQL · Kafka. Daylight Earth with eight artificial satellites: APIs, Services, Data, Java 21, Spring Boot, PostgreSQL, Kafka, React / TypeScript.</desc>',
             '<defs>', definitions(mobile),
             f'<style>text {{ font-family:Arial,Helvetica,sans-serif; font-weight:400; fill:#D0DAE5; }} {css}</style>',
             '</defs>']
    if mobile:
        parts.extend(['<rect width="640" height="700" fill="#09121A"/>',
                      '<g clip-path="url(#mobile-copy)"><use href="#business-background" transform="translate(-25 -35) scale(.9)"/></g>',
                      '<g clip-path="url(#mobile-scene)"><g transform="translate(-601 303)">',
                      '<use href="#business-background"/>', orbital_scene(animated), '</g></g>'])
    else:
        parts.extend(['<use href="#business-background"/>', orbital_scene(animated)])
    parts.append('</svg>\n')
    return '\n'.join(parts)
