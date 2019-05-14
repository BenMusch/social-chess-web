import traceback

from flask import render_template, flash
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, ModelRestApi, SimpleFormView

from . import appbuilder, db, chess_adapters
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
        players = db.session.query(Player).filter(Player.id.in_(form.players.data)).all()
        tournament = db.session.query(Tournament).get(form.tournament.data)
        try:
            chess_adapters.generate_schedule(
                players, tournament, form.name.data, form.num_rounds.data
            )
            flash("Schedule created", "info")
        except Exception as e:
            traceback.print_exc()
            flash("Error creating schedule: %s" % str(e), "error")


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
