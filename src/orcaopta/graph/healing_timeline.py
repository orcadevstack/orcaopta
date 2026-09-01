import plotly.express as px
import pandas as pd

def render_healing_timeline(events, output_html="healing_timeline.html"):
    rows = []
    for ev in events:
        rows.append({
            "timestamp": ev["timestamp"],
            "kind": ev["kind"],
            "action": ev["details"].get("action", "unknown"),
        })

    df = pd.DataFrame(rows)

    fig = px.timeline(
        df,
        x_start="timestamp",
        x_end="timestamp",
        y="kind",
        color="action",
        title="Healing Timeline"
    )

    fig.update_yaxes(autorange="reversed")
    fig.write_html(output_html)
    return output_html
