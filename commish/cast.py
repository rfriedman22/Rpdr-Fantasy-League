import pandas as pd

from .queen import Queen


class Cast:
    """The class for managing the cast of queens in this season of RuPaul's Drag Race.

    Parameters
    ----------
    queens_file : str
        The path to the file containing the list of queens in the cast. Each line in the file should contain the name of a queen.

    Attributes
    ----------
    queens : pd.DataFrame
        A DataFrame containing the Queen objects in the cast, indexed by queen name.
    """

    def __init__(self, queens_file):
        queens = []
        with open(queens_file, "r") as f:
            for line in f:
                queen_name = line.strip()
                queens.append(Queen(queen_name))
        queens = pd.DataFrame({"queen": queens})
        queens["name"] = queens["queen"].apply(lambda q: q.get_name())
        queens = queens.set_index("name", drop=False)
        self.queens = queens

    def _assert_queen_exists(self, queen_name):
        """Make sure a queen's name is in the cast before trying to access it."""
        assert queen_name in self.queens.index.values, (
            f"Queen {queen_name} not found in cast"
        )

    def get_queens(self):
        """Get the DataFrame of Queen objects in the cast."""
        return self.queens

    def get_queen(self, queen_name):
        """Get a specific Queen object from the cast by name."""
        self._assert_queen_exists(queen_name)
        return self.queens.loc[queen_name, "queen"]

    def get_ranks(self):
        """Get the current ranks of all queens in the cast. If a queen has not been eliminated, their rank is 0."""
        ranks = self.queens.apply(lambda row: row["queen"].get_rank(), axis=1).rename(
            "rank"
        )
        return ranks

    def get_performances(self):
        """Get the performance events for all queens in the cast.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing all performance events for all queens, with columns for queen name, event, week, and any other relevant information.
        """
        performances = []
        for name, queen in self.queens["queen"].items():
            events = queen.get_performance_events()
            events["queen"] = name
            performances.append(events)

        performances = pd.concat(performances).reset_index(drop=True)
        return performances

    def num_remaining_queens(self):
        """Get the number of queens in the cast who have not been eliminated yet."""
        eliminated_mask = self.get_queens()["queen"].apply(lambda q: q.is_eliminated())
        num_remaining = sum(~eliminated_mask)
        return num_remaining

    def eliminate_queen(self, queen_name, week):
        """Eliminate a queen from the cast.

        When a queen is eliminated, their rank is set to the number of remaining queens at that time.

        Parameters
        ----------
        queen_name : str
            The name of the queen to eliminate.
        week : int
            The week number when the queen is eliminated. This is only used for logging purposes.
        """
        rank = self.num_remaining_queens()
        queen = self.get_queen(queen_name)
        queen.eliminate(week, rank)
