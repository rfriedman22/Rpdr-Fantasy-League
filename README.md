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
python3 bin/create_league.py --season 17
```

This will build a webpage reporting the state of the league. It expects the following files in `assets/seasons/17/`:
- `contestants.tsv` A table of contestants in the league. The first row is a header that is ignored. Each row is a contestant. The first column is their name, the remaining columns are their rankings of the queens from top to bottom.
- `queens.txt` The list of queens in this season's cast. Each queen is on their own line.
- `scoreboard.md` A markdown file that serves as the template for the scoreboard report.
- `episodes/` A directory of json files numbered `01.json`, `02.json`, etc. following the pattern in `schemas/episode.json`.

The rules files are in `assets/rules/`:
- `event_scores` contain the large and small rules for events like tops and bottoms of the week. Default is large rules. Toggle to small with the `--use_small_scores` flag.
- `rank_values` contain the ranks values for a final three or final four situation. Right now only final four is enabled.

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

## Roadmap
- Create the repo with MIT license. Check everything in, including the website
- Set up the Github pages
- Update the Jotform with link to the page and send out
- Create a config file for each league/season. The config should include a different template for each season.
- Figure out how to have pages for multiple leagues
- Show exact events week-to-week for the queens
- Create a plot that shows each person's total score grow from week-to-week
- Add an event for a second chance (queen is eliminated and comes back). Have a point value for this event. Have system to update queen ranks when someone is uneliminated.
- Share before next All Stars, testing on this season with my league
