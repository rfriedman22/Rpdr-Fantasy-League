#!/usr/bin/env python3
import os
import argparse
import yaml
from glob import glob

from commish.league import League
from commish import plotting


parser = argparse.ArgumentParser(description="Create and analyze a fantasy league.")
parser.add_argument(
    "--season-config", type=str, help="Path to season config YAML file.", required=True
)
parser.add_argument("--debug", action="store_true", help="Enable debug mode.")
parser.add_argument(
    "--output_dir",
    type=str,
    help="Base directory for files to be output. Things will go to <output_dir>/seasons/<season>",
    default="site-build",
)
args = parser.parse_args()
debug = args.debug
output_dir = args.output_dir

with open(args.season_config, "r") as f:
    season_config = yaml.safe_load(f)

season = season_config["season"]
page_dir = os.path.join(output_dir, "seasons", str(season))

league = League(
    season=season,
    queens_file=season_config["queens"],
    contestant_file=season_config["contestants"],
    rank_score_file=season_config["rank_scores"],
    event_scores_file=season_config["event_scores"],
)

# Add episodes
episodes = sorted(glob(os.path.join(season_config["episodes_dir"], "*.json")))
for episode_file in episodes:
    league.add_episode(episode_file)

# The total scores should be displayed in a nice way on the website
scores = league.total_scores().sort_values("total_score", ascending=False)
scores = scores.T.rename(
    index={
        "total_performance_score": "Performance Score",
        "total_rank_score": "Rank Score",
        "total_score": "Total Score",
    }
).rename_axis("", axis="columns")

with open(season_config["scoreboard"], "r") as f:
    scoreboard_md = f.read()

# The plots need to be in the same directory as the page for the website to build properly
plots_dir = os.path.join(page_dir, "plots")
os.makedirs(page_dir, exist_ok=True)
os.makedirs(plots_dir, exist_ok=True)

# Plots
plot_functions = [
    (plotting.plot_total_scores, "total_scores.png"),
    (plotting.plot_total_scores_split, "stacked_total_scores.png"),
    (plotting.plot_weekly_scores, "weekly_scores.png"),
    (plotting.plot_rank_scores, "rank_scores.png"),
    (plotting.plot_performance_scores, "weekly_performance_scores.png"),
]

for plot_func, filename in plot_functions:
    fig = plot_func(league)
    fig.savefig(os.path.join(plots_dir, filename))

event_scores = league.rules.get_event_scores()
event_scores = event_scores.rename_axis("Event", axis="index").rename("Point Value")
event_scores = event_scores.rename(lambda x: x.replace("_", " ").title())

rank_scores = league.rules.get_rank_scores()
rank_scores = rank_scores.rename(
    columns={
        "team_score": "Worth of the Team",
        "queen_score": "Worth of the Queen",
    }
).rename_axis("Rank", axis="index")

# Now when we make the page, the path needs to be relative to the page directory
plots_dir = "plots"
scoreboard_md = scoreboard_md.format(
    season=season,
    performance_rules=event_scores.to_markdown(),
    rank_rules=rank_scores.to_markdown(),
    captain_multiplier=league.rules.get_captain_multiplier(),
    scores_table=scores.to_markdown(),
    total_scores_plot=os.path.join(plots_dir, "total_scores.png"),
    stacked_total_scores_plot=os.path.join(plots_dir, "stacked_total_scores.png"),
    weekly_scores_plot=os.path.join(plots_dir, "weekly_scores.png"),
    rank_scores_plot=os.path.join(plots_dir, "rank_scores.png"),
    weekly_performance_scores_plot=os.path.join(
        plots_dir, "weekly_performance_scores.png"
    ),
)

with open(os.path.join(page_dir, "index.md"), "w") as f:
    f.write(scoreboard_md)
