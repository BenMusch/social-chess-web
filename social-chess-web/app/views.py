from flask import render_template
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, ModelRestApi, SimpleFormView
from . import appbuilder, db

import chessnouns
from chessnouns import player, schedule, tournament
from chessutilities import utilities

from app.models import Player, Tournament, Schedule, Round, Draw, Game
from app.forms import ScheduleForm


"""
    Application wide 404 error handler
"""

class PlayerView(ModelView):
    datamodel = SQLAInterface(Player)
    list_columns = ['name', 'level']

class ScheduleView(ModelView):
    datamodel = SQLAInterface(Schedule)
    list_columns = ['title']

class TournamentView(ModelView):
    datamodel = SQLAInterface(Tournament)
    list_columns = ['title']

class GameView(ModelView):
    datamodel = SQLAInterface(Game)
    list_columns = ['id']


class RoundView(ModelView):
    datamodel = SQLAInterface(Round)
    list_columns = ['id']


class DrawView(ModelView):
    datamodel = SQLAInterface(Draw)
    list_columns = ['id']


class CreateScheduleView(SimpleFormView):
    form = ScheduleForm
    form_title = 'Create a schedule containing the selected players'

    def form_post(self, form):
        import pdb; pdb.set_trace()
        players = db.session.query(Player).filter(Player.id.in_(form.players.data)).all()

        def make_chessnoun(p):
            return player.Player(p.id, p.name, level=p.level, vip=p.vip)

        players = list(map(make_chessnoun, players))
        boards, lopsided, bye = utilities.get_number_of_boards_and_tweaks(len(players))
        sched = schedule.Schedule(
            players, chessnouns.DEFAULT_NUMBER_OF_ROUNDS, lopsided, bye
        )
        sched.sort_players()
        sched.initialize_draws_for_players()
        sched.shuffle_players()
        a, b = sched.divide_players()
        sched.schedule_players()
        sched.assign_scheduled_games_to_draws()
        sched._print_player_draws()
        all_rounds = sched.get_rounds()

        for round_number, rounds in all_rounds:
            db.sesion.add(round_obj)
            db.session.commit()


@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )


db.create_all()

appbuilder.add_view(
    PlayerView,
    "Players",
    icon = "fa-folder-open-o",
    category = "Menu"
)

appbuilder.add_view(
    TournamentView,
    "Tournaments",
    icon = "fa-folder-open-o",
    category = "Menu"
)

appbuilder.add_view(
    ScheduleView,
    "Schedules",
    icon = "fa-folder-open-o",
    category = "Menu"
)

appbuilder.add_view(
    RoundView,
    "Rounds",
    icon = "fa-folder-open-o",
    category = "Menu"
)

appbuilder.add_view(
    GameView,
    "Games",
    icon = "fa-folder-open-o",
    category = "Menu"
)

appbuilder.add_view(
    DrawView,
    "Draws",
    icon = "fa-folder-open-o",
    category = "Menu"
)

appbuilder.add_view(
    CreateScheduleView,
    "Schedule Generator",
    icon = "fa-plus",
    category = "Menu"
)
