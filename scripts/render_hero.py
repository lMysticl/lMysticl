"""Generate the editorial profile cover in two themes and viewport sizes."""

from pathlib import Path


ASSETS = Path(__file__).resolve().parents[1] / "assets"
PALETTES = {
    "dark": {
        "bg_a": "#111318", "bg_b": "#20242B", "border": "#373B41",
        "text": "#F8F5EF", "muted": "#D5D0C7", "quiet": "#A9AAA8",
        "line": "#62615D", "accent": "#E9B47A", "glow": "#BE8751",
    },
    "light": {
        "bg_a": "#FAF7F0", "bg_b": "#EEE9E0", "border": "#D8D0C5",
        "text": "#202124", "muted": "#4E4D49", "quiet": "#64635E",
        "line": "#A9A096", "accent": "#9E562E", "glow": "#D6B18B",
    },
}


def base(width: int, height: int, c: dict[str, str], title: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">Pavel Putrenkov, Senior Java Engineer. Complex inputs, clear outcomes.</desc>
  <defs>
    <linearGradient id="background" x2="1" y2="1"><stop stop-color="{c['bg_a']}"/><stop offset="1" stop-color="{c['bg_b']}"/></linearGradient>
    <radialGradient id="glow"><stop stop-color="{c['glow']}" stop-opacity=".16"/><stop offset="1" stop-color="{c['glow']}" stop-opacity="0"/></radialGradient>
    <linearGradient id="streak"><stop stop-color="{c['accent']}" stop-opacity="0"/><stop offset=".5" stop-color="{c['accent']}"/><stop offset="1" stop-color="{c['accent']}" stop-opacity="0"/></linearGradient>
    <style>text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; }} text.monogram {{ font-family: Georgia, "Times New Roman", serif; }} @media (prefers-reduced-motion: reduce) {{ .motion {{ display: none; }} }}</style>
  </defs>
  <rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="18" fill="url(#background)" stroke="{c['border']}"/>
'''


def moving_streak(c: dict[str, str], x: int, y: int, end: int, width: int, seconds: int) -> str:
    return f'''  <g class="motion">
    <rect x="{x}" y="{y - 2}" width="{width}" height="4" rx="2" fill="url(#streak)" opacity="0">
      <animate attributeName="x" values="{x};{end - width};{end - width}" keyTimes="0;.55;1" dur="{seconds}s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;.9;.9;0;0" keyTimes="0;.07;.47;.56;1" dur="{seconds}s" repeatCount="indefinite"/>
    </rect>
  </g>
'''


def desktop(c: dict[str, str], animated: bool) -> str:
    return base(1200, 430, c, "Pavel Putrenkov — complex inputs, clear outcomes") + f'''
  <circle cx="997" cy="195" r="260" fill="url(#glow)"/>
  <circle cx="995" cy="211" r="154" fill="none" stroke="{c['accent']}" stroke-opacity=".42" stroke-width="1.5"/>
  <circle cx="995" cy="211" r="122" fill="none" stroke="{c['line']}" stroke-opacity=".45"/>
  <text class="monogram" x="890" y="311" fill="{c['accent']}" fill-opacity=".20" font-size="285" font-style="italic">P</text>
  <circle cx="1095" cy="304" r="13" fill="{c['accent']}"/>
  <rect x="60" y="47" width="38" height="4" rx="2" fill="{c['accent']}"/>
  <text x="111" y="52" fill="{c['accent']}" font-size="18" font-weight="700" letter-spacing="2">SENIOR JAVA ENGINEER · SPRING BOOT</text>
  <text x="60" y="133" fill="{c['text']}" font-size="58" font-weight="700">Pavel Putrenkov</text>
  <text x="60" y="221" fill="{c['text']}" font-size="62" font-weight="700">Complex inputs.</text>
  <text x="60" y="291" fill="{c['accent']}" font-size="62" font-weight="700">Clear outcomes.</text>
  <text x="60" y="339" fill="{c['muted']}" font-size="21">Payments, documents and dependable APIs.</text>
  <line x1="60" y1="377" x2="1140" y2="377" stroke="{c['line']}" stroke-opacity=".65"/>
{moving_streak(c, 60, 377, 1140, 138, 9) if animated else ""}  <text x="60" y="409" fill="{c['quiet']}" font-size="16" font-weight="600" letter-spacing="1.5">PAYMENTS  /  DOCUMENTS  /  DEVELOPER TOOLING</text>
</svg>
'''


def mobile(c: dict[str, str], animated: bool) -> str:
    return base(620, 580, c, "Pavel Putrenkov — Senior Java Engineer") + f'''
  <circle cx="510" cy="461" r="160" fill="url(#glow)"/>
  <circle cx="505" cy="447" r="110" fill="none" stroke="{c['accent']}" stroke-opacity=".34" stroke-width="1.5"/>
  <text class="monogram" x="432" y="520" fill="{c['accent']}" fill-opacity=".18" font-size="205" font-style="italic">P</text>
  <circle cx="573" cy="525" r="9" fill="{c['accent']}"/>
  <rect x="34" y="39" width="34" height="4" rx="2" fill="{c['accent']}"/>
  <text x="81" y="45" fill="{c['accent']}" font-size="22" font-weight="700" letter-spacing="1">SENIOR JAVA · SPRING BOOT</text>
  <text x="34" y="130" fill="{c['text']}" font-size="59" font-weight="700">Pavel Putrenkov</text>
  <text x="34" y="218" fill="{c['text']}" font-size="54" font-weight="700">Complex inputs.</text>
  <text x="34" y="282" fill="{c['accent']}" font-size="54" font-weight="700">Clear outcomes.</text>
  <text x="34" y="339" fill="{c['muted']}" font-size="25">Reliable systems for payments,</text>
  <text x="34" y="375" fill="{c['muted']}" font-size="25">documents and developer tools.</text>
  <line x1="34" y1="491" x2="586" y2="491" stroke="{c['line']}" stroke-opacity=".65"/>
{moving_streak(c, 34, 491, 586, 90, 8) if animated else ""}  <text x="34" y="539" fill="{c['quiet']}" font-size="22" font-weight="600" letter-spacing="1">PAYMENTS  /  DOCS  /  TOOLING</text>
</svg>
'''


def main() -> None:
    for theme, colors in PALETTES.items():
        for size, render in (("", desktop), ("mobile-", mobile)):
            for kind, animated in (("animated", True), ("static", False)):
                svg = render(colors, animated)
                path = ASSETS / f"profile-cover-2026-{kind}-{size}{theme}.svg"
                path.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
