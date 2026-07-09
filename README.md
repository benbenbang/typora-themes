# typora-themes

Ten Typora themes across three palettes, generated from upstream color definitions
rather than hand-written.

| Palette                   | Variants                           | Accent           |
| :------------------------ | :--------------------------------- | :--------------- |
| [Catppuccin](catppuccin/) | Latte · Frappé · Macchiato · Mocha | Mauve            |
| [Rosé Pine](rosé-pine/)   | Rosé Pine · Moon · Dawn            | Iris             |
| [Kanagawa](kanagawa/)     | Wave · Dragon · Lotus              | Blue (`syn.fun`) |

Each palette's README documents its role mapping and the contrast decisions behind it.

## Install

```sh
./scripts/sync.sh
```

This copies every theme into Typora's themes folder; restart Typora and they appear in
`Preferences → Appearance → Themes`. Re-run it after changing a theme. Nothing is
symlinked, so the install keeps working if you move or delete this repo. See
[scripts/](scripts/) for `--dry-run`, `--force`, and `--uninstall`.

To install by hand instead, copy the `.css` files to the root of your themes folder and
the theme's asset folder beside them — each palette README has the exact commands.

### Fonts

The themes ask for **Fira Code** and fall back to the platform monospace face. If you
have Fira Code (or a Nerd Font build) installed, it is picked up via `local()`.
`sync.sh` also copies this repo's `firacode-fonts/` once into a shared
`<themes>/theme-fonts/` folder, so the themes render the same on a machine without it.

## Building

The `.css` files are committed, so you only need this to change a theme.

```sh
cd tools
uv sync
uv run build-themes              # all themes
uv run build-themes kanagawa     # just one
```

Edit `tools/src/typora_themes/template.css` (the Typora selectors, shared by every
theme) or a theme's role mapping in `tools/src/typora_themes/themes/`. Never edit the
generated `*.css` — they are overwritten. The build fails if the template references a
variable a theme does not define, so a template edit cannot silently ship a broken
theme. See [tools/](tools/) to add a palette.

## Layout

```
catppuccin/  rosé-pine/  kanagawa/   generated .css + README, fonts symlink
firacode-fonts/                      shared woff files
scripts/sync.sh                      link themes into Typora
tools/                               the generator (uv project)
sources -> …/abnerworks.Typora/themes    your Typora themes folder (gitignored)
```

## Notes on the palettes

None of the three could be ported by copying hex values straight across:

- **Catppuccin** — comments (`overlay0`) sit at 1.7:1 on `surface0` in Latte, so code
  moved to `mantle` with a border for definition.
- **Rosé Pine** — upstream's `palette.json` is stale (it has Dawn's `text` wrong and
  omits the `highlight*` roles), so the palette is taken from `source/index.ts` and
  cross-checked against the built `dist/css`.
- **Kanagawa** — has no machine-readable palette at all; it is parsed statically from
  the Neovim plugin's Lua. Its background ramp is not monotonic, despite the
  `bg_m3 … bg_p2` naming.

Where a palette cannot reach WCAG AA (Rosé Pine Dawn's iris links, at 3.47:1), the
brand color is kept and the number written down rather than silently swapped.

## Credits

[Catppuccin](https://github.com/catppuccin/catppuccin) ·
[Rosé Pine](https://github.com/rose-pine/rose-pine-theme) ·
[Kanagawa](https://github.com/rebelot/kanagawa.nvim) ·
[Fira Code](https://github.com/tonsky/FiraCode)

Palettes belong to their authors and are used under their respective licenses.
