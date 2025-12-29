#!/usr/bin/env python3
import os
import argparse
import yaml
from glob import glob
from jinja2 import Environment, FileSystemLoader

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
os.makedirs(page_dir, exist_ok=True)

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

# Set up the scoreboard page
env = Environment(loader=FileSystemLoader("templates"), autoescape=False)
scoreboard_template = env.get_template("season.md.j2")

has_started = league.episode_number > 0
sections = {
    "scoring": has_started,
}

# Main scoreboard page
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

if "intro_text" not in season_config:
    season_config["intro_text"] = ""

context = {
    "season": season,
    "sections": sections,
    "queen_names": league.cast.get_queens().index.sort_values().tolist(),
    "finished": league.cast.num_remaining_queens() == 0,
    "performance_rules": event_scores.to_markdown(),
    "rank_rules": rank_scores.to_markdown(),
    "captain_multiplier": league.rules.get_captain_multiplier(),
    "intro_text": season_config["intro_text"],
}

# Scoring info
if has_started:
    scoring_context = {}
    scores = league.total_scores().sort_values("total_score", ascending=False)
    scores = scores.T.rename(
        index={
            "total_performance_score": "Performance Score",
            "total_rank_score": "Rank Score",
            "total_score": "Total Score",
        }
    ).rename_axis("", axis="columns")
    scoring_context["scores_table"] = scores.to_markdown()

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
        scoring_context_key = filename.replace(".png", "_plot")
        # Now when we make the page, the path needs to be relative to the page directory
        scoring_context[scoring_context_key] = os.path.join("plots", filename)

    context["scoring"] = scoring_context

# Render the page
with open(os.path.join(page_dir, "index.md"), "w") as f:
    f.write(scoreboard_template.render(**context))
