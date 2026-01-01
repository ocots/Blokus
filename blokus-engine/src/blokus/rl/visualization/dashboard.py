"""
Streamlit Dashboard for Blokus RL Training.

Launch with:
    streamlit run dashboard.py -- --models-dir /path/to/models

Features:
- Real-time metrics visualization
- Experiment comparison
- Auto-refresh during training
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install streamlit pandas plotly")
    sys.exit(1)

from blokus.rl.training.checkpoint import CheckpointManager, ExperimentInfo
from blokus.rl.training.metrics import MetricsTracker


def load_metrics(experiment_path: Path) -> pd.DataFrame:
    """Load metrics CSV as DataFrame."""
    csv_path = experiment_path / "metrics.csv"
    if not csv_path.exists():
        return pd.DataFrame()
    return pd.read_csv(csv_path)


def plot_win_rate(df: pd.DataFrame) -> go.Figure:
    """Plot win rate over training."""
    if df.empty or "eval/win_rate" not in df.columns:
        return go.Figure()
    
    # Filter to eval rows (where win_rate is not NaN)
    eval_df = df[df["eval/win_rate"].notna()].copy()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=eval_df["episode"],
        y=eval_df["eval/win_rate"],
        mode="lines+markers",
        name="Win Rate vs Random",
        line=dict(color="#10b981", width=2),
        marker=dict(size=4)
    ))
    
    # Add 50% baseline
    fig.add_hline(y=0.5, line_dash="dash", line_color="gray",
                  annotation_text="Random baseline (50%)")
    
    fig.update_layout(
        title="🏆 Win Rate vs Random Baseline",
        xaxis_title="Episode",
        yaxis_title="Win Rate",
        yaxis=dict(tickformat=".0%", range=[0, 1]),
        template="plotly_dark"
    )
    
    return fig


def plot_loss(df: pd.DataFrame) -> go.Figure:
    """Plot training loss."""
    if df.empty:
        return go.Figure()
    
    loss_cols = [c for c in df.columns if "loss" in c.lower()]
    if not loss_cols:
        return go.Figure()
    
    fig = go.Figure()
    
    for col in loss_cols:
        col_df = df[df[col].notna()]
        fig.add_trace(go.Scatter(
            x=col_df["step"],
            y=col_df[col],
            mode="lines",
            name=col.replace("train/", "").replace("_", " ").title(),
            opacity=0.7
        ))
    
    fig.update_layout(
        title="📉 Training Loss",
        xaxis_title="Step",
        yaxis_title="Loss",
        yaxis_type="log",
        template="plotly_dark"
    )
    
    return fig


def plot_episode_stats(df: pd.DataFrame) -> go.Figure:
    """Plot episode statistics."""
    if df.empty:
        return go.Figure()
    
    fig = make_subplots(rows=2, cols=1, 
                        subplot_titles=["Episode Length", "Epsilon (Exploration)"])
    
    # Episode length
    if "env/episode_length" in df.columns:
        length_df = df[df["env/episode_length"].notna()]
        fig.add_trace(
            go.Scatter(x=length_df["episode"], y=length_df["env/episode_length"],
                      mode="lines", name="Length"),
            row=1, col=1
        )
    
    # Epsilon
    if "train/epsilon" in df.columns:
        eps_df = df[df["train/epsilon"].notna()]
        fig.add_trace(
            go.Scatter(x=eps_df["episode"], y=eps_df["train/epsilon"],
                      mode="lines", name="Epsilon", line=dict(color="orange")),
            row=2, col=1
        )
    
    fig.update_layout(
        height=500,
        template="plotly_dark",
        showlegend=False
    )
    
    return fig


def main():
    st.set_page_config(
        page_title="Blokus RL Dashboard",
        page_icon="🧩",
        layout="wide"
    )
    
    st.title("🧩 Blokus RL Training Dashboard")
    
    # Sidebar - experiment selection
    st.sidebar.header("⚙️ Configuration")
    
    # Models directory
    models_dir = st.sidebar.text_input(
        "Models Directory",
        value="models/experiments",
        help="Directory containing experiment folders"
    )
    models_path = Path(models_dir)
    
    # List experiments
    experiments = CheckpointManager.list_experiments(models_path)
    
    if not experiments:
        st.warning(f"No experiments found in {models_dir}")
        st.info("Start training to see results here!")
        return
    
    # Experiment selector
    exp_names = [e.name for e in experiments]
    selected_name = st.sidebar.selectbox(
        "Select Experiment",
        exp_names,
        help="Choose an experiment to view"
    )
    
    selected_exp = next(e for e in experiments if e.name == selected_name)
    
    # Auto-refresh
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (5s)", value=False)
    if auto_refresh:
        st.rerun()  # Will trigger refresh
    
    # Load data
    df = load_metrics(selected_exp.path)
    
    # KPIs row
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Episodes", f"{selected_exp.total_episodes:,}")
    with col2:
        st.metric("Best Win Rate", f"{selected_exp.best_win_rate:.1%}")
    with col3:
        st.metric("Current Epoch", selected_exp.current_epoch)
    with col4:
        # Latest win rate
        latest_wr = df["eval/win_rate"].dropna().iloc[-1] if not df.empty and "eval/win_rate" in df else 0
        delta = latest_wr - 0.5  # Delta from random
        st.metric("Current Win Rate", f"{latest_wr:.1%}", delta=f"{delta:+.1%}")
    
    # Charts
    st.subheader("📈 Training Progress")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        fig_wr = plot_win_rate(df)
        st.plotly_chart(fig_wr, use_container_width=True)
    
    with col_right:
        fig_loss = plot_loss(df)
        st.plotly_chart(fig_loss, use_container_width=True)
    
    # Episode stats
    st.subheader("🎮 Episode Statistics")
    fig_stats = plot_episode_stats(df)
    st.plotly_chart(fig_stats, use_container_width=True)
    
    # Recent metrics table
    st.subheader("📋 Recent Metrics")
    if not df.empty:
        st.dataframe(
            df.tail(20).style.format(
                {c: "{:.4f}" for c in df.select_dtypes(include=['float']).columns}
            ),
            use_container_width=True
        )
    
    # Experiment info
    with st.expander("ℹ️ Experiment Details"):
        st.json({
            "name": selected_exp.name,
            "path": str(selected_exp.path),
            "created_at": selected_exp.created_at,
            "updated_at": selected_exp.updated_at,
            "total_episodes": selected_exp.total_episodes,
            "best_win_rate": selected_exp.best_win_rate,
            "current_epoch": selected_exp.current_epoch
        })
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Blokus RL** v0.1")
    st.sidebar.markdown("Made with ❤️ and 🧠")


if __name__ == "__main__":
    main()
