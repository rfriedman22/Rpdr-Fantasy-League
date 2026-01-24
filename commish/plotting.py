import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np


def plot_total_scores(league, color=None, horizontal=True):
    """Plot total scores for each contestant as a bar chart."""
    scores = league.total_scores()
    fig, ax = plt.subplots()
    if horizontal:
        scores = scores.sort_values("total_score", ascending=True)
        bars = ax.barh(scores.index, scores["total_score"], color=color)
        # Add text labels beside each bar
        for bar, value in zip(bars, scores["total_score"]):
            ax.text(
                bar.get_width(),
                bar.get_y() + bar.get_height() / 2,
                f"{value}",
                ha="left",
                va="center",
            )
        ax.set_xlabel("Score")
        if min(scores["total_score"]) < 0:
            ax.axvline(0, color="black", linewidth=0.8)
    else:
        scores = scores.sort_values("total_score", ascending=False)
        bars = ax.bar(scores.index, scores["total_score"], color=color)
        # Add text labels above each bar
        for bar, value in zip(bars, scores["total_score"]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{value}",
                ha="center",
                va="bottom",
            )
        ax.set_ylabel("Score")
        ax.tick_params(axis="x", rotation=45)
        if min(scores["total_score"]) < 0:
            ax.axhline(0, color="black", linewidth=0.8)
    return fig


def plot_total_scores_split(league, colors=None, horizontal=True):
    """Plot total scores split into rank and performance scores as a stacked bar chart."""
    assert len(colors) == 2
    scores = league.total_scores()
    fig, ax = plt.subplots()
    if horizontal:
        scores = scores.sort_values("total_score", ascending=True)
        bars1 = ax.barh(
            scores.index,
            scores["total_performance_score"],
            left=scores["total_rank_score"],
            label="Performance Score",
            color=colors[0],
        )
        bars2 = ax.barh(
            scores.index,
            scores["total_rank_score"],
            label="Rank Score",
            color=colors[1],
        )
        ax.set_xlabel("Score")
        # Add text labels beside each bar
        for b1, b2, value in zip(bars1, bars2, scores["total_score"]):
            ax.text(
                b1.get_width() + b2.get_width(),
                b1.get_y() + b1.get_height() / 2,
                f"{value}",
                ha="left",
                va="center",
            )
        ax.legend(loc="upper left")
        if min(scores["total_score"]) < 0:
            ax.axvline(0, color="black", linewidth=0.8)
    else:
        scores = scores.sort_values("total_score", ascending=False)
        bars1 = ax.bar(
            scores.index,
            scores["total_performance_score"],
            label="Performance Score",
            color=colors[0],
        )
        bars2 = ax.bar(
            scores.index,
            scores["total_rank_score"],
            bottom=scores["total_performance_score"],
            label="Rank Score",
            color=colors[1],
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
        if min(scores["total_score"]) < 0:
            ax.axhline(0, color="black", linewidth=0.8)
    return fig


def plot_weekly_scores(league, **format_kwargs):
    """Plot the weekly performance scores for each contestant's team as a heatmap with total scores as a bar plot on the right."""
    scores = league.get_weekly_scores()
    fig, ax_list = heatmap_bar_biplot(scores, **format_kwargs)
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


def plot_performance_scores(league, **format_kwargs):
    """Plot weekly performance scores for each queen (before the captain multiplier) as a heatmap with total scores as a bar plot on the right."""
    scores = league.get_performance_scores()
    fig, ax_list = heatmap_bar_biplot(scores, **format_kwargs)
    return fig


def heatmap_bar_biplot(
    scores,
    cmap="PuOr_r",
    bar_color=None,
    pixel_size=0.24,
    barplot_width=1.0,
    ytick_space=1.15,
    panel_gap=0.08,
    vpad=0.5,
    fig_dpi=plt.rcParams["figure.dpi"],
):
    """Create a heatmap of scores with a bar plot of total scores to the right.

    Parameters
    ----------
    scores : pd.DataFrame
        DataFrame of scores to plot in the heatmap.
    cmap : str or matplotlib.colors.Colormap
        Colormap to use for the heatmap.
    bar_color : str
        Color of the bars in the bar plot.
    pixel_size : float, optional
        Size of each cell in the heatmap in inches.
    barplot_width : float, optional
        Width of the bar plot in inches.
    ytick_space : float, optional
        Space allocated for y-axis tick labels in inches.
    panel_gap : float, optional
        Gap between the heatmap and bar plot in inches.
    vpad : float, optional
        Vertical padding above and below the heatmap in inches.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The created figure.
    (ax_hm, ax_bar) : tuple of matplotlib.axes.Axes
        The heatmap and bar plot axes.
    """
    # Setup data
    totals = scores.sum(axis=1).sort_values()
    scores = scores.loc[totals.index[::-1]]

    # Figure out dimensions with a temporary heatmap
    nrow, ncol = scores.shape
    tmp_fig, tmp_ax = plt.subplots(figsize=(4, 4))

    tmp_ax.imshow(scores, aspect="equal")
    tmp_ax.set_yticks(range(nrow), labels=scores.index)

    tmp_fig.canvas.draw()
    renderer = tmp_fig.canvas.get_renderer()

    max_label_width_px = max(
        label.get_window_extent(renderer).width
        for label in tmp_ax.get_yticklabels()
        if label.get_text()
    )

    plt.close(tmp_fig)

    ytick_space_in = max_label_width_px / fig_dpi + 0.2
    heatmap_width = ncol * pixel_size
    total_width = ytick_space_in + heatmap_width + panel_gap + barplot_width
    total_height = nrow * pixel_size + 2 * vpad

    # Draw the real heatmap
    fig, ax_hm = plt.subplots(figsize=(total_width, total_height), dpi=fig_dpi)
    heatmap = ax_hm.imshow(
        scores,
        aspect="equal",
        cmap=cmap,
        norm=mcolors.CenteredNorm(),
    )
    set_xticks_above(ax_hm)
    ax_hm.set_xlabel("Episode")
    ax_hm.set_xticks(range(len(scores.columns)), labels=scores.columns)
    ax_hm.set_yticks(range(len(scores.index)), labels=scores.index)
    annotate_heatmap(ax_hm, scores)

    # Barplot
    ax_bar = add_axes(ax_hm, "right", size=barplot_width, pad=panel_gap)
    y = np.arange(nrow)
    ax_bar.barh(y, totals, color=bar_color)
    xmin = min(0, totals.min())
    xmax = totals.max()
    ax_bar.set_xticks([xmin, xmax])
    ax_bar.set_yticks([])
    ax_bar.set_ylim(ax_hm.get_ylim())
    ax_bar.invert_yaxis()
    ax_bar.set_title("Total\nScore")

    if xmin < 0:
        ax_bar.axvline(0, color="black", linewidth=0.8)

    return fig, (ax_hm, ax_bar)


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
    size : int or str, optional
        The size of the new axes as a percentage of the original axes size (str) or as an absolute size in inches (int).
    pad : float, optional
        The padding between the original axes and the new axes in inches.

    Returns
    -------
    matplotlib.axes.Axes
        The newly created axes.
    """
    divider = make_axes_locatable(ax)
    new_ax = divider.append_axes(position, size=size, pad=pad)
    return new_ax
