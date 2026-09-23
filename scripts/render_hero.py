"""Generate the four self-contained, theme-aware profile hero SVGs."""

from pathlib import Path


ASSETS = Path(__file__).resolve().parents[1] / "assets"
THEMES = {
    "dark": {
        "bg_a": "#0B1220", "bg_b": "#12263A", "grid": "#37526B",
        "border": "#344B61", "text": "#F5F9FC", "muted": "#C6D5E2",
        "subtle": "#9FB6C7", "aqua": "#74E5D4", "blue": "#83BFFF",
        "panel": "#142539", "panel_border": "#456077", "glow": "#2C7A87",
    },
    "light": {
        "bg_a": "#F7FAFF", "bg_b": "#E8F3F6", "grid": "#9FC4D1",
        "border": "#C5D7E1", "text": "#102536", "muted": "#375569",
        "subtle": "#4C697B", "aqua": "#087C71", "blue": "#075DA8",
        "panel": "#FFFFFF", "panel_border": "#BED0DA", "glow": "#AADFD9",
    },
}


def base(width: int, height: int, c: dict[str, str], title: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">Java and Spring backend systems for PDF processing and multi-source APIs.</desc>
  <defs>
    <linearGradient id="background" x2="1" y2="1"><stop stop-color="{c['bg_a']}"/><stop offset="1" stop-color="{c['bg_b']}"/></linearGradient>
    <radialGradient id="glow"><stop stop-color="{c['glow']}" stop-opacity=".42"/><stop offset="1" stop-color="{c['glow']}" stop-opacity="0"/></radialGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M 32 0 L 0 0 0 32" fill="none" stroke="{c['grid']}" stroke-opacity=".15"/></pattern>
    <style>text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; }}</style>
  </defs>
  <rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="22" fill="url(#background)" stroke="{c['border']}"/>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="21" fill="url(#grid)"/>
'''


def desktop(c: dict[str, str]) -> str:
    return base(1200, 380, c, "Pavel Putrenkov — reliable software for complex data") + f'''
  <circle cx="1020" cy="100" r="265" fill="url(#glow)"/>
  <rect x="48" y="42" width="46" height="5" rx="2.5" fill="{c['aqua']}"/>
  <text x="106" y="49" fill="{c['aqua']}" font-size="18" font-weight="700" letter-spacing="2">JAVA / SPRING · DOCUMENT SYSTEMS</text>
  <text x="48" y="125" fill="{c['text']}" font-size="56" font-weight="750">Pavel Putrenkov</text>
  <text x="48" y="197" fill="{c['text']}" font-size="48" font-weight="700">Reliable software</text>
  <text x="48" y="251" fill="{c['aqua']}" font-size="48" font-weight="700">for complex data.</text>
  <text x="48" y="300" fill="{c['muted']}" font-size="20">PDF analysis · multi-source APIs · clear contracts</text>
  <line x1="48" y1="331" x2="753" y2="331" stroke="{c['border']}"/>
  <text x="48" y="357" fill="{c['subtle']}" font-size="17" font-weight="600" letter-spacing="1">JAVA 21  /  SPRING BOOT  /  PDFBOX</text>
  <rect x="804" y="40" width="344" height="298" rx="19" fill="{c['panel']}" stroke="{c['panel_border']}"/>
  <text x="833" y="75" fill="{c['subtle']}" font-size="16" font-weight="700" letter-spacing="1.7">FROM INPUT TO EVIDENCE</text>
  <line x1="847" y1="114" x2="847" y2="281" stroke="{c['panel_border']}" stroke-width="2"/>
  <circle cx="847" cy="116" r="6" fill="{c['aqua']}"/>
  <circle cx="847" cy="195" r="6" fill="{c['blue']}"/>
  <circle cx="847" cy="274" r="6" fill="{c['aqua']}"/>
  <text x="872" y="111" fill="{c['subtle']}" font-size="15" font-weight="700" letter-spacing="1">01 / DOCUMENTS</text>
  <text x="872" y="139" fill="{c['text']}" font-size="21" font-weight="650">PDF → usable text</text>
  <text x="872" y="190" fill="{c['subtle']}" font-size="15" font-weight="700" letter-spacing="1">02 / DATA SOURCES</text>
  <text x="872" y="218" fill="{c['text']}" font-size="21" font-weight="650">SQL + Mongo → API</text>
  <text x="872" y="269" fill="{c['subtle']}" font-size="15" font-weight="700" letter-spacing="1">03 / DELIVERY</text>
  <text x="872" y="297" fill="{c['text']}" font-size="21" font-weight="650">Test → release</text>
</svg>
'''


def mobile(c: dict[str, str]) -> str:
    return base(620, 550, c, "Pavel Putrenkov — Java and Spring backend engineer") + f'''
  <circle cx="530" cy="110" r="195" fill="url(#glow)"/>
  <rect x="34" y="36" width="40" height="5" rx="2.5" fill="{c['aqua']}"/>
  <text x="84" y="43" fill="{c['aqua']}" font-size="22" font-weight="700" letter-spacing="1">JAVA / SPRING · DOCUMENTS</text>
  <text x="34" y="126" fill="{c['text']}" font-size="59" font-weight="750">Pavel Putrenkov</text>
  <text x="34" y="212" fill="{c['text']}" font-size="50" font-weight="700">Reliable software</text>
  <text x="34" y="269" fill="{c['aqua']}" font-size="50" font-weight="700">for complex data.</text>
  <text x="34" y="318" fill="{c['muted']}" font-size="26">PDF analysis · multi-source APIs</text>
  <line x1="34" y1="354" x2="586" y2="354" stroke="{c['border']}"/>
  <rect x="34" y="376" width="552" height="67" rx="12" fill="{c['panel']}" stroke="{c['panel_border']}"/>
  <rect x="34" y="457" width="552" height="67" rx="12" fill="{c['panel']}" stroke="{c['panel_border']}"/>
  <circle cx="64" cy="410" r="7" fill="{c['aqua']}"/>
  <circle cx="64" cy="490" r="7" fill="{c['blue']}"/>
  <text x="86" y="417" fill="{c['text']}" font-size="26" font-weight="650">PDF → usable text</text>
  <text x="86" y="498" fill="{c['text']}" font-size="26" font-weight="650">SQL + Mongo → one API</text>
</svg>
'''


def main() -> None:
    for theme, colors in THEMES.items():
        (ASSETS / f"profile-hero-2026-{theme}.svg").write_text(desktop(colors), encoding="utf-8")
        (ASSETS / f"profile-hero-2026-mobile-{theme}.svg").write_text(mobile(colors), encoding="utf-8")


if __name__ == "__main__":
    main()
