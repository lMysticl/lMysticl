"""Shared palette and rendered 3D sprite definitions.

Original geometry, procedural materials and credited NASA surface maps are
rendered by render_profile_3d.py.
Self-contained PNG image elements retain detail inside GitHub SVG image contexts.
"""

CORE_RADIUS = 105
MIDNIGHT = '#081629'
CHAMPAGNE = '#F2CC8F'
TURQUOISE = '#65D6CE'
PERIWINKLE = '#B6ACEF'
ORBIT_COLORS = {
    'amber': (CHAMPAGNE, '#AD753B'),
    'moon': (PERIWINKLE, '#7C70A8'),
    'ocean': (TURQUOISE, '#277F88'),
}

def definitions():
    import base64
    from pathlib import Path
    sprites = Path(__file__).resolve().parents[1] / 'assets' / 'planets-3d'
    parts = ['  <!-- orbital-definitions:start -->',
        '<radialGradient id="orbital-aura"><stop stop-color="#70B8FF" stop-opacity=".18"/><stop offset=".55" stop-color="#70B8FF" stop-opacity=".04"/><stop offset="1" stop-color="#70B8FF" stop-opacity="0"/></radialGradient>']
    for name, ident, extent in [('core','orbital-nucleus',CORE_RADIUS*2.42),('amber','orbital-body-amber',83.6),('moon','orbital-body-moon',35.52),('ocean','orbital-body-ocean',36.48)]:
        encoded = base64.b64encode((sprites/(name+'.png')).read_bytes()).decode('ascii')
        parts.append(f'<image id="{ident}" x="{-extent/2}" y="{-extent/2}" width="{extent}" height="{extent}" href="data:image/png;base64,{encoded}"/>')
    parts.append('  <!-- orbital-definitions:end -->')
    return '\n'.join(parts)
