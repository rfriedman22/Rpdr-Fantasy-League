import json
import pandas as pd


class Episode:
    """Class to represent a single episode of the show.

    Parameters
    ----------
    file : str
        The path to the episode data file (JSON format).

    Attributes
    ----------
    episode : int
        The episode number.
    finale : bool
        Whether this episode is the finale.
    queen_eliminated : str
        The name of the queen eliminated in this episode.
    performance : dict
        A dictionary of performance events and a list of queens associated with them. Also contains information on double shantay/sashay.
    finale_data : dict
        A dictionary containing the winner and runners-up information for the finale episode.
    """

    def __init__(self, file):
        with open(file) as f:
            data = json.load(f)

        self.episode = data["episode"]
        self.finale = data["finale"]
        self.queen_eliminated = data["queen_eliminated"]
        self.performance = data["performance"]
        self.finale_data = data["finale_data"]

    def get_episode_number(self):
        """Get the episode number."""
        return self.episode

    def is_finale(self):
        """Check if this episode is the finale."""
        return self.finale

    def get_eliminated_queen(self):
        """Get the name of the queen eliminated in this episode. Returns None if no queen was eliminated."""
        return self.queen_eliminated

    def get_performance(self):
        """Get a DataFrame of performance events and associated queens."""
        performance = self.performance
        result = []
        for k, v in performance.items():
            if isinstance(v, list) and len(v) > 0:
                for item in v:
                    result.append([k, item])

            # If there's double shantay or sashay, apply to the lip sync participants
            elif k in ["double_shantay", "double_sashay"] and v:
                for queen in performance["lip_sync_for_your_life"]:
                    result.append([k, queen])

        result = pd.DataFrame(result, columns=["event", "queen"])
        return result

    def get_finale_data(self):
        """Get the winner and runners-up information for the finale episode."""
        data = self.finale_data
        return data["winner"][0], data["runners_up"]
