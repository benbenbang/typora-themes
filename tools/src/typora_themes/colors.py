"""Color math shared by the theme specs.

Hex is always authoritative. Upstream palettes sometimes ship rgb arrays that
disagree with their own hex (rose-pine's dawn.overlay, for one), so rgb is
always derived here rather than read from the palette file.
"""


def to_rgb(hex_):
    h = hex_.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def rgba(hex_, alpha):
    r, g, b = to_rgb(hex_)
    return f"rgba({r}, {g}, {b}, {alpha})"


def luminance(hex_):
    def chan(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = to_rgb(hex_)
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def is_dark(hex_):
    return luminance(hex_) < 0.5


def blend(fg, bg, alpha):
    """Composite fg over bg at alpha, returning an opaque hex."""
    f, b = to_rgb(fg), to_rgb(bg)
    return "#{:02x}{:02x}{:02x}".format(
        *(round(f[i] * alpha + b[i] * (1 - alpha)) for i in range(3))
    )


def best_fg(bg, candidates):
    """Highest-contrast candidate hex against bg."""
    return max(candidates, key=lambda c: contrast(c, bg))


def pick_mark(highlight, base, candidates, target=4.5):
    """Strongest tint of `highlight` over `base` that still carries a palette
    foreground at `target` contrast.

    Some palette yellows are mid-tone (Catppuccin Latte's, Rose Pine Dawn's
    gold) and no in-palette foreground clears AA against them at full strength.
    Blending toward base until one does keeps the highlight readable without
    introducing an off-palette color.
    """
    for step in range(20, 3, -1):  # alpha 1.00 -> 0.20
        alpha = step / 20
        bg = blend(highlight, base, alpha)
        fg = best_fg(bg, candidates)
        if contrast(fg, bg) >= target:
            return bg, fg, alpha, contrast(fg, bg)
    raise AssertionError(f"no accessible tint for {highlight} over {base}")


def inline_code(warm, code_bg, code_border, text, dark, target=4.5, max_alpha=0.18):
    """Emphasis for inline `code`, as (foreground, background, border).

    On dark backgrounds a warm foreground (peach/gold/orange) is bright and
    readable, so the glyphs carry the emphasis and the chip is untouched.

    On light backgrounds the same hues top out around 2.2-2.5:1 against the code
    surface -- far below AA -- and darkening them to pass turns peach into mud.
    So the chip carries the emphasis instead: warm tinted background, ordinary
    text. The tint is stepped down until the text clears `target`.
    """
    if dark:
        assert contrast(warm, code_bg) >= target, (
            f"warm inline-code fg {warm} on {code_bg} is only "
            f"{contrast(warm, code_bg):.2f}:1"
        )
        return warm, code_bg, code_border

    steps = max(int(round(max_alpha * 100)), 1)
    for step in range(steps, 0, -1):
        alpha = step / 100
        chip = blend(warm, code_bg, alpha)
        if contrast(text, chip) >= target:
            border = blend(warm, code_bg, min(alpha + 0.22, 1.0))
            return text, chip, border
    raise AssertionError(f"no accessible warm chip for {warm} over {code_bg}")
