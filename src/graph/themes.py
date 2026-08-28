

THEMES = {
    "dark": {
        "bg": "#111111",
        "font": "white",
        "project": "#1f77b4",
        "vm": "#ff7f0e",
        "volume": "#2ca02c",
        "pod": "#d62728",
        "service": "#9467bd",
        "osd": "#17becf",
        "pool": "#bcbd22",
        "resource": "#8c564b",
        "default": "#7f7f7f",
    },
    "neon": {
        "bg": "#000000",
        "font": "#00ffff",
        "project": "#00ffff",
        "vm": "#ff00ff",
        "volume": "#ffff00",
        "pod": "#ff0000",
        "service": "#00ff00",
        "osd": "#ff8800",
        "pool": "#8888ff",
        "resource": "#ff8888",
        "default": "#888888",
    },
}


def heat_color(value: float) -> str:
    """
    value: 0.0 (cool) to 1.0 (hot)
    """
    v = max(0.0, min(1.0, value))
    r = int(255 * v)
    g = int(255 * (1.0 - v))
    return f"#{r:02x}{g:02x}00"
