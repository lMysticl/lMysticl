"""Shared palette, source P outline and rendered 3D sprite definitions.

Original geometry, procedural materials and credited NASA surface maps are
rendered by render_profile_3d.py.
Self-contained PNG image elements retain detail inside GitHub SVG image contexts.
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
LETTER = ('M -46 62 L -45 57 C -33 56 -29 53 -27 42 L -10 -43 '
          'C -8 -55 -11 -58 -23 -58 L -22 -64 H 23 '
          'C 48 -64 63 -54 63 -35 C 63 -9 41 8 12 8 H 4 '
          'L -2 42 C -4 53 0 57 14 57 L 13 62 Z '
          'M 8 -4 H 18 C 37 -4 48 -16 48 -34 '
          'C 48 -47 41 -53 27 -53 H 17 Z')

def definitions(accent):
    import base64
    from pathlib import Path
    sprites = Path(__file__).resolve().parents[1] / 'assets' / 'planets-3d'
    parts = ['  <!-- orbital-definitions:start -->',
        f'<radialGradient id="orbital-aura"><stop stop-color="{accent}" stop-opacity=".24"/><stop offset=".55" stop-color="{accent}" stop-opacity=".07"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>']
    for name, ident, extent in [('core','orbital-nucleus',217.8),('amber','orbital-body-amber',83.6),('moon','orbital-body-moon',35.52),('ocean','orbital-body-ocean',36.48)]:
        encoded = base64.b64encode((sprites/(name+'.png')).read_bytes()).decode('ascii')
        parts.append(f'<image id="{ident}" x="{-extent/2}" y="{-extent/2}" width="{extent}" height="{extent}" href="data:image/png;base64,{encoded}"/>')
    parts.append('  <!-- orbital-definitions:end -->')
    return '\n'.join(parts)
