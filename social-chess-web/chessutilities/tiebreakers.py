"""
Methods for resolving the ties among players trying
to get into the playoffs are complicated enough to
warrant their own module
"""
import logging
import logging.config

logger = logging.getLogger('chess')


def get_tied_list(candidate_list):
    tied_list = []
    target_score = candidate_list[0].get_weighted_score()

    for candidate in candidate_list:
        if candidate.get_weighted_score() == target_score:
            tied_list.append(candidate)

    return tied_list


def extract_using_losses(needed_number, candidates):
    """ This function gets called when we have at least
    two top players tied, but we need fewer names.
    Note that this might not work, but it will return
    a shorter list, or the original one, if it does not
    """

    playoff_list = []

    """
        for item in finalists_slots:
        logger.info(str(item))
    losses_total = 0
    for finalist_slot in finalists_slots:
        candidate_player = finalist_slot.get_player()
        logger.info("Player is {}".format(candidate_player))
        candidate_draw = candidate_player.get_draw()
        logger.info("Draw was {}".format(candidate_draw))
        losses_total += candidate_draw.get_total_loss_points()
    
    if losses_total % len(finalists_slots) == 0:
        # OK, so no differences in losses, we fail
        logger.info("There were no differences after accounting for losses")
        return change, finalists_slots
    else:
        # OK, so we have some differences
        logger.info("Let's get the list sorted by the losses.")
        new_list = sorted(finalists_slots, key=self._get_points_for_player, reverse=False)
        for lost_slot in new_list:
            lost_player = lost_slot.get_player()
            logger.info("Player: {}, Loss points: {}".format(lost_player.get_name(),
                                                             lost_player.get_draw().get_total_loss_points()))
            logger.info(lost_player.get_draw().output_win_loss_record()) 
    
    """

    return playoff_list


def get_one_playoff_contender_from_all_tied(schedule, candidates):
    """ This function gets called when we have one
    finalist so far, but we need another from the
    list of tied people below. This doesn't mean we
    will return one person. We might not be able to
    reduce the list. So we will return a list.
    """

    playoff_list = []

    # So how many have we got?
    if len(candidates) == 2:
        # OK, so just two. Let's get them

        first_player = candidates[0].get_player()
        second_player = candidates[1].get_player()

        # Test #1: Did they play each other?

        played_game = get_common_game(first_player, second_player)

        if played_game:

            if played_game.was_drawn():
                # Ugh.
                # OK, let's see if they were the same level
                if first_player.get_level() < second_player.get_level():
                    # OK, that means we give the second player a performance bonus
                    # as the underdog with same points, and he gets the slot
                    logger.info("We used a performance bonus: first greater than second in a draw")
                    playoff_list.append(first_player)
                    return playoff_list

                elif second_player.get_level() < first_player.get_level():
                    # So the other guy gets the performance bonus
                    logger.info("We used a performance bonus: third greater than second in a draw")
                    playoff_list.append(second_player)
                    return playoff_list

                else:
                    # They are the same level also. So we fail
                    logger.info("They were equal in the draw, no performance bonus")
                    playoff_list += [first_player, second_player]
                    return playoff_list

            elif played_game.did_player_id_win(first_player.get_id()):
                logger.info("First beat second. We broke a tie with the played function")
                playoff_list.append(first_player)
                return playoff_list

            else:
                logger.info("Second beat first. We broke a tie with the played function")
                playoff_list.append(second_player)

                return playoff_list

        else:
            # OK, we failed. They didn't play a game
            # But is one lower-rated than the other?
            # We will call this a performance bonus
            if first_player.get_level() < second_player.get_level():
                logger.info("{} is lower rated than {}, so he gets the slot.".format(first_player.get_name(),
                                                                                     second_player.get_name()))
                playoff_list.append(first_player)
            elif second_player.get_level() < first_player.get_level():
                logger.info("{} is lower rated than {}, so he gets the slot.".format(second_player.get_name(),
                                                                                     first_player.get_name()))
                playoff_list.append(first_player)

            playoff_list += [first_player, second_player]
            return playoff_list

    else:
        # If we are here, we have three or more who are tied
        # for the second slot. We will have to return them all
        # and allow other methods to be applied
        return candidates


def get_common_game(player_one, player_two):
    draw_in_question = player_one.get_draw()
    if not draw_in_question:
        logger.debug("Error: there is no draw object there")
    if draw_in_question.has_played_player_id(player_two.get_id()):
        # OK, so they played
        played_game = draw_in_question.get_game(player_two.get_id())
        return played_game

    return None


def _get_loss_points_for_player(item):
    return item.get_player().get_draw().get_total_loss_points()

