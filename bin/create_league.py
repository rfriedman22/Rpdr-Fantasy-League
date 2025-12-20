#!/usr/bin/env python3
import os
import argparse
from glob import glob
import subprocess

from commish.league import League
from commish import plotting


def run(cmd):
    subprocess.run(cmd, check=True)


parser = argparse.ArgumentParser(description="Create and analyze a fantasy league.")
parser.add_argument("--season", type=str, help="Season identifier.", required=True)
parser.add_argument(
    "--use_small_scores", action="store_true", help="Use small scoring system."
)
args = parser.parse_args()
season = args.season

if args.use_small_scores:
    event_scores_file = "small.tsv"
else:
    event_scores_file = "large.tsv"

# Set up the league
season_dir = os.path.join("assets", "seasons", season)
rules_dir = os.path.join("assets", "rules")
queens_file = os.path.join(season_dir, "queens.txt")
scoreboard_file = os.path.join(season_dir, "scoreboard.md")

league = League(
    season=season,
    queens_file=queens_file,
    contestant_file=os.path.join(season_dir, "contestants.tsv"),
    rank_score_file=os.path.join(rules_dir, "rank_values", "final_four.tsv"),
    event_scores_file=os.path.join(rules_dir, "event_scores", event_scores_file),
)

# Add episodes
episodes = sorted(glob(os.path.join(season_dir, "episodes", "*.json")))
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

with open(scoreboard_file, "r") as f:
    scoreboard_md = f.read()

# Switch to gh-pages to build the website
run(["git", "checkout", "gh-pages"])

page_dir = os.path.join("seasons", season)
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

# Commit and push
run(["git", "add", "."])
run(["git", "commit", "-m", f"Update league page for season {season}"])
run(["git", "push"])

# Switch back to main branch
run(["git", "checkout", "main"])
