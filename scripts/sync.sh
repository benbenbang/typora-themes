#!/usr/bin/env bash
#
# Install this repo's themes into Typora's themes folder.
#
# Typora only lists *.css at the root of its themes folder, and resolves url()
# relative to the .css file. Every theme's CSS asks for ./theme-fonts/*.woff,
# so one shared folder serves them all and the installed layout is:
#
#   <themes>/catppuccin-mocha.css   real file
#   <themes>/theme-fonts/*.woff     real directory, shared by every theme
#
# Everything is copied, never symlinked: the themes folder keeps working after
# this repo is moved or deleted. Re-run after `uv run build-themes` to update.
#
# The font folder name is read out of the generated CSS's own url(), so the
# script and the themes can never disagree about where the fonts live.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FONTS_SRC="$REPO_ROOT/firacode-fonts"

# Records what this script installed. Copies are indistinguishable from files a
# user wrote by hand, so --uninstall consults this instead of guessing, and
# install refuses to clobber anything not listed here.
MANIFEST=".typora-themes-manifest"

# Shared font folder name, read from the generated CSS at run time.
FONTS_DIR=""

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

  Fira Code is copied once into a shared <themes>/theme-fonts/ folder, not into
  each theme. The themes prefer a locally installed Fira Code and fall back to
  the platform monospace face, so they still render if those files are removed.
EOF
}

function log() { printf '  %s\n' "$*"; }

# The font folder a theme's CSS expects, e.g. `theme-fonts`. Read from its url()
# so the script and the generated CSS can never disagree about the name.
#
# No `| head -1`: under `set -o pipefail` the reader exiting early sends SIGPIPE
# to sed, and the 141 takes the whole script down.
function fonts_dir_for() {
    local all
    all="$(sed -n 's|.*url("\./\([^/]*\)/FiraCode-.*|\1|p' "$1")"
    printf '%s\n' "${all%%$'\n'*}"
}

# The woff files the themes actually reference, e.g. FiraCode-Regular.woff.
# firacode-fonts/ also ships FiraCode-VF.woff, which no @font-face names.
function referenced_fonts() {
    local css
    while IFS= read -r css; do
        sed -n 's|.*url("\./[^/]*/\([^"]*\.woff\)".*|\1|p' "$css"
    done < <(theme_css_files) | sort -u
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

# One shared folder for every theme, so the fonts are copied once rather than
# duplicated per theme.
function install_fonts() {
    local themes_dir="$1" fonts_dir="$2" dst="$themes_dir/$2" woff missing=0 n=0

    may_write "$themes_dir" "$fonts_dir" || return 0

    for woff in $(referenced_fonts); do
        if [ -f "$FONTS_SRC/$woff" ]; then
            n=$((n + 1))
        else
            log "warn        $woff referenced by a theme but missing from $FONTS_SRC"
            missing=$((missing + 1))
        fi
    done

    if [ "$DRY_RUN" -eq 1 ]; then
        log "would copy  $fonts_dir/ ($n woff)"
        return 0
    fi

    # An old install may have left a symlink, or a per-theme <asset>/fonts/ tree.
    [ -L "$dst" ] && rm -f "$dst"

    mkdir -p "$dst"
    for woff in $(referenced_fonts); do
        [ -f "$FONTS_SRC/$woff" ] && cp "$FONTS_SRC/$woff" "$dst/$woff"
    done
    log "copied      $fonts_dir/ ($n woff)"
}

# Remove the <asset>/fonts/ folders an older version of this script created.
function prune_legacy_assets() {
    local themes_dir="$1" entry
    while IFS= read -r entry; do
        [ -n "$entry" ] || continue
        local dst="$themes_dir/$entry"
        [ -d "$dst" ] || [ -L "$dst" ] || continue
        if [ "$DRY_RUN" -eq 1 ]; then
            log "would drop  $entry/ (old per-theme font folder)"
        else
            rm -rf "$dst"
            log "dropped     $entry/ (old per-theme font folder)"
        fi
    done < <(legacy_asset_dirs "$themes_dir")
}

# Manifest entries from an older layout: a directory that is not the shared
# fonts dir. Those were the per-theme <asset>/ folders holding fonts/.
function legacy_asset_dirs() {
    local themes_dir="$1" entry
    [ -f "$themes_dir/$MANIFEST" ] || return 0
    while IFS= read -r entry; do
        [ -n "$entry" ] || continue
        case "$entry" in
            *.css) continue ;;
            "$FONTS_DIR") continue ;;
        esac
        printf '%s\n' "$entry"
    done < "$themes_dir/$MANIFEST"
}

function do_install() {
    local themes_dir="$1" css name first_css entries=""
    mkdir -p "$themes_dir"

    if [ ! -d "$FONTS_SRC" ]; then
        echo "missing fonts directory: $FONTS_SRC" >&2
        return 1
    fi

    # Read the first line without a pipe; `| head -1` would SIGPIPE the producer
    # and, with pipefail, abort the script.
    first_css=""
    while IFS= read -r css; do first_css="$css"; break; done < <(theme_css_files)
    if [ -z "$first_css" ]; then
        echo "no generated themes found under $REPO_ROOT" >&2
        return 1
    fi
    FONTS_DIR="$(fonts_dir_for "$first_css")"
    if [ -z "$FONTS_DIR" ]; then
        echo "could not determine the font folder from $first_css" >&2
        return 1
    fi

    # Older installs put a copy of the fonts under every theme's own folder.
    # Drop those before writing the new manifest, or they leak forever.
    prune_legacy_assets "$themes_dir"

    while IFS= read -r css; do
        name="$(basename "$css")"
        install_css "$themes_dir" "$css"
        entries="$entries$name"$'\n'
    done < <(theme_css_files)

    # One shared folder for every theme, not one per theme.
    install_fonts "$themes_dir" "$FONTS_DIR"
    entries="$entries$FONTS_DIR"$'\n'

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
            printf '%-28s -> fonts: %s/\n' "$(basename "$css")" "$(fonts_dir_for "$css")"
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
