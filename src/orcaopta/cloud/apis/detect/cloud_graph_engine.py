import threading
import time

from orcaopta.cloud.apis.detect.graph import build_cloud_graph

# ---------------------------------------------------------
#  CLOUD GRAPH ENGINE
#  - Builds and caches cloud graph
#  - Never crashes if backends fail
#  - Safe for MCP and API usage
# ---------------------------------------------------------

# In‑memory cache
_cached_graph = None
_cached_at = None
_cache_ttl_seconds = 60  # adjust as you like

# Lock for thread safety
_cache_lock = threading.Lock()


def _should_refresh_cache():
    """
    Decide whether the cached graph is stale.
    """
    global _cached_at

    if _cached_graph is None or _cached_at is None:
        return True

    age = time.time() - _cached_at
    return age > _cache_ttl_seconds


def _build_graph_safe():
    """
    Build the cloud graph safely.
    Never raises; always returns a dict.
    """
    try:
        graph = build_cloud_graph()
        if not isinstance(graph, dict):
            return {
                "error": "build_cloud_graph() did not return a dict",
                "raw": graph,
            }
        return graph
    except Exception as e:
        return {
            "error": "Exception while building cloud graph",
            "exception": str(e),
        }


def refresh_cloud_graph():
    """
    Force a rebuild of the cloud graph and update cache.
    Returns the new graph.
    """
    global _cached_graph, _cached_at

    with _cache_lock:
        graph = _build_graph_safe()
        _cached_graph = graph
        _cached_at = time.time()
        return graph


def get_cached_cloud_graph(force_refresh: bool = False):
    """
    Public entry point.

    - If force_refresh=True, rebuilds the graph.
    - Otherwise, returns cached graph if fresh,
      or rebuilds if stale.

    Always returns a dict, never raises.
    """
    global _cached_graph

    with _cache_lock:
        if force_refresh or _should_refresh_cache():
            return refresh_cloud_graph()
        if _cached_graph is None:
            return refresh_cloud_graph()
        return _cached_graph
