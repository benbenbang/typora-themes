"""Catppuccin -> Typora.

Palette roles: base/mantle/crust darken in every flavor (Latte included), so a
single mapping covers all four with no light/dark special-casing.
"""

# standard library
from typing import cast

# typora themes tools
from typora_themes.colors import pick_mark, rgba

NAME = "Catppuccin"
PALETTE_URL = "https://catppuccin.com/palette"
PALETTE_FILE = "catppuccin.json"
OUT_DIR = "catppuccin"
ASSET_DIR = "catppuccin"  # font folder name inside Typora's themes dir
ACCENT = "mauve"
FLAVORS = ("latte", "frappe", "macchiato", "mocha")

PALETTE = None  # injected by build.py


def variants():
    for key in FLAVORS:
        f = cast(dict, PALETTE)[key]
        yield {
            "key": key,
            "id": f"catppuccin-{key}",
            "name": f["name"],
            "dark": f["dark"],
            "colors": {
                n: c["hex"]
                for n, c in sorted(f["colors"].items(), key=lambda kv: kv[1]["order"])
            },
        }


def variables(v):
    c = v["colors"]
    accent = c[ACCENT]

    # A pure-black drop shadow reads as grime on Latte; tint it instead.
    if v["dark"]:
        shadow_weak, shadow_strong = "rgba(0, 0, 0, 0.2)", "rgba(0, 0, 0, 0.5)"
    else:
        shadow_weak = rgba(c["overlay0"], 0.25)
        shadow_strong = rgba(c["overlay0"], 0.45)

    mark_bg, mark_fg, _, _ = pick_mark(
        c["yellow"], c["base"], [c["crust"], c["base"], c["text"]]
    )

    out = {f"--ctp-{name}": hex_ for name, hex_ in c.items()}
    out.update(
        {
            "--accent-color": accent,
            "--font-mono": '"Fira Code", "FiraCode Nerd Font", "FuraCode Nerd Font", ui-monospace, '
            '"SF Mono", Menlo, Consolas, "DejaVu Sans Mono", monospace',
            # backgrounds
            "--bg-color1": c["base"],
            "--bg-color2": c["mantle"],
            "--bg-color3": c["crust"],
            "--bg-color4": c["crust"],
            "--bg-color5": c["surface0"],
            # Code sits on mantle: overlay comments hit 1.7:1 on surface0 in
            # Latte. Definition comes from the border, not the fill.
            "--code-bg-color": c["mantle"],
            "--code-border-color": c["surface0"],
            # text
            "--text-color1": c["text"],
            "--text-color2": c["subtext1"],
            "--text-color3": c["overlay0"],
            "--text-color4": c["text"],
            "--text-color5": c["overlay0"],
            "--link-color": accent,
            # table
            "--table-border-color": c["surface1"],
            "--table-thead-color": c["surface0"],
            "--table-bg-color": c["base"],
            "--table-bg-darker-color": c["mantle"],
            # hover / active
            "--hover-bg-color1": c["surface1"],
            "--hover-bg-color2": c["surface0"],
            "--hover-bg-color3": rgba(c["surface1"], 0.8),
            "--hover-text-color": c["text"],
            "--active-color": c["surface1"],
            "--input-color": c["mantle"],
            "--menu-divider-color": c["surface1"],
            "--scrollbar-thumb-color": c["surface2"],
            "--scrollbar-track-color": rgba(c["surface0"], 0.5),
            "--theme-select-color": accent,
            "--button-color": c["surface1"],
            "--select-color": c["surface0"],
            "--focus-color": rgba(accent, 0.6),
            "--focus-ring-color": rgba(accent, 0.6),
            # syntax
            "--code-red-color": c["red"],
            "--code-yellow-color": c["yellow"],
            "--code-cyan-color": c["teal"],
            "--code-blue-color": c["blue"],
            "--code-purple-color": c["mauve"],
            "--code-orange-color": c["peach"],
            "--code-grey-color": c["overlay2"],
            "--code-green-color": c["green"],
            "--code-operator-color": c["sky"],
            "--code-bracket-color": c["overlay2"],
            "--code-variable2-color": c["lavender"],
            "--code-select-bg-color": c["surface1"],
            "--code-cursor-color": c["rosewater"],
            "--select-text-bg-color": c["surface2"],
            "--search-select-bg-color": rgba(accent, 0.3),
            "--mark-bg-color": mark_bg,
            "--mark-text-color": mark_fg,
            "--shadow-weak": shadow_weak,
            "--shadow-strong": shadow_strong,
            "--danger-color": c["red"],
            "--danger-text-color": c["base"],
            "--backdrop-color": c["crust"],
            # table-insert grid board
            "--grid-thread-filled-color": c["surface2"],
            "--grid-thread-empty-color": c["surface0"],
            "--grid-filled-color": c["overlay0"],
            # mermaid gantt
            "--gantt-section-a-color": c["mantle"],
            "--gantt-section-b-color": c["base"],
            "--gantt-task-color": c["surface1"],
            "--gantt-active-color": c["surface2"],
            "--gantt-done-color": c["surface0"],
            "--gantt-crit-color": c["red"],
            "--gantt-active-crit-color": c["peach"],
            "--gantt-done-crit-color": c["maroon"],
            "--gantt-grid-text-color": c["subtext0"],
            "--gantt-today-color": c["red"],
            # Typora implicit names
            "--primary-color": c["surface1"],
            "--primary-btn-border-color": "transparent",
            "--primary-btn-text-color": c["subtext1"],
            "--side-bar-bg-color": c["mantle"],
            "--control-text-color": c["subtext1"],
            "--control-text-hover-color": c["text"],
            "--text-color": c["text"],
            "--bg-color": c["base"],
            "--item-hover-bg-color": c["surface1"],
            "--item-hover-text-color": c["text"],
            "--active-file-bg-color": c["surface1"],
            "--active-file-text-color": c["text"],
            "--active-file-border-color": accent,
            "--rawblock-edit-panel-bd": c["surface0"],
            "--blur-text-color": c["overlay0"],
            "--node-border": c["surface1"],
            "--node-fill": c["mantle"],
        }
    )
    return out
