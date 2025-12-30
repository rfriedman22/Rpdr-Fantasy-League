import pandas as pd


class Queen:
    """The class for managing a queen on the cast in a season of RuPaul's Drag Race.

    Parameters
    ----------
    name : str
        The name of the queen.

    Attributes
    ----------
    name : str
        The name of the queen.
    week_eliminated : int or None
        The week the queen was eliminated, or None if she is still in the competition.
    rank : int
        The rank of the queen in the competition (1 for winner, 2 for runner-up, etc.). 0 if still competing.
    performance_events : dict
        A dictionary mapping week numbers to lists of performance events for that week.
    """

    def __init__(self, name):
        self.name = name
        self.week_eliminated = None
        self.rank = 0
        self.performance_events = {}

    def get_name(self):
        """Get the name of the queen."""
        return self.name

    def get_week_eliminated(self):
        """Get the week the queen was eliminated, or None if still competing."""
        return self.week_eliminated

    def is_eliminated(self):
        """Check if the queen has been eliminated."""
        return self.week_eliminated is not None

    def get_rank(self):
        """Get the rank of the queen in the competition."""
        return self.rank

    def get_performance_events(self):
        """Get all performance events for the queen as a DataFrame."""
        events = []
        for week, event_list in self.performance_events.items():
            for e in event_list:
                events.append((week, e))
        events = pd.DataFrame(events, columns=["week", "event"])
        return events

    def eliminate(self, week, rank):
        """Eliminate the queen from the competition. Log the week and rank."""
        self.week_eliminated = week
        self.rank = rank

    def add_performance_event(self, event, week):
        """Add a performance event for the queen in a specific week."""
        if week in self.performance_events:
            self.performance_events[week].append(event)
        else:
            self.performance_events[week] = [event]
