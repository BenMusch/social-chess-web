from . import player, game
from chessutilities import utilities
import chessnouns
from chessexceptions import game_error
import logging
import logging.config

logger = logging.getLogger('main')


class Draw(object):
    """
    The draw will be the lineup that a player has in a
    tournament. It will be used in creating the schedule,
    in order to help figure out who needs to be paired,
    and it will also be used during a tournament to the
    matches for a player
    """

    def __init__(self, player_for_draw, number_rounds):
        logger.debug("Draw initialized for {}({}) ".format(player_for_draw.get_name(), player_for_draw.get_level()))
        self._games = list()
        # print("Number of matchups at init is {} ".format(len(self._matchups)))
        assert isinstance(player_for_draw, player.Player)
        self._draw_player = player_for_draw
        self._number_of_rounds = number_rounds

    def __str__(self):
        return_line = "{}'s ({}) Draw--- ".format(self._draw_player.get_name(), self._draw_player.get_level(), end="++")
        for ind_game in self._games:
            players = ind_game.get_players()
            if players[0].get_id() == self._draw_player.get_id():
                # Then player one is ours
                opposing_player = players[1]
            else:
                opposing_player = players[0]

            if ind_game.are_colors_set():
                white = ind_game.get_white_player()
                if white == self._draw_player:
                    color_string = "W vs."
                else:
                    color_string = "B vs."
            else:
                color_string = "NC vs."

            return_line += color_string + " "
            return_line += opposing_player.get_name() + "({}) ".format(opposing_player.get_level()) + " | "

        return return_line

    def output_win_loss_record(self):

        logger.info("Creating win/loss record for {} ".format(self._draw_player.get_name()))

        return_string = ""

        player_id = self._draw_player.get_id()

        round_number = 1
        for ind_game in self._games:
            opposing_player = ind_game.get_opposing_player_of_id(player_id)
            if ind_game.was_drawn():
                return_string += "\nRound {} was a draw against: {} L{}\n".format(round_number,
                                                                                opposing_player.get_name(),
                                                                                opposing_player.get_level())
            elif ind_game.did_player_id_win(player_id):
                return_string += "Round {} was a win against {} L{}\n".format(round_number, opposing_player.get_name(),
                                                                              opposing_player.get_level())
            else:
                return_string += "Round {} was a loss against {} L{}\n".format(round_number, opposing_player.get_name(),
                                                                               opposing_player.get_level())

        return return_string

    def get_number_of_rounds(self):
        return self._number_of_rounds

    def get_number_of_rounds_completed(self):
        return len(self._games)

    def get_rounds_left(self):
        return self._number_of_rounds - len(self._games)

    def get_games(self):
        return self._games

    def number_games_scheduled(self):
        return len(self._games)

    def add_game_by_player(self, opposing_player):
        assert isinstance(opposing_player, player.Player)
        self._games.append(game.Game(self._draw_player, opposing_player))

    def add_game_with_game(self, game_to_add):
        assert isinstance(game_to_add, game.Game)
        self._games.append(game_to_add)

    def add_bye(self):

        self._games.append(game.Game.create_bye_game(self._draw_player))

    def clear_games(self):
        self._games = []

    def has_full_draw(self):
        logger.debug("{} has {} matchups in rounds {} ".format(self._draw_player.get_name(), len(self._games),
                                                               self._number_of_rounds))
        return len(self._games) >= self._number_of_rounds

    def get_player(self):
        return self._draw_player

    def flip_color_two_games(self):
        self._games[0].flip_colors()
        self._games[1].flip_colors()

    def get_total_loss_points(self):

        logger.info("Looking at loss points for {} ".format(self._draw_player.get_name()))
        loss_points = 0
        player_id = self._draw_player.get_id()

        for ind_game in self._games:
            if ind_game.get_result() == chessnouns.NO_RESULT:
                continue
            elif ind_game.was_drawn():
                continue
            elif ind_game.was_bye():
                continue
            elif ind_game.did_player_id_win(player_id):
                continue
            else:
                # OK, a loss
                _, loser = ind_game.get_winning_and_losing_player()
                logger.info("{} lost against {}, a level {}".format(self._draw_player.get_name(), loser.get_name(),
                                                                    loser.get_level()))
                loss_points += loser.get_level()

        logger.info("Total loss points were: {}".format(loss_points))
        return loss_points

    def is_all_one_color(self):
        """
        This function finds out if someone's draw is them being all one color
        :return:
        """
        whites = 0
        blacks = 0
        for ind_game in self._games:
            players = ind_game.get_players()
            if players[0].get_id() == self._draw_player.get_id():
                # Then player one is ours
                if ind_game.get_white_player() == self._draw_player:
                    whites += 1
                else:
                    blacks += 1
            else:
                # So player Two is ours
                if ind_game.get_black_player() == self._draw_player:
                    blacks += 1
                else:
                    whites += 1

        if whites == chessnouns.DEFAULT_NUMBER_OF_GAMES or blacks == chessnouns.DEFAULT_NUMBER_OF_GAMES:
            logger.info("Someone had all one color")
            return True
        else:

            return False

    def has_played_player_id(self, id):
        """
        This is a convenience method for
        checking to see if someone has already been scheduled
        :param id: id
        :return: bool
        """
        for ind_game in self._games:
            players = ind_game.get_players()
            if players[0].get_id() == self._draw_player.get_id():
                # Then player one is ours
                opposing_player = players[1]
            else:
                opposing_player = players[0]
            if id == opposing_player.get_id():
                return True

        return False

    def get_game_for_player(self, opposing_player):
        pass

    def _get_points_for_level(self, level):
        """
        This gets used when an upset is over and
        we just need the points for that level

        """
        if level == chessnouns.KING:
            return chessnouns.LEVEL_FIVE_LEVEL_WIN
        elif level == chessnouns.KNIGHT:
            return chessnouns.LEVEL_FOUR_LEVEL_WIN
        elif level == chessnouns.ADEPT:
            return chessnouns.LEVEL_THREE_LEVEL_WIN
        elif level == chessnouns.IMPROVING:
            return chessnouns.LEVEL_TWO_LEVEL_WIN
        else:
            return chessnouns.LEVEL_ONE_LEVEL_WIN

    def _get_points_for_upset(self, level):

        if level == chessnouns.KING:
            return chessnouns.LEVEL_FOUR_UPSET_WIN
        elif level == chessnouns.KNIGHT:
            return chessnouns.LEVEL_THREE_UPSET_WIN
        elif level == chessnouns.ADEPT:
            return chessnouns.LEVEL_TWO_UPSET_WIN
        else:
            return chessnouns.LEVEL_ONE_UPSET_WIN

    def get_total_weighted_score(self):

        weighted_points = 0

        if not self.get_games():
            return 0

        """
        if self.number_games_scheduled() == 0:
            raise game_error.GameError("You cannot calculate a score without games")
        """

        for individual_game in self.get_games():
            if individual_game.get_result() == chessnouns.NO_RESULT:
                continue
            if individual_game.get_result() == chessnouns.DRAW:
                # OK, so there is a draw
                weighted_points += 0.5
                continue

            winning_player, losing_player = individual_game.get_winning_and_losing_player()

            if winning_player.get_name() == self._draw_player.get_name():
                # OK, so we won
                my_level = self._draw_player.get_level()
                other_level = losing_player.get_level()

                if my_level == chessnouns.KING:
                    weighted_points += self._get_points_for_level(other_level)

                elif my_level == chessnouns.KNIGHT:
                    if other_level == chessnouns.KING:
                        weighted_points += self._get_points_for_upset(other_level)
                    else:
                        weighted_points += self._get_points_for_level(other_level)

                elif my_level == chessnouns.ADEPT:
                    if other_level >= chessnouns.KNIGHT:
                        weighted_points += self._get_points_for_upset(other_level)
                    else:
                        weighted_points += self._get_points_for_level(other_level)

                elif my_level == chessnouns.IMPROVING:
                    if other_level >= chessnouns.ADEPT:
                        weighted_points += self._get_points_for_upset(other_level)
                    else:
                        weighted_points += self._get_points_for_level(other_level)

                elif my_level == chessnouns.BEGINNER:
                    if other_level >= chessnouns.IMPROVING:
                        weighted_points += self._get_points_for_upset(other_level)
                    else:
                        weighted_points += self._get_points_for_level(other_level)

        return weighted_points

    def get_total_raw_points(self):

        raw_points = 0

        # FIXME: Do we want to check this in a different way?
        """
        if self.number_games_scheduled() == 0:
            raise game_error.GameError("You cannot calculate a score without games")
        """

        if not self.get_games():
            return 0

        count = 0
        for individual_game in self.get_games():
            count += 1
            logger.debug("Entering game {} ".format(count))
            if individual_game.get_result() == chessnouns.NO_RESULT:
                logger.debug("No result yet")
                continue
            if individual_game.get_result() == chessnouns.DRAW:
                logger.debug("It was a draw")
                # OK, so there is a draw
                # print("It was a draw")
                raw_points += 0.5
                continue

            winning_player, losing_player = individual_game.get_winning_and_losing_player()

            logger.debug("Checking out winner and loser")
            if winning_player.get_name() == self._draw_player.get_name():
                logger.debug("It was a win for {}({}) ".format(winning_player.get_name(), winning_player.get_level()))
                logger.debug("It was against: {}({}) ".format(losing_player.get_name(), losing_player.get_level()))
                raw_points += 1

        return raw_points
