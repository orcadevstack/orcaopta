import plotly.graph_objects as go

def render_rl_reward_graph(rewards, output_html="rl_reward_graph.html"):
    """
    rewards: list of floats from RL agent
    """

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=rewards,
        mode="lines+markers",
        line=dict(color="#1f77b4"),
        name="Reward"
    ))

    fig.update_layout(
        title="RL Reward Progression",
        xaxis_title="Step",
        yaxis_title="Reward",
        template="plotly_dark"
    )

    fig.write_html(output_html)
    return output_html
