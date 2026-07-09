"""Render Typora themes from a theme spec plus the shared template.

The template and palettes are package data, read through importlib.resources, so
the build works from any working directory. Only the *output* location depends on
the repo, and that is resolved by walking up for a `.git` directory.
"""

# standard library
import importlib
import json
import re
from importlib.resources import files
from pathlib import Path

PACKAGE = "typora_themes"

# One shared font folder at the root of Typora's themes dir, rather than a copy
# per theme. Named distinctly so it cannot collide with a theme's own asset dir.
FONTS_DIR = "theme-fonts"


def repo_root(start=None):
    """Nearest ancestor containing .git, searched from `start` then from here."""
    candidates = []
    if start is not None:
        candidates.append(Path(start).resolve())
    candidates.extend([Path.cwd().resolve(), Path(__file__).resolve()])
    for candidate in candidates:
        for directory in (candidate, *candidate.parents):
            if (directory / ".git").exists():
                return directory
    raise SystemExit("could not locate the repository root (no .git found)")


def read_template():
    return (files(PACKAGE) / "template.css").read_text(encoding="utf-8")


def read_palette(name):
    data = (files(PACKAGE) / "palettes" / name).read_text(encoding="utf-8")
    return json.loads(data)


def load_spec(name):
    spec = importlib.import_module(f"{PACKAGE}.themes.{name}")
    spec.PALETTE = read_palette(spec.PALETTE_FILE)
    return spec


def render(spec, template, root):
    """Write one CSS file per variant. Yields (path, variable_count)."""
    required = set(re.findall(r"var\((--[\w-]+)", template))

    for variant in spec.variants():
        css_vars = spec.variables(variant)

        missing = required - set(css_vars)
        if missing:
            raise SystemExit(
                f"{spec.NAME} / {variant['id']}: template references undefined "
                f"variables: {sorted(missing)}"
            )

        substitutions = {
            "{ROOT_VARS}": "\n".join(f"    {k}: {v};" for k, v in css_vars.items()),
            "{TITLE}": variant.get("title") or f"{spec.NAME} {variant['name']}",
            "{PALETTE_URL}": spec.PALETTE_URL,
            # ACCENT may be a role path ("syn.fun"); specs can supply a nicer label.
            "{ACCENT_NAME}": getattr(spec, "ACCENT_LABEL", spec.ACCENT.capitalize()),
            "{FONTS_DIR}": FONTS_DIR,
        }
        css = template
        for token, value in substitutions.items():
            css = css.replace(token, value)

        leftover = re.findall(r"\{[A-Z_]+\}", css)
        if leftover:
            raise SystemExit(f"{variant['id']}: unsubstituted tokens {leftover}")

        dest = root / spec.OUT_DIR / f"{variant['id']}.css"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(css, encoding="utf-8")
        yield dest, len(css_vars)


def build(names, root=None):
    root = repo_root() if root is None else Path(root).resolve()
    template = read_template()
    for name in names:
        spec = load_spec(name)
        print(f"{spec.NAME}  (accent: {spec.ACCENT})")
        for dest, nvars in render(spec, template, root):
            rel = dest.relative_to(root)
            print(f"  {str(rel):44} {dest.stat().st_size:>6} bytes  {nvars} vars")
