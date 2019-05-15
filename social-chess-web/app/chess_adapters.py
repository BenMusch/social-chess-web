from app import models, db

import chessnouns
from chessnouns import schedule, tournament, game, slot, player
from chessutilities import utilities


def player_chessnoun_from_model(p):
    """Converts a models.Player instance into player.Player"""

    return player.Player(p.id, p.name, p.level, False, p.vip)


def get_bye_player():
    return player.Player.make_bye_player()


def create_player(id, name, level):
    return player.Player(id, name, level)


def persist_game(game, **kwargs):
    """
    Given a game.Game, saves it and its nested entities to the database as a models.Game
    and returns the persisted model
    """
    try:
        white_id = game.get_white_player().get_id()
        black_id = game.get_black_player().get_id()

        player_one_draw = models.Draw(
            tournament_id=kwargs['tournament'].id,
            player_id=white_id
        )
        player_two_draw = models.Draw(
            tournament_id=kwargs['tournament'].id,
            player_id=black_id
        )
        db.session.add(player_one_draw, player_two_draw)
        db.session.commit()

        game_model = models.Game(
            player_one_id=game.get_white_player().get_id(),
            player_two_id=game.get_black_player().get_id(),
            player_one_draw_id=player_one_draw.id,
            player_two_draw_id=player_two_draw.id,
            color_code=chessnouns.PLAYER_ONE_IS_WHITE,
            bye=game.is_bye(),
            round_id=kwargs['round'].id
        )
        db.session.add(game_model)
        db.session.commit()
        return game_model
    except Exception as e:
        db.session.rollback()
        raise e


def persist_schedule(schedule_noun, **kwargs):
    """
    Given a schedule.Schedule, saves it and its nested-entities to the database as a
    models.Schedule and returns the persisted model
    """
    try:
        sched = models.Schedule(
            tournament_id=kwargs['tournament'].id,
            title=kwargs['title']
        )

        db.session.add(sched)
        db.session.commit()

        all_rounds = schedule_noun.get_rounds()
        for round_number, rounds in enumerate(all_rounds):
            round_model = models.Round(round_number=round_number + 1, schedule_id=sched.id)
            db.session.add(round_model)
            db.session.commit()
            for game in rounds:
                persist_game(game, round=round_model, tournament=kwargs['tournament'])
        return sched
    except Exception as e:
        db.session.rollback()
        raise e


def generate_schedule(players, tournament, title, num_rounds):
    """
    Given a list of models.Players and models.Tournament, uses the chess library logic
    to create database entries of the schedule and rounds
    """
    players = list(map(player_chessnoun_from_model, players))
    boards, lopsided, bye = utilities.get_number_of_boards_and_tweaks(len(players))
    sched = schedule.Schedule(players, num_rounds, lopsided, bye)

    sched.sort_players()
    sched.initialize_draws_for_players()
    sched.shuffle_players()
    sched.divide_players()
    sched.schedule_players()
    sched.assign_scheduled_games_to_draws()
    sched._print_player_draws()
    return persist_schedule(sched, tournament=tournament, title=title)


def get_rounds_for_leaderboard(schedule_identifier):

    print("ENTERING GETTING ROUNDS")
    current_dict = {}
    next_dict = {}

    #current_dict[1] = "Mark Money (W) vs. Steve Koczela (B)"
    #current_dict[2] = "Ed Lyons (W) vs. Steve Koczela (B)"

    #next_dict[1] = "Welsh Finging (W) vs.Mary Sue (B)"
    #next_dict[2] = "Tracy Corley (W) vs. Christian Greve(B)"

    scheduled_rounds = db.session.query(models.Round).filter_by(schedule_id=schedule_identifier)

    last_completed_round = 0

    # Now we need to iterate
    for ind_round in scheduled_rounds:
        # Let's get all the games for this round
        round_games = db.session.query(models.Game).filter_by(round_id=ind_round.id)
        # Let's get number of games
        number_round_games = db.session.query(models.Game).filter_by(round_id=ind_round.id).count()

        print("WE ARE LOOKING AT ROUND {} with {} games".format((last_completed_round+1), number_round_games))

        # Now let's go through them
        complete = False

        # We will go through the games
        game_count = 0
        for ind_game in round_games:
            print("Looking at game {}".format((game_count + 1)))
            if ind_game.result == chessnouns.NO_RESULT:
                # As soon as we get a no result, we bail
                break
            else:
                game_count += 1

        if game_count == number_round_games:
            # OK, round complete
            last_completed_round += 1
            continue
        else:
            # We didn't complete
            break

    # So what have we learned here?
    # Let's say the last completed round = 0

    print("Our last completed round was {}".format(last_completed_round))

    # We need to get the games again
    target_round_games = db.session.query(models.Game).filter_by(round_id=(last_completed_round + 1))

    game_count = 1
    for ind_game in target_round_games:
        # We need to create a game object
        first_player_id = ind_game.player_one_id
        second_player_id = ind_game.player_two_id

        if ind_game.color_code == chessnouns.PLAYER_ONE_IS_WHITE:
            one_white = True
            two_white = False
        else:
            one_white = False
            two_white = True

        is_bye = (ind_game.bye == 1)

        first_db_player = db.session.query(models.Player).get(first_player_id)
        first_player = create_player(first_player_id, first_db_player.name, first_db_player.level)

        second_db_player_ = db.session.query(models.Player).get(second_player_id)
        second_player = create_player(second_player_id, second_db_player_.name, second_db_player_.level)

        noun_game = game.Game(first_player, second_player, onewhite=one_white,
                              twowhite=two_white, bye=is_bye)

        # Now we need to add the result if there is one
        noun_game.set_result(ind_game.result)

        current_dict[game_count] = str(noun_game)
        game_count += 1

    if (last_completed_round < 7):
        next_round_games = db.session.query(models.Game).filter_by(round_id=(last_completed_round + 2))

        game_count = 1
        for ind_game in next_round_games:
            # We need to create a game object
            first_player_id = ind_game.player_one_id
            second_player_id = ind_game.player_two_id

            if ind_game.color_code == chessnouns.PLAYER_ONE_IS_WHITE:
                one_white = True
                two_white = False
            else:
                one_white = False
                two_white = True

            is_bye = (ind_game.bye == 1)

            first_db_player = db.session.query(models.Player).get(first_player_id)
            first_player = create_player(first_player_id, first_db_player.name, first_db_player.level)

            # Test for a bye
            if second_player_id == chessnouns.BYE_ID:
                noun_game = game.Game.create_bye_game(first_player)
            else:
                second_db_player = db.session.query(models.Player).get(second_player_id)
                second_player = create_player(second_player_id, second_db_player.name, second_db_player.level)

                noun_game = game.Game(first_player, second_player, onewhite=one_white,
                                      twowhite=two_white, bye=is_bye)

            # Now we need to add the result if there is one
            noun_game.set_result(ind_game.result)

            next_dict[game_count] = str(noun_game)
            game_count += 1


    else:
        next_round_games = {}

    return current_dict, next_dict


def get_slots_for_leaderboard(schedule_identifier):
    scheduled_rounds = db.session.query(models.Round).filter_by(schedule_id=schedule_identifier)

    # Now what we really want to do is to create a list of players, and give them all draw
    # objects. We can then use the logic in the draw objects to get the scores we want

    draw_dict = {}
    player_id_set = set()
    # Let's add a zero to the set so we don't pick up byes
    player_id_set.add(0)

    players_dict = {}
    # But let's add the bye player to the dict
    players_dict[0] = get_bye_player()

    # This is inefficient, but simpler. Let's go through all the games and
    # get the players only

    for ind_round in scheduled_rounds:
        # Let's get all the games for this round
        round_games = db.session.query(models.Game).filter_by(round_id=ind_round.id)
        # Now let's go through them
        for ind_game in round_games:

            player_one_id = ind_game.player_one_id
            if player_one_id not in player_id_set:
                # OK, get the player
                player = db.session.query(models.Player).get(player_one_id)
                players_dict[player_one_id] = create_player(player_one_id, player.name, player.level)
                player_id_set.add(player_one_id)

            player_two_id = ind_game.player_two_id
            if player_two_id not in player_id_set:
                # OK, get the player
                player = db.session.query(models.Player).get(player_two_id)
                players_dict[player_two_id] = create_player(player_two_id, player.name, player.level)
                player_id_set.add(player_two_id)

    # Now we will initialize draws for all players
    for ind_player_id in players_dict.keys():
        players_dict[ind_player_id].set_draw(0)

    # Now we can go through all the games and fill out the draws
    for ind_round in scheduled_rounds:
        # Let's get all the games for this round
        round_games = db.session.query(models.Game).filter_by(round_id=ind_round.id)
        # Now let's go through them
        for ind_game in round_games:

            # If the game doesn't have a result, don't add it:
            if ind_game.result == chessnouns.NO_RESULT:
                continue

            # We need to create a game object
            first_player_id = ind_game.player_one_id
            second_player_id = ind_game.player_two_id

            if ind_game.color_code == chessnouns.PLAYER_ONE_IS_WHITE:
                one_white = True
                two_white = False
            else:
                one_white = False
                two_white = True

            is_bye = (ind_game.bye == 1)

            first_player = players_dict[first_player_id]
            second_player = players_dict[second_player_id]

            noun_game = game.Game(first_player, second_player, onewhite=one_white,
                                  twowhite=two_white, bye=is_bye)

            # Now we need to add the result if there is one
            noun_game.set_result(ind_game.result)

            first_player.get_draw().add_game_with_game(noun_game)
            if second_player.get_id() != chessnouns.BYE_ID:
                second_player.get_draw().add_game_with_game(noun_game)

    slot_tuple_list = []

    # This will be the end
    for ind_player_key, ind_player in players_dict.items():
        if ind_player_key == chessnouns.BYE_ID:
            continue
        ind_draw = ind_player.get_draw()
        raw_points = ind_draw.get_total_raw_points()
        weighted_points = ind_draw.get_total_weighted_score()
        rounds_completed = ind_draw.get_number_of_rounds_completed()

        # We need to use the Slot class not just for convenience, but because
        # it has a sort feature we need
        slot_tuple_list.append(slot.Slot(ind_player, rounds_completed, raw_points,
                                         str(round(weighted_points, chessnouns.WEIGHTED_SCORE_DECIMAL_PRECISION))))

    return sorted(slot_tuple_list)
