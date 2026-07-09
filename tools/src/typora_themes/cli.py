"""Command line entry point.

uv run build-themes                  # all themes
uv run build-themes rose_pine        # one theme
uv run build-themes --repo-root ..   # write somewhere else
"""

# standard library
import argparse

# typora themes tools
from typora_themes.build import build
from typora_themes.themes import NAMES


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="build-themes",
        description="Generate Typora themes from upstream color palettes.",
    )
    parser.add_argument(
        "themes",
        nargs="*",
        metavar="THEME",
        help=f"theme(s) to build (default: all of {', '.join(NAMES)})",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="repository root to write into (default: nearest ancestor with .git)",
    )
    args = parser.parse_args(argv)

    selected = args.themes or list(NAMES)
    unknown = [t for t in selected if t not in NAMES]
    if unknown:
        parser.error(
            f"unknown theme(s): {', '.join(unknown)}. choose from {', '.join(NAMES)}"
        )

    build(selected, root=args.repo_root)


if __name__ == "__main__":
    main()
