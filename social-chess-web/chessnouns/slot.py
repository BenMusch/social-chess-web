import functools


@functools.total_ordering  # This is to help sort methods at bottom
class Slot(object):
    """
    This class is just a place on the leaderboard
    """

    def __init__(self, slot_player, rounds_completed, raw_points, weighted_points):
        self._player = slot_player
        self._rounds = rounds_completed
        self._raw_points = raw_points
        self._weighted_points = weighted_points

    def __str__(self):
        return "{} | Rd:{} | Rp:{} | Wp:{} ".format(self._player.get_name(), self._rounds, self._raw_points,
                                                    self._weighted_points)

    def __repr__(self):
        return "{} | Rd:{} | Rp:{} | Wp:{} ".format(self._player.get_name(), self._rounds, self._raw_points,
                                                    self._weighted_points)

    def get_line(self):
        """
        This will return a tuple that corresponds to the three values
        :return: tuple of attributes
        """
        return self._player.get_name(), self._rounds, self._raw_points, self._weighted_points

    def get_weighted_score(self):
        return self._weighted_points

    def get_raw_points(self):
        return self._raw_points


    def get_player(self):
        return self._player

    def get_rounds_completed(self):
        return self._rounds

    """
    These two methods will ensure a list of these is sorted by weighted points
    """

    def __lt__(self, other):
        return other._weighted_points < self._weighted_points

    def __eq__(self, other):
        return self._weighted_points == other._weighted_points
