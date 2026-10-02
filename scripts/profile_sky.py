"""Deterministic, full-bleed star field for the GitHub cover."""
import math
import random
from collections import defaultdict


def dot(x, y, radius):
    """A circle subpath; many stars share one paint node."""
    x, y, radius = round(x, 2), round(y, 2), round(radius, 2)
    diameter = radius * 2
    return (f'M{x-radius:.2f} {y:.2f}a{radius:.2f} {radius:.2f} 0 1 0 '
            f'{diameter:.2f} 0a{radius:.2f} {radius:.2f} 0 1 0 {-diameter:.2f} 0z')


def distant_stars(mobile, width, height):
    rng = random.Random(263)
    groups = defaultdict(list)
    for _ in range(670 if mobile else 1120):
        x, y = rng.uniform(2, width-2), rng.uniform(2, height-2)
        radius = rng.choices([.4, .6, .9, 1.3], [42, 32, 21, 5])[0]
        brightness = rng.choice([.25, .4, .55, .7])
        # Keep quiet space behind the copy, with richer detail near Earth.
        if (y < 385 if mobile else x < 730):
            brightness *= .46
        color = rng.choice(['#B1D4F0', '#DAE9F2', '#E3BE7E'])
        groups[(color, round(brightness, 3))].append(dot(x, y, radius))
    dust = []
    for _ in range(460 if mobile else 680):
        t = rng.random()
        x = width*(.35+.65*t)+rng.gauss(0, 30)
        y = height*(.95-.85*t)+math.sin(t*9)*height*.14+rng.gauss(0, 28)
        if 2 < x < width-2 and 2 < y < height-2:
            dust.append(dot(x, y, rng.uniform(.25, .8)))
    groups[('#73B7EB', .13)] = dust
    parts = ['    <g id="distant-stars">']
    for i, ((color, opacity), paths) in enumerate(sorted(groups.items())):
        parts.append(f'      <path id="star-batch-{i}" data-point-count="{len(paths)}" '
                     f'd="{"".join(paths)}" fill="{color}" opacity="{opacity}"/>')
    parts.append('    </g>')
    return '\n'.join(parts)


def moving_stars(mobile, animated, frame_time=None):
    """Three repeated tiles drift behind Earth; 48s is an exact loop."""
    x, y, width, height = (280, 390, 338, 126) if mobile else (730, 12, 468, 355)
    rng = random.Random(419 if mobile else 418)
    layers = ((100 if mobile else 130, .35, .6, .4, 48),
              (70 if mobile else 95, .55, .9, .52, 24),
              (35 if mobile else 48, .9, 1.4, .65, 16))
    parts = [f'''    <defs>
      <clipPath id="star-drift-frame"><rect x="{x}" y="{y}" width="{width}" height="{height}"/></clipPath>
    </defs>
    <g id="moving-starfield" clip-path="url(#star-drift-frame)">''']
    still = []
    for i, (count, smallest, largest, brightness, period) in enumerate(layers):
        points = [(rng.uniform(x, x+width), rng.uniform(y, y+height),
                   rng.uniform(smallest, largest)) for _ in range(count)]
        path = ''.join(dot(px+tile*width, py, radius)
                       for tile in (0, 1) for px, py, radius in points)
        travel = -width*((frame_time % period)/period) if frame_time is not None else 0
        parts.append(f'      <g id="star-drift-{i}" class="star-drift{" motion" if animated else ""}" '
                     f'data-visible-points="{count}" transform="translate({travel:.3f} 0)">')
        if animated:
            parts.append(f'        <animateTransform attributeName="transform" type="translate" '
                         f'values="0 0;{-width} 0" dur="{period}s" repeatCount="indefinite"/>')
        parts.append(f'        <path d="{path}" fill="#D9EEFF" opacity="{brightness}"/>\n      </g>')
        if animated:
            still.append(f'        <path d="{"".join(dot(*p) for p in points)}" '
                         f'fill="#D9EEFF" opacity="{brightness}"/>')
    if animated:
        parts.extend(['      <g class="starfield-still">', *still, '      </g>'])
    parts.append('    </g>')
    return '\n'.join(parts)


def shooting_stars(mobile, animated, frame_time=None):
    """Six staggered meteor flights, clipped away from the professional copy.

    Their 12/16/24-second schedules share the existing 48-second orbital loop.
    frame_time lets the preview exporter render the same authored trajectories.
    """
    bounds = (280, 390, 338, 126) if mobile else (730, 12, 468, 355)
    starts = ((290, 397), (390, 399), (290, 427), (320, 401), (390, 406), (296, 438)) if mobile else (
        (740, 24), (890, 30), (744, 146), (790, 32), (925, 45), (745, 255))
    ends = ((610, 497), (612, 475), (610, 508), (600, 480), (610, 483), (605, 511)) if mobile else (
        (1160, 168), (1170, 128), (1170, 252), (1150, 150), (1180, 132), (1180, 345))
    lengths = (55, 34, 42, 48, 32, 39) if mobile else (98, 58, 76, 84, 54, 72)
    schedules = ((16, .1, .28, .85), (24, .55, .67, .6),
                 (12, .03, .19, .5), (16, .38, .53, .7),
                 (24, .82, .94, .55), (12, .61, .78, .45))
    x,y,width,height = bounds
    parts = [f'''  <defs>
    <clipPath id="meteor-frame"><rect x="{x}" y="{y}" width="{width}" height="{height}"/></clipPath>
  </defs>
  <g id="shooting-stars" clip-path="url(#meteor-frame)">''']
    for i, (start,end,length,schedule) in enumerate(zip(starts,ends,lengths,schedules)):
        if not animated and frame_time is None and i >= 2:
            break
        period,enter,leave,brightness = schedule
        slope = (end[1]-start[1])/(end[0]-start[0])
        sx,sy = start
        opacity = brightness
        if frame_time is None:
            if not animated:
                sx,sy = ((start[k]+end[k])/2 for k in (0,1))
            else:
                opacity = 0
        else:
            phase = (frame_time % period)/period
            progress = max(0, min(1, (phase-enter)/(leave-enter)))
            sx,sy = (start[k]+progress*(end[k]-start[k]) for k in (0,1))
            fade = min((phase-enter)/.025, (leave-phase)/.025, 1)
            opacity = brightness*max(0, fade)
        parts.append(f'''    <defs>
      <linearGradient id="meteor-tail-{i}" gradientUnits="userSpaceOnUse" x1="{-length}" y1="{-length*slope}" x2="0" y2="0">
        <stop stop-color="#88C9F3" stop-opacity="0"/>
        <stop offset=".65" stop-color="#BBDDFA" stop-opacity=".45"/>
        <stop offset="1" stop-color="#F5FAFF"/>
      </linearGradient>
    </defs>
    <g id="shooting-star-{i}" class="shooting-star{' motion' if animated else ''}" transform="translate({sx:.3f} {sy:.3f})" opacity="{opacity:.3f}">''')
        if animated:
            timing = f'dur="{period}s" repeatCount="indefinite"'
            parts.append(f'''      <animateTransform attributeName="transform" type="translate" values="{start[0]} {start[1]};{start[0]} {start[1]};{end[0]} {end[1]};{end[0]} {end[1]}" keyTimes="0;{enter};{leave};1" {timing}/>
      <animate attributeName="opacity" values="0;0;{brightness};{brightness};0;0" keyTimes="0;{enter};{enter+.025};{leave-.025};{leave};1" {timing}/>''')
        parts.append(f'''      <path d="M {-length} {-length*slope:.3f} Q {-length*.4:.3f} {-length*.4*slope-1:.3f} 0 0 Q {-length*.4:.3f} {-length*.4*slope+1:.3f} {-length} {-length*slope:.3f} Z" fill="url(#meteor-tail-{i})"/>
      <circle r="5" fill="url(#sky-star)" opacity=".5"/>
      <circle r=".9" fill="#F4FAFF"/>
    </g>''')
    parts.append('  </g>')
    return '\n'.join(parts)


def sky(mobile, animated=False, frame_time=None):
    width,height=(620,580) if mobile else (1200,430)
    parts=[f'''  <!-- profile-sky:start -->
  <defs>
    <clipPath id="sky-frame"><rect x="1" y="1" width="{width-2}" height="{height-2}" rx="18"/></clipPath>
    <radialGradient id="sky-blue"><stop stop-color="#165991" stop-opacity=".42"/><stop offset=".5" stop-color="#0C315B" stop-opacity=".2"/><stop offset="1" stop-color="#081629" stop-opacity="0"/></radialGradient>
    <radialGradient id="sky-lilac"><stop stop-color="#B6ACEF" stop-opacity=".1"/><stop offset="1" stop-color="#081629" stop-opacity="0"/></radialGradient>
    <radialGradient id="sky-gold"><stop stop-color="#D59C4E" stop-opacity=".18"/><stop offset=".45" stop-color="#956237" stop-opacity=".05"/><stop offset="1" stop-color="#05101D" stop-opacity="0"/></radialGradient>
    <radialGradient id="sky-star"><stop stop-color="#E2F3FF"/><stop offset=".15" stop-color="#82C5FF" stop-opacity=".8"/><stop offset="1" stop-color="#368DFF" stop-opacity="0"/></radialGradient>
    <linearGradient id="sky-text-shade"><stop stop-color="#030A14" stop-opacity=".32"/><stop offset=".62" stop-color="#030A14" stop-opacity=".23"/><stop offset="1" stop-color="#030A14" stop-opacity="0"/></linearGradient>
  </defs>
  <g id="full-banner-starfield" clip-path="url(#sky-frame)">
    <rect width="{width}" height="{height}" fill="#081629"/>
    <ellipse cx="{width*.72}" cy="{height*.3}" rx="{width*.43}" ry="{height*.8}" fill="url(#sky-blue)"/>
    <ellipse cx="{width*.88}" cy="{height*.52}" rx="{width*.2}" ry="{height*.48}" fill="url(#sky-gold)"/>
    <ellipse cx="{width*.83}" cy="{height*.55}" rx="{width*.16}" ry="{height*.44}" fill="url(#sky-lilac)"/>
    <ellipse cx="{width*.15}" cy="{height*.8}" rx="{width*.35}" ry="{height*.6}" fill="url(#sky-blue)"/>''']
    parts.append(distant_stars(mobile, width, height))
    parts.append(moving_stars(mobile, animated, frame_time))
    for x,y,size in [(width*.08,height*.59,4),(width*.56,height*.12,4),(width*.94,height*.82,6),(width*.68,height*.7,3)]:
        parts.append(f'    <circle cx="{x}" cy="{y}" r="{size*2}" fill="url(#sky-star)"/><path d="M {x-size} {y} H {x+size} M {x} {y-size} V {y+size}" stroke="#C2E2FF" stroke-width=".5" opacity=".7"/>')
    parts.append(f'    <rect width="{width}" height="{height}" fill="url(#sky-text-shade)"/>')
    parts.append(shooting_stars(mobile, animated, frame_time))
    parts.append('  </g>\n  <!-- profile-sky:end -->')
    return '\n'.join(parts)
