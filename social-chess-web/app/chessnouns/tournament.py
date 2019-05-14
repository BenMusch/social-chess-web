"""
This class will keep track of an individual tournament
"""
import chessnouns
from . import slot
from . import player
from . import game
from datetime import date
from chessutilities import tiebreakers
import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('tournament')


class Tournament(object):

    def __init__(self, schedule, tournament_name, tournament_date=None):

        # The draw dictionary has the player ids
        # as keys, and the draw objects as values

        if not tournament_date:
            self._event_date = date.today()
        else:
            self._event_date = tournament_date

        self._name = tournament_name
        self._schedule = schedule
        self._playoff = None  # This will just be a game
        self._winner = None  # This will be the id of the winner

        # Now we need to build a dictionary for the players,
        # where the the key is the id, value is the draw
        self._tournament_draw_dict = {ind_player.get_id(): ind_player.get_draw() for ind_player in
                                      self._schedule.get_players()}

    def create_random_results_all(self):

        rounds = self._schedule.get_rounds()
        count = 1
        logger.debug("Creating random results in round {}".format(count))
        for ind_round in rounds:
            self.create_random_results_for_round(ind_round)

    def create_random_results_for_round(self, tournament_round):

        for ind_game in tournament_round:
            logger.debug("Setting result for game: {} ".format(ind_game))
            ind_game.set_likely_random_result()
            logger.debug("Result: {} vs ")

    def return_result_numbers(self):
        """
        This method is just a check on the data.
        It will return wins, losses, and draws for
        the tournament.

        If there are no draws, it should return
        40 wins, 40 losses for 40 games, etc.

        """
        wins = 0
        byes = 0
        losses = 0
        draws = 0

        for player_key, draw in self._tournament_draw_dict.items():
            for ind_game in draw.get_games():
                if ind_game.was_drawn():
                    draws += 1
                elif ind_game.was_bye():
                    byes += 1
                elif ind_game.did_player_id_win(player_key):
                    wins += 1
                else:
                    losses += 1

        return wins, byes, losses, draws

    def get_total_number_of_games(self):
        return self._schedule.get_total_number_of_games()

    def get_leaderboard(self, maximum_number=0):
        """
        This method will return a list of tuples, sorted

        We will go through the draw dictionary, tally up the score, and then
        add the entries to a list of slot objects, and then sort them

        """

        slot_list = []
        for player_key, draw in self._tournament_draw_dict.items():
            tourney_player = self._schedule.get_scheduled_player_for_id(player_key)
            raw_points = draw.get_total_raw_points()
            weighted_points = draw.get_total_weighted_score()
            rounds_completed = draw.get_number_of_rounds_completed()
            slot_list.append(slot.Slot(tourney_player, rounds_completed, raw_points,
                                       str(round(weighted_points, chessnouns.WEIGHTED_SCORE_DECIMAL_PRECISION))))

        if maximum_number == 0:
            # We are saying 0 means return all of them
            return sorted(slot_list)
        else:
            # So we only want the top X players
            return sorted(slot_list)[:maximum_number]

    def calculate_playoff_candidates(self):
        """
        Here we are trying to figure out the top two people,
        or, if there are ties, the people tied for the top
        two slots
        :return bool, list - we are returning True if we used
        tiebreaks, false if not, and then a list of finalists
        """

        # We want to track how often we use tiebreaks, so we
        # will return one of these values. We are using
        # these variable names to make the code more readable
        # and less subject to error

        we_used_tiebreaks = True
        did_not_use_tiebreaks = False

        finalists = []

        # First, let's get the list
        leader_list = sorted(self.get_leaderboard())

        logger.info("\nHere is the leaderboard going into this:\n")
        logger.info(leader_list)

        """ We are going to get the first person, who is
        going to have the highest score, but they might 
        not be the only person with that score. """
        top_person = leader_list[0]
        top_score = top_person.get_weighted_score()
        logger.debug("Top score was: {}".format(top_score))

        """What we need to know now is if he's alone
         at the top of the leaderboard."""

        next_person = leader_list[1]
        next_score = next_person.get_weighted_score()
        logger.debug("Next score was: {}".format(next_score))

        third_person = leader_list[2]
        third_score = third_person.get_weighted_score()
        logger.debug("Third score was: {}".format(third_score))

        # Let us see if the first person is alone
        if top_score > next_score:
            # OK, leader is alone, so add him
            finalists.append(top_person)

            # But now we need to know if there are ties beneath him
            if next_score > third_score:
                # Great, then we can just add the second and be done
                finalists.append(next_person)
                return did_not_use_tiebreaks, finalists
            else:
                # So we are in a situation where the first guy is alone,
                # but the next two (or more) are tied
                # So let's pop off the first guy, and send the list
                # for processing
                leader_list.pop(0)

                # Let's get just the tied ones
                tied_list = tiebreakers.get_tied_list(leader_list)
                outstanding_list = tiebreakers.get_one_playoff_contender_from_all_tied(self._schedule, tied_list)
                if len(outstanding_list) == 1:
                    finalists.append(outstanding_list[0])
                    return we_used_tiebreaks, finalists
                else:
                    # So we still have more than one. Let's see if we can get just
                    # one by calculating against losses
                    loss_calculated_list = tiebreakers.extract_using_losses(1, outstanding_list)
                    return we_used_tiebreaks, loss_calculated_list

        # So now we are looking at the possibility of multiple people tied at the top
        elif top_score == next_score:

            # We need to see if the third one is lower,
            #    simplifying things
            if next_score > third_score:
                finalists.append(top_person)
                finalists.append(next_person)
                return did_not_use_tiebreaks, finalists
            else:
                # Everyone is tied at the top
                # We will use a function to resolve and try to get 2

                # But first we need to just get the tied players at the top
                tied_list = tiebreakers.get_tied_list(leader_list)
                loss_calculated_list = tiebreakers.extract_using_losses(2, tied_list)
                return we_used_tiebreaks, loss_calculated_list
