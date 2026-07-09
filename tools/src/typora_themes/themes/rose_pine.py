"""Rose Pine -> Typora.

Mapped from the upstream role table, not by eye:

    base/surface/overlay  background, ascending contrast
    muted                 comments
    subtle                punctuation, operators
    text                  high-contrast foreground
    highlightLow/Med/High cursor line / selection bg / borders + cursor
    love gold rose pine foam iris
                          errors+builtins, strings, booleans, functions,
                          object keys, links+parameters

Unlike Catppuccin, the ramp direction is not uniform: on the dark variants
surface and overlay are *lighter* than base, while on Dawn surface is lighter
but overlay is darker. Only `overlay` is used as a raised surface, so the
mapping still holds -- but nothing here may assume "surface is darker".
"""

# standard library
from typing import cast

# typora themes tools
from typora_themes.colors import pick_mark, rgba

NAME = "Rose Pine"
PALETTE_URL = "https://rosepinetheme.com/palette"
PALETTE_FILE = "rose-pine.json"
OUT_DIR = "rosé-pine"  # repo folder (accented, matches the brand)
ASSET_DIR = "rose-pine"  # font folder inside Typora's themes dir (ascii; matches the css filenames)
ACCENT = "iris"
# Explicit: pre-commit's pretty-format-json sorts keys, so dict order is not stable.
VARIANTS = ("main", "moon", "dawn")

PALETTE = None  # injected by build.py


def variants():
    for key in VARIANTS:
        v = cast(dict, PALETTE)["variants"][key]
        yield {
            "key": key,
            "id": v["id"],
            "name": v["name"],
            "dark": v["dark"],
            "colors": {
                n: c["hex"]
                for n, c in sorted(v["colors"].items(), key=lambda kv: kv[1]["order"])
            },
        }


def variables(v):
    c = v["colors"]
    accent = c[ACCENT]
    dark = v["dark"]

    if dark:
        shadow_weak, shadow_strong = "rgba(0, 0, 0, 0.2)", "rgba(0, 0, 0, 0.5)"
    else:
        shadow_weak = rgba(c["muted"], 0.25)
        shadow_strong = rgba(c["muted"], 0.45)

    # gold is the only warm highlight; on Dawn it is a mid-tone that no palette
    # foreground clears AA against at full strength, so pick_mark blends it.
    mark_bg, mark_fg, _, _ = pick_mark(
        c["gold"], c["base"], [c["base"], c["text"], c["surface"]]
    )

    # Code sits on `surface` (the role upstream designates for panels/inputs).
    # `overlay` would be a raised surface and, on Dawn, is darker than base.
    code_bg = c["surface"]

    # Comments use `subtle`, not `muted`. Upstream assigns comments to `muted`,
    # but muted never clears 3:1 against any background on Moon (2.79) or Dawn
    # (2.87) -- its best case anywhere is 2.73 on Dawn's base. `subtle` is the
    # next step up the same ramp and reaches 4.2-5.1 on code_bg. Comments stay
    # italic, so they remain distinguishable from punctuation.
    comment = c["subtle"]

    out = {f"--rp-{name}": hex_ for name, hex_ in c.items()}
    out.update(
        {
            "--accent-color": accent,
            "--font-mono": '"Fira Code", "FiraCode Nerd Font", "FuraCode Nerd Font", ui-monospace, '
            '"SF Mono", Menlo, Consolas, "DejaVu Sans Mono", monospace',
            # backgrounds
            "--bg-color1": c["base"],
            "--bg-color2": c["surface"],
            "--bg-color3": c["overlay"],
            "--bg-color4": c["overlay"],
            "--bg-color5": c["overlay"],
            "--code-bg-color": code_bg,
            "--code-border-color": c["highlightMed"],
            # text
            "--text-color1": c["text"],
            "--text-color2": c["subtle"],
            "--text-color3": c["muted"],
            "--text-color4": c["text"],
            "--text-color5": c["muted"],
            "--link-color": accent,
            # table
            "--table-border-color": c["highlightMed"],
            "--table-thead-color": c["overlay"],
            "--table-bg-color": c["base"],
            "--table-bg-darker-color": c["surface"],
            # hover / active
            "--hover-bg-color1": c["highlightMed"],
            "--hover-bg-color2": c["highlightLow"],
            "--hover-bg-color3": rgba(c["highlightMed"], 0.8),
            "--hover-text-color": c["text"],
            "--active-color": c["highlightMed"],
            "--input-color": c["surface"],
            "--menu-divider-color": c["highlightMed"],
            "--scrollbar-thumb-color": c["highlightHigh"],
            "--scrollbar-track-color": rgba(c["highlightLow"], 0.5),
            "--theme-select-color": accent,
            "--button-color": c["overlay"],
            "--select-color": c["surface"],
            "--focus-color": rgba(accent, 0.6),
            "--focus-ring-color": rgba(accent, 0.6),
            # syntax, per the upstream role table
            "--code-red-color": c["love"],  # errors, builtins
            "--code-yellow-color": c["gold"],  # strings, warnings
            "--code-cyan-color": c["rose"],  # booleans
            "--code-blue-color": c["foam"],  # object keys, info
            "--code-purple-color": c["iris"],  # parameters, links
            "--code-orange-color": c["rose"],  # no orange in palette
            "--code-grey-color": comment,  # comments (see above)
            "--code-green-color": c["pine"],  # functions
            "--code-operator-color": c["subtle"],  # operators, punctuation
            "--code-bracket-color": c["subtle"],
            "--code-variable2-color": c["iris"],
            # selection bg is explicitly paired with `text` upstream
            "--code-select-bg-color": c["highlightMed"],
            "--code-cursor-color": c["highlightHigh"],
            "--select-text-bg-color": c["highlightMed"],
            "--search-select-bg-color": rgba(accent, 0.3),
            "--mark-bg-color": mark_bg,
            "--mark-text-color": mark_fg,
            "--shadow-weak": shadow_weak,
            "--shadow-strong": shadow_strong,
            "--danger-color": c["love"],
            "--danger-text-color": c["base"],
            "--backdrop-color": c["base"] if dark else c["overlay"],
            # table-insert grid board
            "--grid-thread-filled-color": c["highlightHigh"],
            "--grid-thread-empty-color": c["overlay"],
            "--grid-filled-color": c["muted"],
            # mermaid gantt
            "--gantt-section-a-color": c["surface"],
            "--gantt-section-b-color": c["base"],
            "--gantt-task-color": c["highlightMed"],
            "--gantt-active-color": c["highlightHigh"],
            "--gantt-done-color": c["highlightLow"],
            "--gantt-crit-color": c["love"],
            "--gantt-active-crit-color": c["gold"],
            "--gantt-done-crit-color": c["rose"],
            "--gantt-grid-text-color": c["subtle"],
            "--gantt-today-color": c["love"],
            # Typora implicit names
            "--primary-color": c["overlay"],
            "--primary-btn-border-color": "transparent",
            "--primary-btn-text-color": c["subtle"],
            "--side-bar-bg-color": c["surface"],
            "--control-text-color": c["subtle"],
            "--control-text-hover-color": c["text"],
            "--text-color": c["text"],
            "--bg-color": c["base"],
            "--item-hover-bg-color": c["highlightMed"],
            "--item-hover-text-color": c["text"],
            "--active-file-bg-color": c["highlightMed"],
            "--active-file-text-color": c["text"],
            "--active-file-border-color": accent,
            "--rawblock-edit-panel-bd": c["overlay"],
            "--blur-text-color": c["muted"],
            "--node-border": c["highlightMed"],
            "--node-fill": c["surface"],
        }
    )
    return out
