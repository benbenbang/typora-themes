#!/usr/bin/env bash
#
# Install this repo's themes into Typora's themes folder.
#
# Typora only lists *.css at the root of its themes folder, and resolves url()
# relative to the .css file. Each theme's CSS asks for ./<asset>/fonts/*.woff,
# so the installed layout is:
#
#   <themes>/catppuccin-mocha.css       real file
#   <themes>/catppuccin/fonts/*.woff    real directory, real font files
#
# Everything is copied, never symlinked: the themes folder keeps working after
# this repo is moved or deleted. Re-run after `uv run build-themes` to update.
#
# The asset folder name is read out of each .css file's own url(), so it stays
# correct even where it differs from the repo folder (rosé-pine -> rose-pine).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FONTS_SRC="$REPO_ROOT/firacode-fonts"

# Records what this script installed. Copies are indistinguishable from files a
# user wrote by hand, so --uninstall consults this instead of guessing, and
# install refuses to clobber anything not listed here.
MANIFEST=".typora-themes-manifest"

DRY_RUN=0
FORCE=0
ACTION="install"

function findext_root() {
    local MACOS="$HOME/Library/Application Support/abnerworks.Typora/themes"
    local WINDOWS="${APPDATA:-}/Typora/themes"
    local LINUX="$HOME/.config/Typora/themes"

    local DEFAULT_PATH=""
    case "$(uname -s)" in
        Darwin)
            DEFAULT_PATH="$MACOS"
            ;;
        Linux)
            DEFAULT_PATH="$LINUX"
            ;;
        CYGWIN*|MINGW*|MSYS*|Windows_NT)
            DEFAULT_PATH="$WINDOWS"
            ;;
        *)
            echo "Unsupported OS: $(uname -s)" >&2
            return 1
            ;;
    esac

    local EXTENSION_PATH="${TYPORA_EXTENSION_PATH:-$DEFAULT_PATH}"
    echo "${EXTENSION_PATH}"
}

function usage() {
    cat <<'EOF'
Usage: scripts/sync.sh [options]

Copies every generated theme into Typora's themes folder.

Options:
  -n, --dry-run    Show what would happen; change nothing.
  -f, --force      Overwrite files this script did not install.
  -u, --uninstall  Remove everything this script installed.
  -l, --list       List the themes this repo provides, then exit.
  -h, --help       Show this help.

Environment:
  TYPORA_EXTENSION_PATH   Override the themes folder (default: per-OS location).

Notes:
  Themes are copied, not symlinked, so they survive moving or deleting this repo.
  Re-run this script after `uv run build-themes` to push changes to Typora.

  Anything this script did not install is left alone unless --force. What it did
  install is recorded in <themes>/.typora-themes-manifest.

  Fira Code is copied into each theme's fonts/ folder. The themes prefer a
  locally installed Fira Code and fall back to the platform monospace face, so
  they still render if those files are removed.
EOF
}

function log() { printf '  %s\n' "$*"; }

# The asset folder a theme's CSS expects, e.g. `rose-pine`. Read from its url().
function asset_dir_for() {
    sed -n 's|.*url("\./\([^/]*\)/fonts/.*|\1|p' "$1" | head -1
}

# Theme dirs = repo subdirs holding at least one generated Typora theme.
# Identified by the header the generator writes, so `sources/` (a symlink to
# Typora's own folder) and the toolkit's sample CSS are never picked up.
function theme_css_files() {
    local dir css
    for dir in "$REPO_ROOT"/*/; do
        case "$(basename "$dir")" in
            sources|tools|scripts|firacode-fonts|typora-theme-toolkit) continue ;;
        esac
        for css in "$dir"*.css; do
            [ -e "$css" ] || continue
            if head -1 "$css" | grep -q 'for Typora$'; then
                printf '%s\n' "$css"
            fi
        done
    done
}

# Was `entry` (a top-level name) recorded by a previous install?
function in_manifest() {
    local themes_dir="$1" entry="$2"
    [ -f "$themes_dir/$MANIFEST" ] || return 1
    grep -Fxq -- "$entry" "$themes_dir/$MANIFEST"
}

# Decide whether we may write to <themes>/<entry>. Prints a reason and returns 1
# when the path exists but we did not put it there.
function may_write() {
    local themes_dir="$1" entry="$2" dst="$themes_dir/$2"

    if [ ! -e "$dst" ] && [ ! -L "$dst" ]; then
        return 0
    fi
    if in_manifest "$themes_dir" "$entry"; then
        return 0
    fi
    # A symlink into this repo is from an older version of this script.
    if [ -L "$dst" ]; then
        local target
        target="$(readlink "$dst")"
        case "$target" in "$REPO_ROOT"/*) return 0 ;; esac
    fi
    if [ "$FORCE" -eq 1 ]; then
        return 0
    fi
    log "skip        $entry (exists, not installed by this script; use --force)"
    return 1
}

function install_css() {
    local themes_dir="$1" css="$2" name
    name="$(basename "$css")"

    may_write "$themes_dir" "$name" || return 0

    if [ "$DRY_RUN" -eq 1 ]; then
        log "would copy  $name"
        return 0
    fi
    rm -rf "$themes_dir/$name"
    cp "$css" "$themes_dir/$name"
    log "copied      $name"
}

function install_fonts() {
    local themes_dir="$1" asset="$2" dst="$themes_dir/$2" n

    may_write "$themes_dir" "$asset" || return 0

    n="$(find "$FONTS_SRC" -name '*.woff' | wc -l | tr -d ' ')"
    if [ "$n" -eq 0 ]; then
        log "warn        $FONTS_SRC has no .woff files; $asset/fonts left empty"
    fi

    if [ "$DRY_RUN" -eq 1 ]; then
        log "would copy  $asset/fonts/ ($n woff)"
        return 0
    fi

    # An old install may have left a symlink here; replace it with a real dir.
    [ -L "$dst" ] && rm -f "$dst"

    mkdir -p "$dst/fonts"
    if [ "$n" -gt 0 ]; then
        cp "$FONTS_SRC"/*.woff "$dst/fonts/"
    fi
    log "copied      $asset/fonts/ ($n woff)"
}

function do_install() {
    local themes_dir="$1" css asset name seen_assets="" entries=""
    mkdir -p "$themes_dir"

    if [ ! -d "$FONTS_SRC" ]; then
        echo "missing fonts directory: $FONTS_SRC" >&2
        return 1
    fi

    # Process substitution, not a pipe: a pipe would run the loop in a subshell
    # and lose `seen_assets`, re-copying each asset dir once per variant.
    while IFS= read -r css; do
        name="$(basename "$css")"
        install_css "$themes_dir" "$css"
        entries="$entries$name"$'\n'

        asset="$(asset_dir_for "$css")"
        [ -n "$asset" ] || continue
        case " $seen_assets " in *" $asset "*) continue ;; esac
        seen_assets="$seen_assets $asset"
        install_fonts "$themes_dir" "$asset"
        entries="$entries$asset"$'\n'
    done < <(theme_css_files)

    if [ "$DRY_RUN" -eq 0 ]; then
        printf '%s' "$entries" > "$themes_dir/$MANIFEST"
        log "wrote       $MANIFEST"
    fi
}

function do_uninstall() {
    local themes_dir="$1" entry removed=0
    [ -d "$themes_dir" ] || { echo "nothing to do: $themes_dir does not exist"; return 0; }

    if [ ! -f "$themes_dir/$MANIFEST" ]; then
        log "no $MANIFEST found; nothing installed by this script"
        return 0
    fi

    while IFS= read -r entry; do
        [ -n "$entry" ] || continue
        local dst="$themes_dir/$entry"
        [ -e "$dst" ] || [ -L "$dst" ] || continue
        if [ "$DRY_RUN" -eq 1 ]; then
            log "would remove  $entry"
        else
            rm -rf "$dst"
            log "removed       $entry"
        fi
        removed=$((removed + 1))
    done < "$themes_dir/$MANIFEST"

    if [ "$DRY_RUN" -eq 0 ]; then
        rm -f "$themes_dir/$MANIFEST"
        log "removed       $MANIFEST"
    fi
    if [ "$removed" -eq 0 ]; then
        log "nothing to remove"
    fi
    return 0
}

function main() {
    while [ $# -gt 0 ]; do
        case "$1" in
            -n|--dry-run)   DRY_RUN=1 ;;
            -f|--force)     FORCE=1 ;;
            -u|--uninstall) ACTION="uninstall" ;;
            -l|--list)      ACTION="list" ;;
            -h|--help)      usage; return 0 ;;
            *) echo "unknown option: $1" >&2; usage >&2; return 2 ;;
        esac
        shift
    done

    if [ "$ACTION" = "list" ]; then
        while IFS= read -r css; do
            printf '%-28s -> asset dir: %s\n' "$(basename "$css")" "$(asset_dir_for "$css")"
        done < <(theme_css_files)
        return 0
    fi

    local themes_dir
    themes_dir="$(findext_root)"

    echo "repo:   $REPO_ROOT"
    echo "themes: $themes_dir"
    [ "$DRY_RUN" -eq 1 ] && echo "(dry run)"
    echo

    case "$ACTION" in
        install)   do_install "$themes_dir" ;;
        uninstall) do_uninstall "$themes_dir" ;;
    esac

    echo
    echo "Restart Typora to pick up changes."
}

main "$@"
