import pandas as pd


class Rules:
    """The class that defines the scoring rules for the league.

    Parameters
    ----------
    rank_score_file : str
        The path to the file containing rank score values. Assumes the first column is 'rank' and the second column is 'score'.
    event_scores_file : str
        The path to the file containing event score values. Assumes the first column is 'event' and the second column is 'score'.
    captain_multiplier : int
        The multiplier applied to the captain's score.

    Attributes
    ----------
    rank_scores : pd.DataFrame
        A DataFrame mapping ranks to team score and queen scores.
    event_scores : pd.Series
        A Series mapping event to score.
    captain_multiplier : int
        The multiplier applied to the captain's score.
    """

    def __init__(self, rank_score_file, event_scores_file, captain_multiplier):
        self.rank_scores = pd.read_csv(rank_score_file, sep="\t", index_col="rank")
        self.event_scores = pd.read_csv(
            event_scores_file, sep="\t", index_col="event"
        ).squeeze()
        self.captain_multiplier = captain_multiplier

    def get_captain_multiplier(self):
        """What is the captain multiplier?"""
        return self.captain_multiplier

    def get_rank_scores(self, kind="both"):
        """How many points is each rank worth?"""
        if kind == "both":
            return self.rank_scores
        elif kind == "team":
            return self.rank_scores["team_score"].rename("score")
        elif kind == "queen":
            return self.rank_scores["queen_score"].rename("score")
        else:
            raise ValueError(f"Unknown kind: {kind}")

    def get_event_scores(self):
        """How many points is each event worth?"""
        return self.event_scores
