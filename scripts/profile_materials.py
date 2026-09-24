"""Vector materials for the profile's planets and gold monogram.

The artwork is original geometry. Reference photographs inform lighting,
layered rings and cloud structure; no third-party pixels or fonts are embedded.
"""

CORE_RADIUS = 90
MIDNIGHT = '#081629'
CHAMPAGNE = '#F2CC8F'
TURQUOISE = '#65D6CE'
PERIWINKLE = '#B6ACEF'
ORBIT_COLORS = {
    'amber': (CHAMPAGNE, '#AD753B'),
    'moon': (PERIWINKLE, '#7C70A8'),
    'ocean': (TURQUOISE, '#277F88'),
}

# A custom serif outline keeps the monogram identical on every GitHub client.
LETTER = ('M -49 59 L -48 54 C -36 53 -32 52 -30 41 L -10 -42 '
          'C -7 -54 -9 -58 -21 -59 L -20 -65 L 28 -65 '
          'C 57 -65 72 -54 68 -31 C 64 -9 45 7 15 7 L 3 7 '
          'L -5 42 C -7 52 -3 54 11 54 L 10 59 Z '
          'M 9 -8 L 20 -8 C 40 -8 50 -18 54 -35 '
          'C 57 -48 47 -52 30 -52 L 20 -52 Z')


def gradients(accent):
    return f'''
    <radialGradient id="orbital-aura"><stop stop-color="{accent}" stop-opacity=".19"/><stop offset=".58" stop-color="{accent}" stop-opacity=".06"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
    <radialGradient id="orbital-shadow"><stop stop-color="#020812" stop-opacity=".85"/><stop offset="1" stop-color="#020812" stop-opacity="0"/></radialGradient>
    <radialGradient id="orbital-core" cx=".25" cy=".18" r=".84"><stop stop-color="#C4C3B3"/><stop offset=".19" stop-color="#789096"/><stop offset=".42" stop-color="#375361"/><stop offset=".69" stop-color="#112B40"/><stop offset=".9" stop-color="{MIDNIGHT}"/><stop offset="1" stop-color="#020812"/></radialGradient>
    <radialGradient id="orbital-specular"><stop stop-color="#FFF5DC" stop-opacity=".55"/><stop offset=".42" stop-color="#D9E8E2" stop-opacity=".15"/><stop offset="1" stop-color="#C9E8EF" stop-opacity="0"/></radialGradient>
    <radialGradient id="orbital-atmosphere"><stop offset=".81" stop-color="{TURQUOISE}" stop-opacity="0"/><stop offset=".9" stop-color="#8BDDDC" stop-opacity=".2"/><stop offset=".94" stop-color="#86C6DC" stop-opacity=".045"/><stop offset="1" stop-color="{TURQUOISE}" stop-opacity="0"/></radialGradient>
    <linearGradient id="orbital-rim" x1=".1" y1="0" x2=".9" y2="1"><stop stop-color="#F6E6BA"/><stop offset=".3" stop-color="#A4BDC2"/><stop offset=".57" stop-color="#234250"/><stop offset=".77" stop-color="#101E2B"/><stop offset="1" stop-color="#AC895B"/></linearGradient>
    <linearGradient id="orbital-gold" gradientUnits="userSpaceOnUse" x1="-28" y1="-64" x2="49" y2="65"><stop stop-color="#FFF4D4"/><stop offset=".24" stop-color="{CHAMPAGNE}"/><stop offset=".43" stop-color="#B57E42"/><stop offset=".49" stop-color="#D4A05E"/><stop offset=".56" stop-color="#FFE4AF"/><stop offset=".72" stop-color="#E3B270"/><stop offset="1" stop-color="#976033"/></linearGradient>
    <linearGradient id="orbital-bevel" gradientUnits="userSpaceOnUse" x1="-35" y1="-62" x2="45" y2="62"><stop stop-color="#FFF9E5"/><stop offset=".28" stop-color="#FFE4AA"/><stop offset=".52" stop-color="#BE864A"/><stop offset=".73" stop-color="#FFF0C8"/><stop offset="1" stop-color="#87542D"/></linearGradient>
    <linearGradient id="orbital-gold-side" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#8B5A30"/><stop offset=".45" stop-color="#47301E"/><stop offset=".68" stop-color="#B38348"/><stop offset="1" stop-color="#261D18"/></linearGradient>
    <radialGradient id="orbital-amber" cx=".25" cy=".18" r=".88"><stop stop-color="#FFF0C9"/><stop offset=".28" stop-color="#DFC08B"/><stop offset=".55" stop-color="#BA8B58"/><stop offset=".8" stop-color="#62452F"/><stop offset="1" stop-color="#151827"/></radialGradient>
    <radialGradient id="orbital-moon" cx=".24" cy=".17" r=".9"><stop stop-color="#FAF0DB"/><stop offset=".28" stop-color="#D5D4CE"/><stop offset=".58" stop-color="#9EABB2"/><stop offset=".83" stop-color="#485A6D"/><stop offset="1" stop-color="#121F35"/></radialGradient>
    <radialGradient id="orbital-crater" cx=".65" cy=".8" r=".85"><stop stop-color="#ACBAC0"/><stop offset=".48" stop-color="#71818F"/><stop offset=".74" stop-color="#3B5264"/><stop offset="1" stop-color="#526472"/></radialGradient>
    <radialGradient id="orbital-ocean" cx=".26" cy=".18" r=".87"><stop stop-color="#97DFEA"/><stop offset=".24" stop-color="#358EB4"/><stop offset=".53" stop-color="#14567F"/><stop offset=".79" stop-color="#092C51"/><stop offset="1" stop-color="#031326"/></radialGradient>
    <linearGradient id="orbital-land" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#CED3A7"/><stop offset=".35" stop-color="#8BAD99"/><stop offset=".68" stop-color="#4F938C"/><stop offset="1" stop-color="#286473"/></linearGradient>
    <radialGradient id="orbital-terminator" cx=".23" cy=".16" r=".9"><stop offset=".25" stop-color="#020916" stop-opacity="0"/><stop offset=".53" stop-color="#020916" stop-opacity=".08"/><stop offset=".75" stop-color="#020916" stop-opacity=".34"/><stop offset="1" stop-color="#020916" stop-opacity=".86"/></radialGradient>
    <linearGradient id="orbital-ring-light" x1="0" y1="0" x2=".9" y2="1"><stop stop-color="#FFEBBD"/><stop offset=".35" stop-color="#C9AE80"/><stop offset=".64" stop-color="#F6DCA9"/><stop offset="1" stop-color="#74614D"/></linearGradient>'''


def nucleus():
    # Broad swirls remain readable at 1x; smaller tributaries add surface relief.
    swirls = [
        'M -90 -35 C -55 -73 -35 -24 -3 -38 S 44 -62 82 -21',
        'M -94 -23 C -64 -58 -47 -23 -24 -22 S 4 -49 30 -32 S 69 -19 94 -6',
        'M -97 -8 C -68 -24 -57 -4 -40 2 S -17 -6 -9 -22',
        'M -88 25 C -51 11 -41 42 -7 34 S 38 4 78 27',
        'M -72 51 C -43 30 -14 65 21 50 S 60 27 88 41',
        'M -53 71 C -26 49 14 77 44 62 S 67 49 79 54',
    ]
    terrain = '\n'.join(
        f'        <path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" opacity="{opacity}"/>'
        for i, d in enumerate(swirls)
        for color, width, opacity in (
            ('#061722', 6 + i % 3, '.28'), ('#9FB5AE', 1.2, '.25'),
        ))
    sides = '\n'.join(
        f'        <use href="#orbital-letter" transform="translate({i} {i * .85:.2f})" fill="url(#orbital-gold-side)" stroke="#6F4929" stroke-width=".7"/>'
        for i in range(8, 0, -1))
    return f'''
    <clipPath id="orbital-core-clip"><circle r="{CORE_RADIUS}"/></clipPath>
    <path id="orbital-letter" d="{LETTER}" fill-rule="evenodd" clip-rule="evenodd"/>
    <g id="orbital-nucleus">
      <circle cx="9" cy="12" r="111" fill="url(#orbital-shadow)"/>
      <circle r="100" fill="url(#orbital-atmosphere)"/>
      <circle r="{CORE_RADIUS}" fill="url(#orbital-core)" stroke="url(#orbital-rim)" stroke-width="1.3"/>
      <g clip-path="url(#orbital-core-clip)">
{terrain}
        <path d="M -82 -45 C -61 -58 -59 -37 -42 -40 S -24 -63 -9 -52 M -80 31 C -63 20 -49 47 -32 43 M 24 68 C 43 64 49 45 71 44" fill="none" stroke="#D7C49A" stroke-width=".7" opacity=".32"/>
        <ellipse cx="-37" cy="-55" rx="59" ry="32" transform="rotate(-24 -37 -55)" fill="url(#orbital-specular)"/>
        <circle r="90" fill="url(#orbital-terminator)" opacity=".32"/>
        <path d="M -82 -24 A 86 86 0 0 1 -28 -81" fill="none" stroke="#F7EED4" stroke-opacity=".62" stroke-width="1.25" stroke-linecap="round"/>
        <path d="M 20 87 A 89 89 0 0 0 81 36" fill="none" stroke="#CAA772" stroke-opacity=".38" stroke-width="1"/>
        <use href="#orbital-letter" transform="translate(12 12)" fill="#020711" stroke="#020711" stroke-width="9" opacity=".13"/>
        <use href="#orbital-letter" transform="translate(9 9)" fill="#020711" stroke="#020711" stroke-width="3" opacity=".6"/>
{sides}
        <use href="#orbital-letter" fill="url(#orbital-gold)" stroke="url(#orbital-bevel)" stroke-width="2.4" stroke-linejoin="round"/>
        <path d="M -18 -63 H 28 C 52 -63 66 -56 67 -43 M -47 57 H 9 M 12 -10 C 33 -9 45 -17 50 -30" fill="none" stroke="#FFF4D4" stroke-opacity=".7" stroke-width=".7" stroke-linecap="round"/>
      </g>
    </g>'''


def rings(front):
    # Cassini-inspired gaps and varying optical density, with separate near arcs.
    layers = [(26,7.8,1.6,'.3'),(28,8.5,1.4,'.55'),(30,9.1,1.6,'.85'),
              (31.7,9.7,1.1,'.95'),(34.2,10.4,1.4,'.75'),(36,11,.65,'.65')]
    parts = ['      <g transform="rotate(-24)">']
    for rx, ry, width, opacity in layers:
        geometry = (f'path d="M -{rx} 0 A {rx} {ry} 0 0 0 {rx} 0"'
                    if front else f'ellipse rx="{rx}" ry="{ry}"')
        parts.append(f'        <{geometry} fill="none" stroke="url(#orbital-ring-light)" stroke-width="{width}" opacity="{opacity}"/>')
    if front:
        parts.append('        <path d="M -35 0 A 35 10.7 0 0 0 35 0" fill="none" stroke="#FFF1D0" stroke-width=".35" opacity=".8"/>')
    else:
        parts.append('        <path d="M 17 -9 L 33 -6 29 -1 16 -2 Z" fill="#070B13" opacity=".6"/>')
    parts.append('      </g>')
    return '\n'.join(parts)


def amber():
    bands = []
    for y, width, color, opacity in [(-14,2.4,'#F8E4B9',.6),(-10,2,'#9B7954',.5),
        (-6,3,'#F7D9A4',.55),(-1,3.7,'#98704B',.6),(4,2.6,'#E7BD81',.8),
        (9,2.4,'#8F6848',.45),(13,1.7,'#F2D3A0',.55)]:
        bands.append(f'        <path d="M -24 {y} C -8 {y+5} 7 {y+5} 24 {y-1}" fill="none" stroke="{color}" stroke-width="{width}" opacity="{opacity}"/>')
    return f'''
    <clipPath id="orbital-amber-clip"><circle r="20"/></clipPath>
    <g id="orbital-body-amber">
{rings(False)}
      <circle r="20" fill="url(#orbital-amber)"/>
      <g clip-path="url(#orbital-amber-clip)">
      <g transform="rotate(-13)">
{chr(10).join(bands)}
        <path d="M -22 -4 C -13 0 -11 -4 -7 -1 S 1 4 5 1 S 15 4 22 0 M -21 7 C -11 9 -5 5 2 9 S 17 11 22 7" fill="none" stroke="#FFF0C9" stroke-opacity=".4" stroke-width=".65"/>
        <ellipse cx="7" cy="5" rx="5.2" ry="2.4" fill="#A7643D" opacity=".7"/>
        <ellipse cx="6.3" cy="4.7" rx="3.6" ry="1.3" fill="#DFB584"/>
        <path d="M 2 4 Q 7 1.7 11 5" fill="none" stroke="#FFE9C0" stroke-width=".6" opacity=".8"/>
      </g>
        <path d="M -24 3 Q -1 -1 23 -12" fill="none" stroke="#291D1A" stroke-width="3" opacity=".35"/>
      </g>
      <circle r="20" fill="url(#orbital-terminator)"/>
{rings(True)}
      <path d="M -17 -8 A 18.8 18.8 0 0 1 -7 -17" fill="none" stroke="#FFF3D2" opacity=".8" stroke-width=".8" stroke-linecap="round"/>
    </g>'''


def moon():
    craters = []
    for x,y,r,flatten in [(-5,-5,4.2,.87),(5,4.8,3.7,.86),(4.4,-9,2.3,.68),
                         (-9,5,2.7,.77),(10,-1,2,.7),(-1,10.7,1.4,.6),(-10,-7,1.4,.7)]:
        craters.append(f'''        <g transform="translate({x} {y}) scale(1 {flatten})">
          <circle r="{r+1}" fill="#D5DADB" opacity=".14"/>
          <circle r="{r}" fill="url(#orbital-crater)"/>
          <path d="M {-r*.93} 0 A {r} {r} 0 0 0 {r*.9} {r*.25}" fill="none" stroke="#EFF0DC" stroke-width=".7" opacity=".82"/>
          <path d="M {-r*.82} {-r*.1} A {r*.86} {r*.86} 0 0 1 {r*.72} {-r*.55}" fill="none" stroke="#304658" stroke-width=".6" opacity=".66"/>
          <circle cx=".4" cy=".45" r="{r*.22}" fill="#C6D0CA" opacity=".55"/>
        </g>''')
    return f'''
    <clipPath id="orbital-moon-clip"><circle r="16"/></clipPath>
    <g id="orbital-body-moon">
      <circle r="16" fill="url(#orbital-moon)"/>
      <g clip-path="url(#orbital-moon-clip)">
        <path d="M -15 -3 Q -6 -13 1 -7 T 13 -9 L 17 1 Q 9 0 3 8 T -13 13 Z" fill="#647D92" opacity=".24"/>
{chr(10).join(craters)}
        <path d="M -2 -16 Q 1 -10 -2 -6 M -14 0 L -10 2 M 7 10 L 9 13" fill="none" stroke="#E2DFCE" stroke-width=".5" opacity=".33"/>
      </g>
      <circle r="16" fill="url(#orbital-terminator)"/>
      <path d="M -13 -7 A 15 15 0 0 1 -6 -14" fill="none" stroke="#FFF5E1" stroke-width=".75" opacity=".8"/>
      <path d="M 5 15 A 16 16 0 0 0 14 6" fill="none" stroke="#9CAAD7" stroke-width=".65" opacity=".35"/>
    </g>'''


def ocean():
    land = ('M -12 -13 C -8 -15 -2 -12 -3 -9 S -7 -7 -5 -4 '
            'S 1 -5 1 -1 -4 1 -4 4 -7 5 -9 1 -14 -2 -12 -6 Z '
            'M 5 -2 C 9 -4 15 -1 16 3 S 12 8 11 10 7 15 4 12 '
            'S 5 8 2 6 3 1 5 -2 Z')
    return f'''
    <clipPath id="orbital-ocean-clip"><circle r="16"/></clipPath>
    <g id="orbital-body-ocean">
      <circle r="18" fill="url(#orbital-atmosphere)"/>
      <circle r="16" fill="url(#orbital-ocean)" stroke="#7ECDE9" stroke-width=".65" stroke-opacity=".65"/>
      <g clip-path="url(#orbital-ocean-clip)">
        <path d="{land}" transform="translate(.5 .6)" fill="#092F4B" opacity=".75"/>
        <path d="{land}" fill="url(#orbital-land)"/>
        <path d="M -11 -12 Q -6 -13 -4 -9 M 6 1 Q 11 0 13 4" fill="none" stroke="#D3DAB1" stroke-width=".65" opacity=".65"/>
        <g fill="none" stroke-linecap="round">
          <path d="M -18 -3 C -10 -8 -7 -1 0 -4 S 11 -10 18 -4 M -18 6 C -8 0 -5 8 2 5 S 9 3 17 8" transform="translate(.5 1)" stroke="#092C50" stroke-width="2" opacity=".4"/>
          <path d="M -18 -3 C -10 -8 -7 -1 0 -4 S 11 -10 18 -4 M -18 6 C -8 0 -5 8 2 5 S 9 3 17 8" stroke="#E4F4EF" stroke-width="1.6" opacity=".8"/>
          <path d="M -9 -12 C -3 -9 3 -14 9 -10 M -10 12 C -7 8 -2 10 3 12" stroke="#E6F8F6" stroke-width="1" opacity=".75"/>
          <path d="M 3 -4 C 9 -8 14 -4 10 -1 S 4 -1 7 -3" stroke="#F5FFFA" stroke-width=".7" opacity=".9"/>
        </g>
      </g>
      <circle r="16" fill="url(#orbital-terminator)"/>
      <ellipse cx="-6" cy="-9" rx="4" ry="2.3" transform="rotate(-30 -6 -9)" fill="url(#orbital-specular)" opacity=".65"/>
      <path d="M -13 -7 A 15.2 15.2 0 0 1 -6 -14" fill="none" stroke="#D0F5FF" stroke-width=".9" opacity=".85" stroke-linecap="round"/>
    </g>'''


def definitions(accent):
    return ('  <!-- orbital-definitions:start -->' + gradients(accent) + nucleus()
            + amber() + moon() + ocean() + '\n  <!-- orbital-definitions:end -->')
