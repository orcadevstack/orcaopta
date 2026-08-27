import time

_healing_events: list[dict] = []


def add_event(kind: str, details: dict):
    """
    kind: "openstack", "network", "storage", "kubernetes", "terraform", "global"
    details: anything you want to show on the dashboard
    """
    _healing_events.append({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "kind": kind,
        "details": details,
    })


def get_events():
    return list(_healing_events)[-200:]  # last 200 events
