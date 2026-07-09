# Catppuccin

Typora themes for all four [Catppuccin](https://catppuccin.com/palette) flavors, accented with **Mauve**.

| Theme | Flavor | |
| :--- | :--- | :--- |
| `catppuccin-latte.css` | Latte | light |
| `catppuccin-frappe.css` | Frappé | dark |
| `catppuccin-macchiato.css` | Macchiato | dark |
| `catppuccin-mocha.css` | Mocha | dark |

## Install

Typora resolves `url()` relative to the theme file, and only lists `.css` files at the
root of the themes folder. So the CSS goes at the root and any fonts go in a
`catppuccin/` folder beside it — the same layout the stock `gothic` theme uses.

Open `Preferences → Appearance → Open Theme Folder`, then:

```sh
THEMES="$HOME/Library/Application Support/abnerworks.Typora/themes"   # macOS
cp catppuccin/catppuccin-*.css "$THEMES/"
```

Restart Typora; the flavors appear as four entries in the Themes menu.

### Fonts

The themes ask for Fira Code and fall back to the platform monospace face. Nothing is
bundled — no font is committed under `catppuccin/`.

If Fira Code (or a Nerd Font build) is **installed on your system**, it is picked up via
`local()` and there is nothing else to do. Otherwise, to embed it for this theme, copy
the woff files in yourself:

```sh
mkdir -p "$THEMES/catppuccin/fonts"
cp firacode-fonts/*.woff "$THEMES/catppuccin/fonts/"
```

Skip that step and Typora will simply log two missing `.woff` requests and render with
the fallback face.

## Palette

The four themes are generated from the upstream palette rather than hand-written:

```sh
cd tools && uv run build-themes catppuccin
```

`tools/src/typora_themes/palettes/catppuccin.json` is vendored from
[catppuccin/palette](https://github.com/catppuccin/palette) and pinned. To follow an
upstream change, replace it and re-run. The role mapping lives in
`tools/src/typora_themes/themes/catppuccin.py`; the shared markup styling lives in
`tools/src/typora_themes/template.css`. Never edit the generated `catppuccin-*.css`.

### Contrast notes

Catppuccin's `overlay` ramp is intentionally low-contrast, which takes some care where
it meets text:

- **Code sits on `mantle`, not `surface0`.** Comments (`overlay2`) reach 5.1–6.2:1 on
  the dark flavors and 3.25:1 on Latte. On `surface0` they would fall to 1.7:1. A 1px
  `surface0` border keeps the block distinct from the page instead of relying on fill.
- **`==highlight==` is tinted per flavor.** Latte's yellow is a mid-tone mustard that no
  palette color clears 4.5:1 against, so it's blended toward `base` (α=0.5) until it
  does. The dark flavors keep yellow at full strength.

Body text and links clear WCAG AA (4.5:1) in every flavor.
