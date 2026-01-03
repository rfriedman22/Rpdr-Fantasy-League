import pandas as pd


class Contestant:
    """A Contestant represents a single player in the fantasy league.

    Parameters
    ----------
    name : str
        The name of the contestant.
    queen_rankings : pd.DataFrame
        A DataFrame containing the contestant's rankings of the queens, with one queen name per row, ordered from highest to lowest rank. The first queen is the captain, the next two are team members.

    Attributes
    ----------
    name : str
        The name of the contestant.
    queen_rankings : pd.DataFrame
        A DataFrame containing the contestant's rankings of the queens, with columns "queen" and "rank".
    """

    def __init__(self, name, queen_rankings):
        self.name = name

        queen_rankings["rank"] = queen_rankings.index + 1
        queen_rankings = queen_rankings.set_index("queen", drop=False)
        self.queen_rankings = queen_rankings

    def get_queen_rankings(self):
        """Get the contestant's rankings of the queens."""
        return self.queen_rankings

    def get_captain(self):
        """Get the contestant's captain (the queen ranked first)."""
        return self.get_queen_rankings().iloc[0]["queen"]

    def get_team(self):
        """Get the contestant's team (the first three queens ranked)."""
        return self.get_queen_rankings().iloc[:3]["queen"].values


class Contestants:
    """The class for managing the contestants in the fantasy league.

    Parameters
    ----------
    contestant_file : str
        The path to the file containing the contestants' data. Each row is a contestant and their rankings of the queens. The header row is skipped.
    n_queens : int
        The number of queens in the cast.

    Attributes
    ----------
    contestants : pd.DataFrame
        A DataFrame where the index is the contestant's name and there is a column "contestant" containing the Contestant objects.
    """

    def __init__(self, contestant_file, n_queens):
        names = ["name"] + [str(i) for i in range(1, n_queens + 1)]
        contestants_df = pd.read_csv(
            contestant_file,
            sep="\t",
            usecols=range(n_queens + 1),
            names=names,
            skiprows=1,
            index_col="name",
            comment="#",
        )
        contestants = pd.Series(
            {
                name: Contestant(
                    name, data.rename("queen").reset_index(drop=True).to_frame()
                )
                for name, data in contestants_df.iterrows()
            }
        )

        contestants.index.name = "name"
        contestants = contestants.rename("contestant").to_frame()
        contestants["name"] = contestants.index
        self.contestants = contestants

    def _assert_contestant_exists(self, contestant_name):
        """Make sure the contestant exists in the contestants DataFrame."""
        assert contestant_name in self.contestants.index.values, (
            f"Contestant {contestant_name} not found in contestants"
        )

    def get_contestants(self):
        """Get the DataFrame of all contestants."""
        return self.contestants

    def get_contestant(self, contestant_name):
        """Get a specific Contestant object by name."""
        self._assert_contestant_exists(contestant_name)
        return self.contestants.loc[contestant_name, "contestant"]

    def get_queen_rankings(self):
        """Get the queen rankings for all contestants.

        Returns
        -------
        pd.Series
            A Series where the index is the contestant's name and the values are DataFrames of queen rankings for each contestant.
        """
        rankings = (
            self.contestants["contestant"]
            .apply(lambda c: c.get_queen_rankings())
            .rename("queen_rankings")
        )
        return rankings

    def get_captains(self):
        """Get the captains for all contestants.

        Returns
        -------
        pd.Series
            A Series where the index is the contestant's name and the values are the captains (the queen ranked first) for each contestant.
        """
        captains = (
            self.contestants["contestant"]
            .apply(lambda c: c.get_captain())
            .rename("captain")
        )
        return captains

    def get_teams(self):
        """Get the teams for all contestants.

        Returns
        -------
        pd.Series
            A Series where the index is the contestant's name and the values are the teams (the first three queens ranked) for each contestant.
        """
        return (
            self.contestants["contestant"].apply(lambda c: c.get_team()).rename("team")
        )
