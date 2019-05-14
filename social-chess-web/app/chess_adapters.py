from app import models, db

import chessnouns
from chessnouns import player, schedule, tournament
from chessutilities import utilities


def player_chessnoun_from_model(p):
    """Converts a models.Player instance into player.Player"""
    return player.Player(p.id, p.name, p.level, False, p.vip)


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


MODEL_CONVERTERS = {
    models.Player: player_chessnoun_from_model,
}


def chessnoun_from_model(model):
    fun = MODEL_CONVERTERS.get(type(model))

    if fun is None: raise ValueError("Cannot convert type %s" % type(model))
    return fun(model)


def generate_schedule(players, tournament, title):
    """
    Given a list of models.Players and models.Tournament, uses the chess library logic
    to create database entries of the schedule and rounds
    """
    players = list(map(chessnoun_from_model, players))
    boards, lopsided, bye = utilities.get_number_of_boards_and_tweaks(len(players))
    sched = schedule.Schedule(
        players, chessnouns.DEFAULT_NUMBER_OF_ROUNDS, lopsided, bye
    )

    sched.sort_players()
    sched.initialize_draws_for_players()
    sched.shuffle_players()
    sched.divide_players()
    sched.schedule_players()
    sched.assign_scheduled_games_to_draws()
    sched._print_player_draws()
    return persist_schedule(sched, tournament=tournament, title=title)
