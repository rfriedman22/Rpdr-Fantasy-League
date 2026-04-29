# RPDR Fantasy League App

[!["Buy Me A Coffee"](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-orange?logo=buy-me-a-coffee)](https://www.buymeacoffee.com/rfriedman22)

This is an app to manage a fantasy league for RuPaul's Drag Race.

## Quickstart
Install the `commish` package to manage the league:
```sh
pip install .
```

Build a season:
```sh
python3 bin/create_league.py --season-config season-configs/17.yml
```

This script expects a file formatted like the one in `schemas/season-config.yml`, which should contain:
- The season number
- The path to several files, including the queens, the contestant submissions, and rulesets
- The path to a directory containing json files numbered `01.json`, `02.json`, etc. following the pattern in `schemas/episode.json`
- Any introductory text about the league
- Various customization options for the colors used in plots. If these parameters are not set, the defaults are used.
    - Note that if heatmap text annotations are hard to see, try setting the corresponding invert value to true.
- Optionally, the name of a template for the scoreboard. Template must be located in `templates`. Default is `season.md.j2`.

It will output a markdown file that can be rendered as a webpage using Jekyll or similar tools. The file is generated using Jinja2 following the templates in `templates/`.

There are multiple predefined rulesets provided in `assets/rules/`:
- `event_scores` contain the large and small rules for events like tops and bottoms of the week.
- `rank_values` contain the ranks values for a final three or final four situation.

## Working with your league
The main class for a league is the `League` class. You can create a league with the above files as follows:
```python
league = League(
    season = 17,
    queens_file = "queens.txt",
    contestant_file = "contestants.tsv",
    rank_score_file = "final_four.tsv",
    event_scores_file = "large.tsv"
)
```

Show the rules of the leauge:
```python
league.rules.get_captain_multiplier()
league.rules.get_rank_scores()
league.rules.get_event_scores()
```

Show everybody's captain or teams:
```python
league.contestants.get_captains()
league.contestants.get_teams()
```

Show how a specific player ranked the queens:
```python
ryan = league.contestants.get_contestant("Ryan")
ryan.get_queen_rankings()
```

Get information on the event scores on a specific queen:
```python
onya = league.cast.get_queen("Onya Nurve")
onya.get_performance_events()
```

### Adding an Episode
To add an episode to your league, make a copy of `schemas/episode.json` called `<episode number>.json` located in the `episodes_dir` of your season. Note that the episode number must be two digits, so single digit episodes need a leading zero. Any fields where the values are lists can be filled in with names of queens in the season's `queens.txt` file. Some special cases are below:
- In the case of a lip sync smackdown, points are applied each time a queen's name is entered for winning a lip sync. Do not enter queens for having to lip sync for their life.
- If there is a double sashay or a double shantay, the points are applied to all queens who have to lip sync for their life.
- All queens who are eliminated at the same time (e.g. from double sashays or a bracket-style elimination) will be assigned the same rank. For example, if 10 queens are remaining and 2 queens are eliminated at the same time, they tie for 9th place.
- In the finale episode, set the `finale` field to `true`, fill in the winner and runner up, and place any queens who made it to the finale but did not advance to the final lip sync in the `queen_eliminated` field.

## Publishing to the Web
There is a template for the website located in `site-template`. To publish the site to the web, run:
```sh
sh bin/publish.sh
```
This script starts by creating a temporary copy of `site-template` in a directory called `site-build`. Then it runs `create_league.py` for each YAML file in `season-configs`. Next it will switch to the `gh-pages`, move all the files out of the build, and remove the directory. Finally, it will commit and push to `gh-pages` before switching back to `main`.

You can test a local copy first by running:
```sh
sh bin/build_local.sh
```
This does a similar thing to `publish.sh`, but instead of switching branches, it will launch a local server so you can preview the website.

## Roadmap
- Enable archiving of past seasons
- Include checks on team creation so every queen is included
- Show exact events week-to-week for the queens
- Create a plot that shows each person's total score grow from week-to-week
- Share

### All Stars 11
- Need to account for differences in team composition (2 vs 3).