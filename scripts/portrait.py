#!/usr/bin/env python3
"""Convierte una imagen (pixel-art / foto) en ASCII art a color.

Pipeline:
    pixel-art.png -> [resize + aspect fix] -> por bloque:
        luminancia -> caracter ASCII
        color RGB   -> se guarda para pintar en el SVG

Salidas:
    portrait.txt  -> ASCII monocromo (preview / fallback)
    portrait.json -> [{char, color}] por celda, consumido por build_svg.py

Uso:
    python scripts/portrait.py assets/pixel-art.png --width 62
"""
from __future__ import annotations

import argparse
import colorsys
import json
from pathlib import Path

from PIL import Image, ImageEnhance

# Rampa de densidad: de más oscuro (denso) a más claro (vacío).
# Menos caracteres = más "aireado" y legible en el retrato.
RAMP = "@%#*+=-:. "

# Los glifos de terminal miden ~2x de alto que de ancho.
# Compensamos muestreando las filas a la mitad para no estirar la cara.
CELL_ASPECT = 0.5


def luminance(r: int, g: int, b: int) -> float:
    """Luminancia percibida (Rec. 601). El ojo ve el verde más brillante."""
    return 0.299 * r + 0.587 * g + 0.114 * b


def is_background(r: int, g: int, b: int) -> bool:
    """El fondo del retrato es gris muy claro y casi neutro.

    Un pixel es fondo si es claro Y sus canales están muy juntos (sin croma).
    Así recortamos el fondo sin comerse la camisa clara ni la piel.
    """
    brightest = max(r, g, b)
    spread = brightest - min(r, g, b)
    return brightest > 205 and spread < 18


def punch_color(r: int, g: int, b: int) -> tuple[int, int, int]:
    """Empuja el color hacia su tono dominante para que no se vea lavado.

    Al reducir la imagen, muchos bloques promedian con el fondo y pierden
    saturación. Aquí ponemos un piso: si el pixel tiene algo de croma, lo
    saturamos para que la camisa verde y el pelo lean como tales en el SVG.
    """
    rn, gn, bn = r / 255, g / 255, b / 255
    h, s, v = colorsys.rgb_to_hsv(rn, gn, bn)
    if s > 0.08:  # solo si hay color real (no gris puro)
        s = min(1.0, s * 1.55 + 0.08)
    rn, gn, bn = colorsys.hsv_to_rgb(h, s, v)
    return round(rn * 255), round(gn * 255), round(bn * 255)


def to_ascii(image_path: Path, width: int) -> list[list[dict[str, str] | None]]:
    """Devuelve una grilla de celdas. Cada celda es {char, color} o None (fondo)."""
    img = Image.open(image_path).convert("RGB")

    # Preprocesado: subir saturación y contraste ANTES de reducir,
    # para que los colores del pixel-art sobrevivan al downsampling.
    img = ImageEnhance.Color(img).enhance(1.5)
    img = ImageEnhance.Contrast(img).enhance(1.18)
    src_w, src_h = img.size

    height = max(1, int(width * (src_h / src_w) * CELL_ASPECT))
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    pixels = img.load()

    grid: list[list[dict[str, str] | None]] = []
    for y in range(height):
        row: list[dict[str, str] | None] = []
        for x in range(width):
            r, g, b = pixels[x, y]
            if is_background(r, g, b):
                row.append(None)
                continue
            lum = luminance(r, g, b)
            idx = int((lum / 255) * (len(RAMP) - 1))
            cr, cg, cb = punch_color(r, g, b)
            row.append({"char": RAMP[idx], "color": f"#{cr:02x}{cg:02x}{cb:02x}"})
        grid.append(row)
    return grid


def render_txt(grid: list[list[dict[str, str] | None]]) -> str:
    lines = []
    for row in grid:
        lines.append("".join(cell["char"] if cell else " " for cell in row))
    return "\n".join(line.rstrip() for line in lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Imagen -> ASCII art a color.")
    parser.add_argument("image", type=Path, help="Ruta a la imagen de origen.")
    parser.add_argument("--width", type=int, default=62, help="Ancho en caracteres.")
    parser.add_argument("--out-dir", type=Path, default=Path("."), help="Directorio de salida.")
    args = parser.parse_args()

    grid = to_ascii(args.image, args.width)

    txt_path = args.out_dir / "portrait.txt"
    json_path = args.out_dir / "portrait.json"

    txt_path.write_text(render_txt(grid), encoding="utf-8")
    json_path.write_text(json.dumps(grid, ensure_ascii=False), encoding="utf-8")

    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    print(f"OK -> {txt_path} y {json_path}  ({cols}x{rows} celdas)")


if __name__ == "__main__":
    main()
