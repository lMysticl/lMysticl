"""Deterministic, full-bleed star field for the GitHub cover."""
import math
import random


def sky(mobile):
    width,height=(620,580) if mobile else (1200,430)
    rng=random.Random(263)
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
    # Stars span the entire banner, with brighter dust near the orbital scene.
    for i in range(410 if mobile else 660):
        x,y=rng.uniform(2,width-2),rng.uniform(2,height-2)
        r=rng.choices([.35,.55,.85,1.2],[45,32,19,4])[0]
        opacity=rng.uniform(.18,.55)*(.6 if x<width*.64 else 1)
        color=rng.choice(['#B1D4F0','#DAE9F2','#E3BE7E'])
        parts.append(f'    <circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" opacity="{opacity:.2f}"/>')
    for i in range(500):
        t=rng.random(); x=width*(.35+.65*t)+rng.gauss(0,30)
        y=height*(.95-.85*t)+math.sin(t*9)*height*.14+rng.gauss(0,28)
        if 2<x<width-2 and 2<y<height-2:
            parts.append(f'    <circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(.25,.85):.2f}" fill="#73B7EB" opacity="{rng.uniform(.03,.17):.2f}"/>')
    for x,y,size in [(width*.08,height*.59,4),(width*.56,height*.12,4),(width*.94,height*.82,6),(width*.68,height*.7,3)]:
        parts.append(f'    <circle cx="{x}" cy="{y}" r="{size*2}" fill="url(#sky-star)"/><path d="M {x-size} {y} H {x+size} M {x} {y-size} V {y+size}" stroke="#C2E2FF" stroke-width=".5" opacity=".7"/>')
    parts.append(f'    <rect width="{width}" height="{height}" fill="url(#sky-text-shade)"/>\n  </g>\n  <!-- profile-sky:end -->')
    return '\n'.join(parts)
