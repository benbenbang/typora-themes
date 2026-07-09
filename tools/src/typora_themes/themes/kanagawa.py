"""Kanagawa -> Typora.

Upstream has no machine-readable palette: `lua/kanagawa/colors.lua` holds a flat
list of ~100 names and `lua/kanagawa/themes.lua` maps them onto semantic roles
per theme. Both are parsed statically (never executed) into palettes/kanagawa.json,
so the roles below are upstream's own, not a re-reading of the hex values:

    ui.fg / fg_dim        default and dimmed foreground
    ui.bg_m3..bg_p2       background ramp around ui.bg
    ui.bg_visual/search   selection and search highlight
    ui.special/nontext    de-emphasised foregrounds
    syn.*                 fun, keyword, string, type, constant, comment, ...

Two upstream quirks drive the mapping:

1. The bg ramp is NOT monotonic. On Dragon `bg_m1` is *lighter* than `bg`; on
   Lotus `bg_p1` is *darker* than `bg`. Only bg_m3/bg_m2/bg_dim are reliably
   darker than bg in all three, so every recessed surface comes from those.
2. `syn.comment` never clears 4.5:1 on any background, and on Lotus it fails even
   3:1 (2.93 on bg). Comments use `ui.special` instead -- the next step up, and
   the only in-palette foreground that holds up across all three variants.
"""

# typora themes tools
from typora_themes.colors import inline_code, pick_mark, rgba

NAME = "Kanagawa"
PALETTE_URL = "https://github.com/rebelot/kanagawa.nvim"
PALETTE_FILE = "kanagawa.json"
OUT_DIR = "kanagawa"
ACCENT = "syn.fun"  # crystalBlue / dragonBlue2 / lotusBlue4; AA on all variants
ACCENT_LABEL = "Blue (syn.fun)"
# Explicit: pre-commit's pretty-format-json sorts keys, so dict order is unstable.
VARIANTS = ("wave", "dragon", "lotus")
SECTIONS = ("ui", "syn", "diag", "vcs", "diff")

PALETTE = None  # injected by build.py


def _flatten(colors):
    """ui.float.bg -> 'ui-float-bg', in a deterministic order."""
    flat = {}
    for section in SECTIONS:
        for key in sorted(colors[section]):
            value = colors[section][key]
            if isinstance(value, dict):
                for sub in sorted(value):
                    flat[f"{section}-{key}-{sub}"] = value[sub]
            else:
                flat[f"{section}-{key}"] = value
    return flat


def variants():
    for key in VARIANTS:
        v = PALETTE["variants"][key]
        yield {
            "key": key,
            "id": v["id"],
            "name": v["name"],
            "title": v["name"],
            "dark": v["dark"],
            "colors": v["colors"],
        }


def variables(v):
    c = v["colors"]
    ui, syn, diag, vcs = c["ui"], c["syn"], c["diag"], c["vcs"]
    accent = syn["fun"]

    if v["dark"]:
        shadow_weak, shadow_strong = "rgba(0, 0, 0, 0.2)", "rgba(0, 0, 0, 0.5)"
    else:
        shadow_weak = rgba(ui["nontext"], 0.25)
        shadow_strong = rgba(ui["nontext"], 0.45)

    # diag.warning is the palette's only true highlighter tone. On Lotus it is a
    # mid-tone orange that no palette color clears AA against at full strength,
    # so pick_mark blends it toward bg until one does.
    mark_bg, mark_fg, _, _ = pick_mark(
        diag["warning"], ui["bg"], [ui["bg"], ui["fg"], ui["bg_m3"]]
    )

    # Comments: see module docstring. ui.special beats syn.comment everywhere.
    comment = ui["special"]

    # Inline `code`: orange glyphs on dark, orange-tinted chip on Lotus.
    ic_fg, ic_bg, ic_border = inline_code(
        syn["constant"], ui["bg_m2"], ui["bg_p1"], ui["fg"], v["dark"]
    )

    out = {f"--kg-{name}": hex_ for name, hex_ in _flatten(c).items()}
    out.update(
        {
            "--accent-color": accent,
            # backgrounds -- only bg_m3/bg_m2/bg_dim are darker than bg everywhere
            "--bg-color1": ui["bg"],
            "--bg-color2": ui["float"]["bg"],
            "--bg-color3": ui["bg_m2"],
            "--bg-color4": ui["float"]["bg"],
            "--bg-color5": ui["bg_p1"],
            "--code-bg-color": ui["bg_m2"],
            "--inline-code-color": ic_fg,
            "--inline-code-bg-color": ic_bg,
            "--inline-code-border-color": ic_border,
            "--code-border-color": ui["bg_p1"],
            # text
            "--text-color1": ui["fg"],
            "--text-color2": ui["fg_dim"],
            "--text-color3": ui["nontext"],
            "--text-color4": ui["fg"],
            "--text-color5": ui["nontext"],
            "--link-color": accent,
            # table
            "--table-border-color": ui["float"]["fg_border"],
            "--table-thead-color": ui["bg_p1"],
            "--table-bg-color": ui["bg"],
            "--table-bg-darker-color": ui["bg_m2"],
            # hover / active
            "--hover-bg-color1": ui["bg_p2"],
            "--hover-bg-color2": ui["bg_p1"],
            "--hover-bg-color3": rgba(ui["bg_p2"], 0.8),
            "--hover-text-color": ui["fg"],
            "--active-color": ui["bg_p2"],
            "--input-color": ui["bg_m2"],
            "--menu-divider-color": ui["float"]["fg_border"],
            "--scrollbar-thumb-color": ui["pmenu"]["bg_thumb"],
            "--scrollbar-track-color": rgba(ui["pmenu"]["bg_sbar"], 0.5),
            "--theme-select-color": accent,
            "--button-color": ui["bg_p1"],
            "--select-color": ui["bg_m2"],
            "--focus-color": rgba(accent, 0.6),
            "--focus-ring-color": rgba(accent, 0.6),
            # syntax, from upstream's syn.* roles
            "--code-red-color": syn["special2"],
            "--code-yellow-color": syn["identifier"],
            "--code-cyan-color": syn["type"],
            "--code-blue-color": syn["fun"],
            "--code-purple-color": syn["keyword"],
            "--code-orange-color": syn["constant"],
            "--code-grey-color": comment,
            "--code-green-color": syn["string"],
            "--code-operator-color": syn["operator"],
            "--code-bracket-color": syn["punct"],
            "--code-variable2-color": syn["special1"],
            "--code-select-bg-color": ui["bg_visual"],
            "--code-cursor-color": ui["fg"],
            "--select-text-bg-color": ui["bg_visual"],
            "--search-select-bg-color": ui["bg_search"],
            "--mark-bg-color": mark_bg,
            "--mark-text-color": mark_fg,
            "--shadow-weak": shadow_weak,
            "--shadow-strong": shadow_strong,
            "--danger-color": diag["error"],
            "--danger-text-color": ui["bg"],
            "--backdrop-color": ui["bg_m3"],
            # table-insert grid board
            "--grid-thread-filled-color": ui["bg_p2"],
            "--grid-thread-empty-color": ui["bg_p1"],
            "--grid-filled-color": ui["nontext"],
            # mermaid gantt
            "--gantt-section-a-color": ui["bg_m2"],
            "--gantt-section-b-color": ui["bg"],
            "--gantt-task-color": ui["bg_p1"],
            "--gantt-active-color": ui["bg_p2"],
            "--gantt-done-color": ui["bg_m2"],
            "--gantt-crit-color": diag["error"],
            "--gantt-active-crit-color": diag["warning"],
            "--gantt-done-crit-color": vcs["removed"],
            "--gantt-grid-text-color": ui["fg_dim"],
            "--gantt-today-color": diag["error"],
            # Typora implicit names
            "--primary-color": ui["bg_p1"],
            "--primary-btn-border-color": "transparent",
            "--primary-btn-text-color": ui["fg_dim"],
            "--side-bar-bg-color": ui["float"]["bg"],
            "--control-text-color": ui["fg_dim"],
            "--control-text-hover-color": ui["fg"],
            "--text-color": ui["fg"],
            "--bg-color": ui["bg"],
            "--item-hover-bg-color": ui["bg_p2"],
            "--item-hover-text-color": ui["fg"],
            "--active-file-bg-color": ui["bg_p2"],
            "--active-file-text-color": ui["fg"],
            "--active-file-border-color": accent,
            "--rawblock-edit-panel-bd": ui["bg_p1"],
            "--blur-text-color": ui["nontext"],
            "--node-border": ui["float"]["fg_border"],
            "--node-fill": ui["float"]["bg"],
        }
    )
    return out
