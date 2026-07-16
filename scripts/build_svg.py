#!/usr/bin/env python3
"""Genera profile.svg: una ventana de terminal con neofetch + retrato ASCII a color.

Consume:
    portrait.json      (del portrait.py) -> ASCII a color, panel izquierdo
    profile_data.py    -> datos del neofetch, panel derecho

Salida:
    profile.svg        -> se embebe en el README con <img>

Uso:
    python scripts/build_svg.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

from profile_data import FOOTER, HOST, PROMPT_USER, SECTIONS, THEME, TITLE, USER

# --- Métricas de layout (en px) ---------------------------------------------
CHAR_W = 7.6          # ancho de glifo monoespaciado
LINE_H = 15           # alto de línea
PAD = 22              # padding interno
TITLEBAR_H = 34       # alto de la barra de título
ART_GAP = 26          # separación entre retrato y neofetch
FONT = "'JetBrains Mono','Fira Code','SF Mono',Consolas,monospace"


def load_grid() -> list[list[dict | None]]:
    return json.loads(Path("portrait.json").read_text(encoding="utf-8"))


def build_art_tspans(grid: list[list[dict | None]], x0: float, y0: float) -> tuple[str, float, float]:
    """Devuelve (svg, art_width_px, art_height_px) del retrato ASCII a color."""
    cols = max(len(r) for r in grid)
    lines = []
    for ri, row in enumerate(grid):
        y = y0 + ri * LINE_H
        spans = []
        # Agrupamos celdas contiguas del mismo color en un solo tspan (menos nodos).
        run_chars: list[str] = []
        run_color: str | None = None
        run_start_x = x0

        def flush(cx: float):
            if run_chars and run_color:
                text = escape("".join(run_chars))
                spans.append(
                    f'<tspan x="{cx:.1f}" y="{y:.1f}" fill="{run_color}">{text}</tspan>'
                )

        for ci in range(cols):
            cell = row[ci] if ci < len(row) else None
            color = cell["color"] if cell else None
            char = cell["char"] if cell else " "
            if color != run_color:
                flush(run_start_x)
                run_chars = []
                run_color = color
                run_start_x = x0 + ci * CHAR_W
            run_chars.append(char)
        flush(run_start_x)
        if spans:
            lines.append("".join(spans))
    art_w = cols * CHAR_W
    art_h = len(grid) * LINE_H
    return "\n".join(lines), art_w, art_h


def build_neofetch(x0: float, y0: float) -> tuple[str, float]:
    """Panel derecho: neofetch con datos reales. Devuelve (svg, height_px)."""
    out: list[str] = []
    y = y0
    label_w = 9  # caracteres reservados para la etiqueta

    # Encabezado: user@host
    out.append(
        f'<tspan x="{x0:.1f}" y="{y:.1f}">'
        f'<tspan fill="{THEME["accent"]}" font-weight="bold">{USER}</tspan>'
        f'<tspan fill="{THEME["fg"]}">@</tspan>'
        f'<tspan fill="{THEME["accent"]}" font-weight="bold">{HOST}</tspan>'
        f"</tspan>"
    )
    y += LINE_H
    out.append(
        f'<tspan x="{x0:.1f}" y="{y:.1f}" fill="{THEME["dim"]}">'
        + escape("-" * 26)
        + "</tspan>"
    )
    y += LINE_H * 1.4

    for si, section in enumerate(SECTIONS):
        header = section["header"]
        out.append(
            f'<tspan x="{x0:.1f}" y="{y:.1f}" fill="{THEME["magenta"]}" font-weight="bold">'
            + escape(header)
            + "</tspan>"
        )
        y += LINE_H
        for label, value in section["rows"]:
            pad_label = (label + " " * label_w)[:label_w]
            out.append(
                f'<tspan x="{x0:.1f}" y="{y:.1f}">'
                f'<tspan fill="{THEME["cyan"]}">{escape(pad_label)}</tspan>'
                f'<tspan fill="{THEME["fg"]}">{escape(value)}</tspan>'
                f"</tspan>"
            )
            y += LINE_H
        if si < len(SECTIONS) - 1:
            y += LINE_H * 0.5

    y += LINE_H * 0.8
    out.append(
        f'<tspan x="{x0:.1f}" y="{y:.1f}" fill="{THEME["accent"]}">'
        + escape(FOOTER)
        + "</tspan>"
    )
    y += LINE_H * 1.6
    ts = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    out.append(
        f'<tspan x="{x0:.1f}" y="{y:.1f}" fill="{THEME["dim"]}">'
        + escape(f"last updated {ts}")
        + "</tspan>"
    )
    return "\n".join(out), y - y0 + LINE_H


def build_svg() -> str:
    grid = load_grid()

    art_x = PAD
    art_y = TITLEBAR_H + PAD + LINE_H
    art_svg, art_w, art_h = build_art_tspans(grid, art_x, art_y)

    neo_x = art_x + art_w + ART_GAP
    neo_svg, neo_h = build_neofetch(neo_x, art_y)

    # Ancho del neofetch (aprox por la línea más larga).
    max_chars = 0
    for section in SECTIONS:
        for label, value in section["rows"]:
            max_chars = max(max_chars, 9 + len(value))
    max_chars = max(max_chars, len("last updated 00 Xxx 0000, 00:00 UTC"))
    neo_w = max_chars * CHAR_W

    width = int(neo_x + neo_w + PAD)
    body_h = max(art_h, neo_h)
    height = int(TITLEBAR_H + PAD + LINE_H + body_h + PAD)

    total_lines = len(grid)
    type_dur = 2.6  # segundos del efecto typing

    prompt_y = TITLEBAR_H + PAD + LINE_H * 0.2
    reveal_w = width - 2 * PAD

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}" font-family="{FONT}" font-size="12.5">
  <defs>
    <clipPath id="reveal">
      <rect x="0" y="0" width="0" height="{height}">
        <animate attributeName="width" from="0" to="{width}"
                 dur="{type_dur}s" fill="freeze" calcMode="spline"
                 keySplines="0.22 1 0.36 1" begin="0.3s"/>
      </rect>
    </clipPath>
    <linearGradient id="titlebar" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#20262e"/>
      <stop offset="1" stop-color="{THEME['titlebar']}"/>
    </linearGradient>
  </defs>

  <!-- ventana -->
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10"
        fill="{THEME['bg']}" stroke="{THEME['border']}" stroke-width="1"/>
  <path d="M10 0.5 H{width - 10} A9.5 9.5 0 0 1 {width - 0.5} 10 V{TITLEBAR_H}
           H0.5 V10 A9.5 9.5 0 0 1 10 0.5 Z" fill="url(#titlebar)"/>
  <line x1="0.5" y1="{TITLEBAR_H}" x2="{width - 0.5}" y2="{TITLEBAR_H}"
        stroke="{THEME['border']}" stroke-width="1"/>

  <!-- botones -->
  <circle cx="20" cy="{TITLEBAR_H / 2}" r="6" fill="{THEME['close']}"/>
  <circle cx="40" cy="{TITLEBAR_H / 2}" r="6" fill="{THEME['min']}"/>
  <circle cx="60" cy="{TITLEBAR_H / 2}" r="6" fill="{THEME['max']}"/>
  <text x="{width / 2}" y="{TITLEBAR_H / 2 + 4}" text-anchor="middle"
        fill="{THEME['dim']}" font-size="12">{escape(TITLE)} — zsh</text>

  <!-- prompt -->
  <text x="{PAD}" y="{prompt_y + LINE_H}" fill="{THEME['fg']}">
    <tspan fill="{THEME['accent']}" font-weight="bold">➜</tspan>
    <tspan fill="{THEME['cyan']}" dx="6">~</tspan>
    <tspan fill="{THEME['fg']}" dx="6">neofetch --profile</tspan>
  </text>

  <!-- contenido revelado con efecto typing -->
  <g clip-path="url(#reveal)">
    <text xml:space="preserve">
{art_svg}
    </text>
    <text xml:space="preserve">
{neo_svg}
    </text>
  </g>

  <!-- cursor parpadeante al final -->
  <rect x="{PAD}" y="{height - PAD - LINE_H + 2}" width="8" height="15"
        fill="{THEME['accent']}" opacity="0">
    <animate attributeName="opacity" values="0;0;1;1;0;0" dur="1s"
             begin="{type_dur + 0.3}s" repeatCount="indefinite"/>
  </rect>
</svg>
'''


def main() -> None:
    svg = build_svg()
    Path("profile.svg").write_text(svg, encoding="utf-8")
    print(f"OK -> profile.svg ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
