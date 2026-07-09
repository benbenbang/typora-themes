# Rosé Pine

Typora themes for all three [Rosé Pine](https://rosepinetheme.com/palette) variants,
accented with **Iris**.

| Theme                | Variant        |       |
| :------------------- | :------------- | :---- |
| `rose-pine.css`      | Rosé Pine      | dark  |
| `rose-pine-moon.css` | Rosé Pine Moon | dark  |
| `rose-pine-dawn.css` | Rosé Pine Dawn | light |

File names are the upstream variant ids, so they stay ASCII even though this folder
carries the accented brand name.

## Install

Typora resolves `url()` relative to the theme file, and only lists `.css` files at the
root of the themes folder. So the CSS goes at the root and any fonts go in a
`rose-pine/` folder beside it — the same layout the stock `gothic` theme uses.

Open `Preferences → Appearance → Open Theme Folder`, then:

```sh
THEMES="$HOME/Library/Application Support/abnerworks.Typora/themes"   # macOS
cp rosé-pine/rose-pine*.css "$THEMES/"
```

Restart Typora; the variants appear as three entries in the Themes menu.

### Fonts

The themes ask for Fira Code and fall back to the platform monospace face. Nothing is
bundled — no font is committed under `rosé-pine/`.

If Fira Code (or a Nerd Font build) is **installed on your system**, it is picked up via
`local()` and there is nothing else to do. Otherwise, to embed it for this theme:

```sh
mkdir -p "$THEMES/rose-pine/fonts"
cp firacode-fonts/*.woff "$THEMES/rose-pine/fonts/"
```

Skip that step and Typora will simply log two missing `.woff` requests and render with
the fallback face.

## Palette

Generated from the upstream palette rather than hand-written:

```sh
cd tools && uv run build-themes rose_pine
```

`tools/src/typora_themes/palettes/rose-pine.json` is derived from `source/index.ts` in
[rose-pine/rose-pine-palette](https://github.com/rose-pine/rose-pine-palette) (pinned at
`92af52b`). Syntax colors follow upstream's own role table — `love` for errors and
builtins, `gold` for strings, `rose` for booleans, `pine` for functions, `foam` for
object keys, `iris` for links and parameters, `muted` for de-emphasis.

### Why not upstream's `palette.json`

That file is stale and internally inconsistent; the vendored copy uses
`source/index.ts`, cross-checked against the built `dist/css` artifacts:

- It gives Dawn's `text` as `#464261`. The real value is `#575279` — `dist/css`,
  `source/index.ts`, and the site all agree.
- It omits `highlightLow` / `highlightMed` / `highlightHigh` entirely, which are the
  roles upstream designates for cursor line, selection background, and borders.
- Its `rgb` arrays disagree with its own `hex` for `dawn.overlay`
  (`[242, 233, 222]` vs `#f2e9e1` → `[242, 233, 225]`). The generator derives rgb from
  hex and never reads upstream's arrays.

### Contrast notes

Unlike Catppuccin, the background ramp is not monotonic: on the dark variants `surface`
and `overlay` are _lighter_ than `base`, while on Dawn `surface` is lighter but `overlay`
is darker. Nothing in the mapping may assume "surface is darker".

- **Comments use `subtle`, not `muted`.** Upstream assigns comments to `muted`, but
  `muted` never clears 3:1 against any background on Moon (2.79:1) or Dawn (2.87:1).
  `subtle` is the next step up the same ramp and reaches 4.2–5.1:1 on the code surface.
  Comments stay italic, so they remain distinct from punctuation.
- **`==highlight==` is tinted per variant.** Dawn's `gold` is a mid-tone that no palette
  color clears 4.5:1 against, so it is blended toward `base` (α=0.5) until it does. The
  dark variants keep `gold` at full strength.
- **Dawn's links are 3.47:1.** `iris` on Dawn's `base` does not reach WCAG AA, and no
  palette role clears 4.5:1 across all three variants (`pine` fixes Dawn at 5.59:1 but
  collapses to 3.38:1 on the main variant). Upstream assigns `iris` to links, so the
  brand color is kept rather than silently swapped. Body text clears AA everywhere.
