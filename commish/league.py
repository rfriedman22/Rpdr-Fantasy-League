import os
import itertools
import numpy as np
import pandas as pd

from .cast import Cast
from .contestant import Contestants
from .episode import Episode
from .rules import Rules


# The League class manages the overall fantasy league, including contestants, cast, episodes, and rules.
class League:
    """The main class for managing a fantasy league.

    The League class handles the players of the league (Contestants), the cast of queens (Cast), the episodes (Episode), and the scoring rules (Rules). Each week, a new episode is added to the league, which updates the performance of the queens in the cast. The league can then calculate scores for each contestant based on their chosen queens' performances and rankings.

    Parameters
    ----------
    season : str
        The season identifier for the league.
    queens_file : str
        The path to the file containing the list of queens in the cast.
    contestant_file : str
        The path to the file containing the contestants' data. Each row is a contestant and their rankings of the queens. The header row is skipped.
    rank_score_file : str
        The path to the file containing rank score values.
    event_scores_file : str
        The path to the file containing event score values.
    captain_multiplier : int, optional
        The multiplier applied to the captain's score (default is 2).

    Attributes
    ----------
    season : str
        What season of RuPaul's Drag Race the league is for.
    episode_number : int
        How many episodes have been added to this league.
    cast : Cast
        The cast of queens in this season of RuPaul's Drag Race.
    rules : Rules
        How scoring is calculated for this league.
    contestants : Contestants
        The contestants playing in this fantasy league.
    """

    def __init__(
        self,
        season,
        queens_file,
        contestant_file,
        rank_score_file,
        event_scores_file,
        captain_multiplier=2,
    ):
        # Attributes
        self.season = season
        self.episode_number = 0
        self.cast = Cast(queens_file)
        self.rules = Rules(rank_score_file, event_scores_file, captain_multiplier)
        self.contestants = Contestants(
            contestant_file, n_queens=len(self.cast.get_queens())
        )

    def _get_queen_rank_scores(self):
        """What is the current rank score for each queen in the cast?"""
        ranks = self.cast.get_ranks().to_frame()
        ranks = ranks.join(self.rules.get_rank_scores(kind="queen"), on="rank").fillna(
            0
        )
        scores = ranks["score"].rename("queen_rank_score").astype(int)
        return scores

    def _get_contestants_rank_scores(self):
        """How much is each queen worth for each contestant based on their rankings?"""
        contestants = self.contestants.get_contestants()
        queen_rankings = contestants["contestant"].apply(
            lambda c: c.get_queen_rankings()
        )
        rank_scores = queen_rankings.apply(
            lambda x: x.join(self.rules.get_rank_scores(kind="team"), on="rank")[
                "score"
            ]
        )
        return rank_scores

    def get_rank_scores(self):
        """The rank score is calculated by multiplying the queen's rank score by the contestant's rank score for that queen.

        Returns
        -------
        pd.DataFrame
            A DataFrame where the index is the contestant's name and the columns are the queens' names. The values are the rank scores for each queen for each contestant.
        """
        queen_scores = self._get_queen_rank_scores()
        contestant_scores = self._get_contestants_rank_scores()
        rank_scores = contestant_scores * queen_scores
        return rank_scores

    def get_performance_scores(self):
        """The performance score is calculated by summing the event scores for each queen for each week.

        Returns
        -------
        pd.DataFrame
            A DataFrame where the index is the queen's name and the columns are the week numbers. The values are the performance scores for each queen for each week.
        """
        performances = self.cast.get_performances()
        performance_scores = (
            performances.join(self.rules.get_event_scores(), on="event")
            .groupby(["queen", "week"])["value"]
            .sum()
            .rename("performance_score")
            .reset_index()
        )
        performance_scores = (
            performance_scores.pivot(
                index="queen", columns="week", values="performance_score"
            )
            .fillna(0)
            .astype(int)
            # Backfill any queens not on the scoreboard
            .reindex(self.cast.get_queens().index, fill_value=0)
        )
        return performance_scores

    def get_weekly_scores(self):
        """Calculate the weekly performance scores for each contestant based on their team captain and other two team members. The captain's performance score is multiplied by the captain multiplier.

        Returns
        -------
        pd.DataFrame
            A DataFrame where the index is the contestant's name and the columns are the week numbers. The values are the total performance scores for each contestant for each week.
        """
        performance_scores = self.get_performance_scores()

        # Make a local copy to avoid modifying the original data
        contestant_data = self.contestants.get_contestants().copy()
        contestant_data["team"] = self.contestants.get_teams()
        contestant_data["team_scores"] = contestant_data["team"].apply(
            lambda x: performance_scores.loc[x]
        )
        contestant_data["captain"] = contestant_data["contestant"].apply(
            lambda c: c.get_captain()
        )

        # Anonymous inner function to get the weekly scores for each team
        def get_row_scores(row):
            scores = row["team_scores"]
            scores.loc[row["captain"]] *= self.rules.get_captain_multiplier()
            return scores.sum(axis=0).rename("performance_score").reset_index()

        # Combine all contestant weekly scores into a single DataFrame
        weekly_scores = pd.concat(
            contestant_data.apply(get_row_scores, axis=1).tolist(),
            keys=contestant_data.index,
        ).reset_index()
        # Pivot from long to wide format
        weekly_scores = (
            weekly_scores.pivot(
                index="name", columns="week", values="performance_score"
            )
            .fillna(0)
            .astype(int)
        )
        return weekly_scores

    def total_performance_scores(self):
        """Calculate the total performance scores for each contestant by summing their weekly scores.

        Returns
        -------
        pd.Series
            A Series where the index is the contestant's name and the values are the total performance scores.
        """
        weekly_scores = self.get_weekly_scores()
        total_scores = weekly_scores.sum(axis=1).rename("total_performance_score")
        return total_scores

    def total_rank_scores(self):
        """Calculate the total rank scores for each contestant by summing their weekly rank scores.

        Returns
        -------
        pd.Series
            A Series where the index is the contestant's name and the values are the total rank scores.
        """
        rank_scores = self.get_rank_scores()
        total_scores = rank_scores.sum(axis=1).rename("total_rank_score")
        return total_scores

    def total_scores(self):
        """Calculate the total scores for each contestant by summing their total performance and rank scores.

        Returns
        -------
        pd.DataFrame
            A DataFrame where the index is the contestant's name and the columns are 'total_performance_score', 'total_rank_score', and 'total_score'.
        """
        total_performance = self.total_performance_scores()
        total_rank = self.total_rank_scores()
        scores = pd.concat([total_performance, total_rank], axis=1)
        scores["total_score"] = total_performance + total_rank
        return scores

    def add_episode(self, episode_file):
        """Add a new episode to the league and update the state accordingly.

        The episode is read in from the provided file. The state is updated with the following procedure:
        1. Eliminate any queens who were eliminated in this episode.
        2. Update the performance events for each queen based on the episode's performance data.
        3. If this is the finale episode, log the runner-up and winner.

        Parameters
        ----------
        episode_file : str
            The path to the episode data file (JSON format).
        """
        # Make sure this is the right episode
        episode = Episode(episode_file)
        episode_number = episode.get_episode_number()
        assert episode_number == self.episode_number + 1, (
            f"The next episode is {self.episode_number + 1}, but episode number {episode_number} was provided."
        )
        print(f"Adding episode {episode_number}...")
        self.episode_number = episode_number

        cast = self.cast

        # Eliminate queens as needed
        eliminated_queen = episode.get_eliminated_queen()
        if len(eliminated_queen) > 0:
            for q in eliminated_queen:
                cast.eliminate_queen(q, episode_number)

        # Apply the performance events to the appropriate queens
        for event, queen in episode.get_performance().itertuples(index=False):
            cast.get_queen(queen).add_performance_event(event, episode_number)

        # If this is the finale, eliminate the runner up and then the winner
        if episode.is_finale():
            winner, runners_up = episode.get_finale_data()
            for q in runners_up:
                cast.eliminate_queen(q, episode_number)

            cast.eliminate_queen(winner, episode_number)
