import chessnouns
from chessnouns import player
import random
from chessexceptions import game_error
import logging.config

logger = logging.getLogger('main')


class Game(object):
    """
    This will represent a game. It is one of the most
    important core components of the system.

    Some things:

    1. You initialize a game with the two players
    2. You do not choose the colors at that time.
    3. You can initialize a game as a bye

    """

    @classmethod
    def create_bye_game(cls, player_getting_bye, onewhite=True, twowhite=False):
        return Game(player_getting_bye, player.Player.make_bye_player(), onewhite=onewhite, twowhite=twowhite, bye=True)

    def __str__(self):

        # The complexity here is about whether we want to show levels in the output
        if chessnouns.SHOW_LEVELS:
            level_string = "({})"
        else:
            level_string = "{}"

        # We need to handle bye
        if self._player_two.get_id() == chessnouns.BYE_ID:
            # OK we have one
            return "{} has a bye".format(self._player_one.get_name())


        # # Brian Jencunas(3)[N] vs. Christian Greve(4)[N]
        if self._color_code == chessnouns.NO_COLOR_SELECTED:
            return_line = "{}".format(self._player_one.get_name())
            return_line += level_string.format(self._player_one.get_level() if chessnouns.SHOW_LEVELS else "")
            return_line += "[N] vs. {}".format(self._player_two.get_name())
            return_line += level_string.format(self._player_two.get_level() if chessnouns.SHOW_LEVELS else "")
            return_line += "[N]"

        # Brian Jencunas(3)[W] vs. Christian Greve(4)[B]
        elif self._color_code == chessnouns.PLAYER_ONE_IS_WHITE:
            return_line = "{}".format(self._player_one.get_name())
            return_line += level_string.format(self._player_one.get_level() if chessnouns.SHOW_LEVELS else "")
            return_line += "[W] vs. {}".format(self._player_two.get_name())
            return_line += level_string.format(self._player_two.get_level() if chessnouns.SHOW_LEVELS else "")
            return_line += "[B]"

        # Brian Jencunas(3)[W] vs. Christian Greve(4)[B]
        else:
            return_line = "{}".format(self._player_two.get_name())
            return_line += level_string.format(self._player_two.get_level() if chessnouns.SHOW_LEVELS else "")
            return_line += "[W] vs. {}".format(self._player_one.get_name())
            return_line += level_string.format(self._player_one.get_level() if chessnouns.SHOW_LEVELS else "")
            return_line += "[B]"

        return return_line

    def __repr__(self):
        return self.__str__()

    def get_leaderboard_string_white_first(self):
        """
        This will be a white-first rendering of the game
        for the leaderboard
        """

        # We need to handle bye
        if self._player_two.get_id() == chessnouns.BYE_ID:
            # OK we have one
            return "{} | Bye".format(self._player_one.get_name())

        white = self.get_white_player()
        black = self.get_black_player()
        return "{} vs. {}".format(white.get_name(), black.get_name())

    def get_leaderboard_array_white_first(self):

        if self._player_two.get_id() == chessnouns.BYE_ID:
            # OK we have one
            return [self._player_one.get_name(), chessnouns.BYE_NAME]
        else:
            white = self.get_white_player()
            black = self.get_black_player()
            return [white.get_name(), black.get_name()]


    def make_player_one_white(self):
        self._color_code = chessnouns.PLAYER_ONE_IS_WHITE

    def make_player_two_white(self):
        self._color_code = chessnouns.PLAYER_ONE_IS_BLACK

    def get_game_points(self):
        return int(self._player_one.get_level()) + int(self._player_two.get_level())

    def __init__(self, player_one, player_two, time=chessnouns.STANDARD_GAME_TIME,
                 onewhite=False, twowhite=False, bye=False):

        self._bye = bye
        self._player_one = player_one
        self._player_two = player_two
        self._result = chessnouns.NO_RESULT
        self._game_time = time

        if onewhite:
            self._color_code = chessnouns.PLAYER_ONE_IS_WHITE
        elif twowhite:
            self._color_code = chessnouns.PLAYER_ONE_IS_BLACK
        else:
            self._color_code = chessnouns.NO_COLOR_SELECTED

    def are_colors_set(self):
        return self._color_code != chessnouns.NO_COLOR_SELECTED

    def set_random_color(self):

        r1 = random.randint(0, 2)

        if r1 == 1:
            self._color_code = chessnouns.PLAYER_ONE_IS_WHITE
        else:
            self._color_code = chessnouns.PLAYER_ONE_IS_BLACK

    def set_random_result(self):

        r1 = random.randint(1, 11)

        if r1 == 1:
            self._result = chessnouns.DRAW
        elif r1 < 6:
            self._result = chessnouns.BLACK_WINS
        else:
            self._result = chessnouns.WHITE_WINS

    def _tally_player_win(self, winning_player):
        """
        This method is used as an internal function
        that assigns the win to the right player and
        color
        :param winning_player:
        :return:
        """

        if self.get_white_player().get_id() == winning_player.get_id():
            self._result = chessnouns.WHITE_WINS
        else:
            # So he's black
            self._result = chessnouns.BLACK_WINS

    def set_likely_random_result(self):
        """
        This is an improvement on the random result generator
        that will acknowledge that the more experienced player
        usually will win
        """

        first_player_level = self._player_one.get_level()
        second_player_level = self._player_two.get_level()

        # Let's get the draw out of the way - very unlikely
        try_draw_number = random.randint(1, 90)

        if try_draw_number == 1:
            self._result = chessnouns.DRAW
            return

        num = random.randint(1, 10)

        if first_player_level > second_player_level:
            # So the first player is more likely to win
            # let's see if he does
            if num > 3:  # yes
                self._tally_player_win(self._player_one)

            else:  # no
                self._tally_player_win(self._player_two)

        elif second_player_level > first_player_level:
            # So the second player is more likely to win
            # let's see if he does
            if num > 3:  # yes
                self._tally_player_win(self._player_two)
            else:  # no
                self._tally_player_win(self._player_one)

        else:
            # So they are evenly matched
            even_number = random.randint(1, 2)
            if even_number == 1:
                self._tally_player_win(self._player_one)
            else:
                self._tally_player_win(self._player_two)

    def set_random_colors(self):

        r1 = random.randint(1, 2)

        if r1 == 1:
            self._color_code = chessnouns.PLAYER_ONE_IS_WHITE
        else:
            self._color_code = chessnouns.PLAYER_ONE_IS_BLACK

    def contains_player(self, candidate_player):
        return self._player_one == candidate_player or self._player_two == candidate_player

    def get_opposing_player_of_id(self, identifier):
        if self._player_one.get_id() == identifier:
            return self._player_two
        else:
            return self._player_one

    def is_bye(self):
        return self._bye

    def get_players(self):
        return [self._player_one, self._player_two]

    def is_game_over(self):
        return self._result != chessnouns.NO_RESULT

    def flip_colors(self):

        if self._color_code == chessnouns.NO_COLOR_SELECTED:
            raise game_error.GameError("You cannot flip colors before selecting them")
        elif self._color_code == chessnouns.PLAYER_ONE_IS_WHITE:
            self._color_code = chessnouns.PLAYER_ONE_IS_BLACK
        else:
            self._color_code = chessnouns.PLAYER_ONE_IS_WHITE

    def get_white_player(self):
        if self._color_code == chessnouns.NO_COLOR_SELECTED:
            raise game_error.GameError("You cannot get the white player without selecting colors")
        if self._color_code == chessnouns.PLAYER_ONE_IS_WHITE:
            return self._player_one
        else:
            return self._player_two

    def get_black_player(self):
        if self._color_code == chessnouns.NO_COLOR_SELECTED:
            raise game_error.GameError("You cannot get the black player without selecting colors")
        if self._color_code == chessnouns.PLAYER_ONE_IS_BLACK:
            return self._player_one
        else:
            return self._player_two

    def set_time(self, time):
        self._game_time = time

    def get_time(self):
        return self._game_time

    def set_result(self, result):
        self._result = result

    def get_result(self):
        return self._result

    def was_drawn(self):
        return self._result == chessnouns.DRAW

    def was_bye(self):
        return self._bye

    def did_player_id_win(self, player_id):
        winner, _ = self.get_winning_and_losing_player()
        return player_id == winner.get_id()

    def get_players_result_string(self):

        if self._result == chessnouns.DRAW:
            winner = self.get_white_player()
            loser = self.get_black_player()
            outcome_string = "draw"
            color_string = "white"
        else:

            winner, loser  = self.get_winning_and_losing_player()
            if self._result == chessnouns.WHITE_WINS:
                outcome_string = "won"
                color_string = "white"
            else:
                outcome_string = "won"
                color_string = "black"

        result_string = "{}({}) {} as {} vs. {}({})".format(winner.get_name(), winner.get_level(), outcome_string,
                                                            color_string, loser.get_name(), loser.get_level())

        return result_string



    def get_winning_and_losing_player(self):

        if self._result == chessnouns.DRAW:
            raise game_error.GameError("You must check for a draw before seeking a winner")

        if self._bye is True:
            return self._player_one, player.Player.make_bye_player()

        if self._color_code == chessnouns.NO_COLOR_SELECTED:
            raise game_error.GameError("You cannot get the winning player without selecting colors")
        if self._result == chessnouns.NO_RESULT:
            raise game_error.GameError("You cannot get the winning player without a result")
        if self._color_code == chessnouns.PLAYER_ONE_IS_WHITE and self._result == chessnouns.WHITE_WINS:
            return self._player_one, self._player_two
        else:
            return self._player_two, self._player_one
