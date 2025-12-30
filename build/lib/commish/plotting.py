import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mpl_toolkits.axes_grid1 import make_axes_locatable


def plot_total_scores(league):
    """Plot total scores for each contestant as a bar chart."""
    scores = league.total_scores().sort_values("total_score", ascending=False)
    fig, ax = plt.subplots()
    bars = ax.bar(scores.index, scores["total_score"])
    ax.set_ylabel("Score")
    # Add text labels above each bar
    for bar, value in zip(bars, scores["total_score"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value}",
            ha="center",
            va="bottom",
        )
    return fig


def plot_total_scores_split(league):
    """Plot total scores split into rank and performance scores as a stacked bar chart."""
    scores = league.total_scores().sort_values("total_score", ascending=False)
    fig, ax = plt.subplots()
    bars1 = ax.bar(scores.index, scores["total_rank_score"], label="Rank Score")
    bars2 = ax.bar(
        scores.index,
        scores["total_performance_score"],
        bottom=scores["total_rank_score"],
        label="Performance Score",
    )
    ax.set_ylabel("Score")
    # Add text labels above each bar
    for b1, b2, value in zip(bars1, bars2, scores["total_score"]):
        ax.text(
            b1.get_x() + b1.get_width() / 2,
            b1.get_height() + b2.get_height(),
            f"{value}",
            ha="center",
            va="bottom",
        )
    ax.legend(loc="lower left")
    return fig


def plot_weekly_scores(league):
    """Plot the weekly performance scores for each contestant's team as a heatmap with total scores as a bar plot on the right."""
    scores = league.get_weekly_scores()
    totals = scores.sum(axis=1).sort_values()
    scores = scores.loc[totals.index[::-1]]

    fig, ax = plt.subplots()
    # Draw the heatmap
    heatmap = ax.imshow(
        scores,
        aspect="equal",
        cmap="coolwarm",
        norm=mcolors.CenteredNorm(),
    )
    set_xticks_above(ax)
    ax.set_xlabel("Episode")
    ax.set_xticks(range(len(scores.columns)), labels=scores.columns)
    ax.set_yticks(range(len(scores.index)), labels=scores.index)
    annotate_heatmap(ax, scores)

    # Add barplot of total performance scores to the right
    ax2 = add_axes(ax, "right")
    bars = ax2.barh(scores.index, totals)
    ax2.set_xticks([0, max(totals)])
    ax2.set_yticks([])
    ax2.set_ylim(reversed(ax.get_ylim()))
    ax2.set_title("Total\nScore")
    fig.tight_layout()
    return fig


def plot_rank_scores(league):
    """Plot the rank scores each queen contributes to each team. Queens are ordered by their rank in the season. Queens who are still in the competition are at the bottom."""
    scores = league.get_rank_scores().T
    ranks = league.cast.get_ranks()
    ranks[ranks == 0] = float("inf")  # So that unranked go to bottom
    ranks = ranks.sort_values()
    scores = scores.loc[ranks.index, ::-1]
    fig, ax = plt.subplots()
    ax.imshow(scores, aspect="equal", cmap="Reds")
    ax.set_xticks(range(len(scores.columns)))
    ax.set_xticklabels(scores.columns, rotation=90, ha="center", va="top")
    ax.set_yticks(range(len(scores.index)), labels=scores.index)
    annotate_heatmap(ax, scores)
    fig.tight_layout()
    return fig


def plot_performance_scores(league):
    """Plot weekly performance scores for each queen (before the captain multiplier) as a heatmap with total scores as a bar plot on the right."""
    scores = league.get_performance_scores()
    totals = scores.sum(axis=1).sort_values()
    scores = scores.loc[totals.index[::-1]]

    fig, ax = plt.subplots()
    # Draw the heatmap
    heatmap = ax.imshow(
        scores,
        aspect="equal",
        cmap="coolwarm",
        norm=mcolors.CenteredNorm(),
    )
    set_xticks_above(ax)
    ax.set_xlabel("Episode")
    ax.set_xticks(range(len(scores.columns)), labels=scores.columns)
    ax.set_yticks(range(len(scores.index)), labels=scores.index)
    annotate_heatmap(ax, scores)

    # Add barplot of total performance scores to the right
    ax2 = add_axes(ax, "right")
    bars = ax2.barh(scores.index, totals)
    ax2.set_xticks([min(totals), max(totals)])
    ax2.set_yticks([])
    ax2.axvline(0, color="black", linewidth=0.8)
    ax2.set_ylim(reversed(ax.get_ylim()))
    ax2.set_title("Total\nScore")

    fig.tight_layout()
    return fig


def annotate_heatmap(ax, data):
    """Annotate each cell on the heatmap with the underlying value"""
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(
                j,
                i,
                f"{data.iloc[i, j]}",
                ha="center",
                va="center",
                color="black"
                if abs(data.iloc[i, j]) < (data.values.max() / 2)
                else "white",
            )
    return ax


def set_xticks_above(ax):
    """Set x-axis ticks above the plot."""
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")


def add_axes(ax, position, size="25%", pad=0.02):
    """Add new axes to a given axes at the specified position.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The original axes to which new axes will be added.
    position : str
        The position to add the new axes ('right', 'left', 'top', 'bottom').
    size : str, optional
        The size of the new axes as a percentage of the original axes size.
    pad : float, optional
        The padding between the original axes and the new axesß.

    Returns
    -------
    matplotlib.axes.Axes
        The newly created axes.
    """
    divider = make_axes_locatable(ax)
    new_ax = divider.append_axes(position, size=size, pad=pad)
    return new_ax
