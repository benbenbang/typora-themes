#!/usr/bin/env python3
"""Generate the four Catppuccin Typora themes from the canonical palette.

    python3 catppuccin/tools/generate.py

Reads tools/template.css and tools/palette.json, writes catppuccin-<flavor>.css.
To track an upstream palette change, replace tools/palette.json and re-run.
"""

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent

# catppuccin/palette @ this blob; bump alongside tools/palette.json
PALETTE_SHA = "2a5d25cb0b00033bb049d11ab12c8bed478bf4e8"
ACCENT = "mauve"
FLAVORS = ("latte", "frappe", "macchiato", "mocha")


def rgba(color, alpha):
    c = color["rgb"]
    return f"rgba({c['r']}, {c['g']}, {c['b']}, {alpha})"


def luminance(hex_):
    def chan(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = (int(hex_[i : i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def blend(fg_hex, bg_hex, alpha):
    """Composite fg over bg at alpha, returning an opaque hex."""
    out = []
    for i in (1, 3, 5):
        f, b = int(fg_hex[i : i + 2], 16), int(bg_hex[i : i + 2], 16)
        out.append(round(f * alpha + b * (1 - alpha)))
    return "#{:02x}{:02x}{:02x}".format(*out)


def pick_mark(colors, candidates=("crust", "base", "text")):
    """Strongest yellow tint that still carries a palette foreground at 4.5:1.

    Latte's yellow is a mid-tone mustard: nothing in the palette clears AA on it
    at full strength (best is 3.05:1), so the tint is blended toward base until
    it does. The dark flavors' yellows are pale and pass at full strength.
    """
    yellow, base = colors["yellow"]["hex"], colors["base"]["hex"]
    for step in range(20, 3, -1):  # alpha 1.00 -> 0.20
        alpha = step / 20
        bg = blend(yellow, base, alpha)
        fg = max(candidates, key=lambda k: contrast(colors[k]["hex"], bg))
        if contrast(colors[fg]["hex"], bg) >= 4.5:
            return bg, fg, alpha, contrast(colors[fg]["hex"], bg)
    raise AssertionError("no accessible mark tint found")


def main():
    palette = json.loads((HERE / "palette.json").read_text())
    template = (HERE / "template.css").read_text()

    for key in FLAVORS:
        flavor = palette[key]
        colors = flavor["colors"]

        # Emit in the palette's own order, not dict order: pre-commit's
        # pretty-format-json sorts keys, which would otherwise reshuffle every
        # generated file whenever palette.json is reformatted.
        ordered = sorted(colors.items(), key=lambda kv: kv[1]["order"])
        palette_vars = "\n".join(f"    --ctp-{name}: {c['hex']};" for name, c in ordered)

        # A pure-black drop shadow reads as grime on Latte; tint it instead.
        if flavor["dark"]:
            shadow_weak, shadow_strong = "rgba(0, 0, 0, 0.2)", "rgba(0, 0, 0, 0.5)"
        else:
            shadow_weak = rgba(colors["overlay0"], 0.25)
            shadow_strong = rgba(colors["overlay0"], 0.45)

        mark_bg, mark_fg, mark_alpha, mark_ratio = pick_mark(colors)

        css = template
        for token, value in {
            "{FLAVOR_NAME}": flavor["name"],
            "{PALETTE_SHA}": PALETTE_SHA[:12],
            "{ACCENT_NAME}": colors[ACCENT]["name"],
            "{ACCENT_KEY}": ACCENT,
            "{PALETTE_VARS}": palette_vars,
            "{MARK_BG}": mark_bg,
            "{MARK_FG_KEY}": mark_fg,
            "{SURFACE1_A80}": rgba(colors["surface1"], 0.8),
            "{SURFACE0_A50}": rgba(colors["surface0"], 0.5),
            "{ACCENT_A60}": rgba(colors[ACCENT], 0.6),
            "{ACCENT_A30}": rgba(colors[ACCENT], 0.3),
            "{SHADOW_WEAK}": shadow_weak,
            "{SHADOW_STRONG}": shadow_strong,
        }.items():
            css = css.replace(token, value)

        dest = OUT / f"catppuccin-{key}.css"
        dest.write_text(css)
        print(
            f"{dest.name:28} {len(css):>6} bytes  "
            f"mark={mark_bg} on {mark_fg:5} a={mark_alpha:.2f} {mark_ratio:.2f}:1"
        )


if __name__ == "__main__":
    main()
