# Kanagawa

Typora themes for all three [Kanagawa](https://github.com/rebelot/kanagawa.nvim) variants,
accented with the signature blue (`syn.fun`).

| Theme | Variant | |
| :--- | :--- | :--- |
| `kanagawa-wave.css` | Kanagawa Wave | dark |
| `kanagawa-dragon.css` | Kanagawa Dragon | dark |
| `kanagawa-lotus.css` | Kanagawa Lotus | light |

## Install

Typora resolves `url()` relative to the theme file, and only lists `.css` files at the
root of the themes folder. So the CSS goes at the root and any fonts go in a
`kanagawa/` folder beside it — the same layout the stock `gothic` theme uses.

Open `Preferences → Appearance → Open Theme Folder`, then:

```sh
THEMES="$HOME/Library/Application Support/abnerworks.Typora/themes"   # macOS
cp kanagawa/kanagawa-*.css "$THEMES/"
```

Restart Typora; the variants appear as three entries in the Themes menu.

### Fonts

The themes ask for Fira Code and fall back to the platform monospace face. Nothing is
bundled — no font is committed under `kanagawa/`.

If Fira Code (or a Nerd Font build) is **installed on your system**, it is picked up via
`local()` and there is nothing else to do. Otherwise, to embed it for this theme:

```sh
mkdir -p "$THEMES/kanagawa/fonts"
cp firacode-fonts/*.woff "$THEMES/kanagawa/fonts/"
```

Skip that step and Typora will simply log two missing `.woff` requests and render with
the fallback face.

## Palette

Generated from upstream rather than hand-written:

```sh
cd tools && uv run build-themes kanagawa
```

Kanagawa ships no machine-readable palette. `lua/kanagawa/colors.lua` holds a flat list
of 103 color names, and `lua/kanagawa/themes.lua` maps them onto semantic roles
(`ui.*`, `syn.*`, `diag.*`, `vcs.*`, `diff.*`) once per variant.
`tools/src/typora_themes/palettes/kanagawa.json` is **parsed statically** from both
files, pinned at `bb85e4b` — the Lua is never executed. Syntax colors therefore follow
upstream's own `syn.*` roles rather than a re-reading of the hex values.

Two upstream details are normalised on the way in:

- `syn.variable` is the literal `"none"`, meaning "inherit the default foreground". It
  is resolved to `ui.fg`.
- `term[]` (18 ANSI colors) and `ui.pmenu.fg_sel` (also `"none"`) are dropped as unused.

### Contrast notes

**The background ramp is not monotonic.** Despite the `bg_m3 … bg … bg_p2` naming, on
Dragon `bg_m1` is *lighter* than `bg`, and on Lotus `bg_p1` is *darker* than `bg`. Only
`bg_m3`, `bg_m2` and `bg_dim` are reliably darker than `bg` in all three variants, so
every recessed surface (code, inputs, alternating table rows) is drawn from those. Any
mapping that assumes "`_p` means lighter" will invert on one variant.

- **Comments use `ui.special`, not `syn.comment`.** Upstream's comment color never
  clears 4.5:1 on any background, and on Lotus it fails even 3:1 (2.37:1 on the code
  surface). `ui.special` reaches 5.42 / 4.82 / 3.31:1 and is the only in-palette
  foreground that holds up across all three. Comments stay italic.
- **`==highlight==` uses `diag.warning`, tinted per variant.** Lotus's orange is a
  mid-tone that no palette color clears 4.5:1 against at full strength, so it is blended
  toward `bg` (α=0.4) until it does. The dark variants keep it at full strength.

Body text (11.26 / 10.76 / 6.19:1) and links (5.94 / 6.90 / 4.59:1) clear WCAG AA in
every variant. `syn.keyword` also clears AA everywhere if you prefer a violet accent.
