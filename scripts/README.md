# scripts

## `sync.sh`

Copies the generated themes into Typora's themes folder.

```sh
./scripts/sync.sh              # install / update everything
./scripts/sync.sh --dry-run    # show what would happen
./scripts/sync.sh --uninstall  # remove what this script installed
./scripts/sync.sh --help
```

Re-run it after `uv run build-themes` to push changes to Typora, then restart Typora.

### What it creates

Typora only lists `.css` files at the **root** of its themes folder, and resolves
`url()` relative to the `.css` file. Each theme's CSS asks for
`./<asset>/fonts/*.woff`, so:

```
<themes>/rose-pine.css        real file
<themes>/rose-pine/fonts/     real directory, real .woff files
```

Everything is **copied, not symlinked**, so the themes folder keeps working after this
repo is moved or deleted. Nothing installed refers back to the repo.

Only the `.css` files and the fonts are copied — the repo's theme folder is never
installed wholesale, so its `README.md` and the other variants' CSS stay out of Typora's
themes folder.

The asset folder name is read out of each `.css` file's own `url()` declaration rather
than hardcoded, which is why the accented `rosé-pine/` repo folder installs as
`rose-pine/` — matching what the CSS actually asks for.

### Behavior

| | |
| :--- | :--- |
| Re-running | Idempotent. Refreshes files it installed, so a rebuilt theme is picked up. |
| Tracking | What it installed is recorded in `<themes>/.typora-themes-manifest`. |
| Foreign files | Left alone. A hand-written `github.css` is never touched. |
| Name collisions | Skipped with a warning unless `--force`. |
| `--uninstall` | Removes only what the manifest lists, then the manifest. |
| Older installs | A previous symlinked install is replaced with real files. |

### Themes folder

Detected per OS, overridable with `TYPORA_EXTENSION_PATH`:

| OS | Path |
| :--- | :--- |
| macOS | `~/Library/Application Support/abnerworks.Typora/themes` |
| Linux | `~/.config/Typora/themes` |
| Windows | `%APPDATA%/Typora/themes` |

```sh
TYPORA_EXTENSION_PATH=/tmp/themes ./scripts/sync.sh --dry-run
```

### Fonts

Fira Code is copied into each theme's `fonts/` folder. The themes prefer a locally
installed Fira Code via `local()` and fall back to the platform monospace face, so they
still render correctly if those files are ever removed.
