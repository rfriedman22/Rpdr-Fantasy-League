# RuPaul's Drag Race Season {season} Fantasy League

This is the fantasy league for RuPaul's Drag Race I ran for some friends. I ran it out of Google Sheets, but it was kind of a pain to maintain that way, so I decided to make myself an app to manage the scoring for me. I've tested it out by recreating the league from this season.

Right now, the scoring information is with an updated rules set I'm using for next season. It doesn't change the results, but it's not the same rules as what actually went down. Once I set things up for the upcoming season and work out the website a little bit more, I'll revert this season to the scoring system that was used at the time.

## Scoring

There are two ways to earn points: the **performance** of your team and the **rank** of each queen.

### Performances

Each week, you gain or lose points when the following things happen to your team member:

{performance_rules}

Points have {captain_multiplier} times greater value for your captain.

In a lip sync smackdown, points are earned each time a queen wins a lip sync, but no points are deducted for a queen being eliminated from the bracket.

### Ranks

Based on how a queen ranks, they will earn a select number of points. Those points will be multiplied by the point value of the rank assigned in the team selection.

**Note:** This scoring system assumes a final four and no double sashays. In a final four, third and fourth place are worth the same. The teammate you think will be runner-up is worth slightly more than the third teammate. Rules will be adjusted if needed.

{rank_rules}

#### Example

- Team 1 ranks Jinkx 12th
- Team 2 ranks Jinkx 5th
- Team 3 ranks Jinkx as their captain

Jinkx finishes in 4th, so she is worth 13 points. Then:
- Team 1 earns 3 x 13 = 39 points
- Team 2 earns 10 x 13 = 130 points
- Team 3 earns 25 x 13 = 325 points

## Total Scores

Here's how everybody did overall this season:

{scores_table}

![Total Scores]({total_scores_plot})

![Stacked Total Scores]({stacked_total_scores_plot})

## Rank Scores

Here is how every queen finished and how many points they earned for each contestant in the league:

![Rank Scores]({rank_scores_plot})

## Performance Scores

Here's how well everyone's team did on a week-to-week basis:

![Weekly Scores]({weekly_scores_plot})

Here is the breakdown of how each queen scored each week:

![Weekly Performance Scores]({weekly_performance_scores_plot})