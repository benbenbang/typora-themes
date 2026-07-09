# typora-themes

Generates the Typora themes in this repo from upstream color palettes. The generated
`*.css` files are committed; this package is what produces them.

## Usage

```sh
cd tools
uv sync
uv run build-themes              # all themes
uv run build-themes kanagawa     # just one
```

Output is written into the repo, next to each theme's README. The repo root is found by
walking up for a `.git` directory, so the command works from any directory; pass
`--repo-root` to override.

## Layout

```
src/typora_themes/
  cli.py            argument parsing
  build.py          template rendering, repo-root discovery
  colors.py         contrast, luminance, alpha blending
  template.css      the Typora selectors, shared by every theme
  themes/           one module per theme: palette roles -> CSS variables
  palettes/         vendored upstream palettes, pinned
```

`template.css` and `palettes/` are package data, read through `importlib.resources`, so
the build behaves the same whether it runs from the source tree or an installed wheel.

## Adding a theme

Add `palettes/<theme>.json`, then a `themes/<theme>.py` exposing:

| Name                            | Meaning                                              |
| :------------------------------ | :--------------------------------------------------- |
| `NAME`, `PALETTE_URL`, `ACCENT` | shown in the generated file header                   |
| `PALETTE_FILE`                  | filename under `palettes/`                           |
| `OUT_DIR`                       | repo folder the CSS is written to                    |
| `variants()`                    | yields `{id, name, dark, colors}` per variant        |
| `variables(variant)`            | maps palette roles onto the template's CSS variables |

Register it in `themes.NAMES`. The build fails if `variables()` omits any variable
`template.css` references, so a template edit cannot silently produce a broken theme.

## Notes

Every palette needed care beyond copying hex values — comment contrast and `==highlight==`
legibility differ per variant, Rosé Pine's upstream `palette.json` is stale, and
Kanagawa's background ramp is not monotonic. Each theme's README documents what was
changed and why.

Kanagawa has no machine-readable palette; its JSON is parsed statically from the
Neovim plugin's Lua (never executed).
