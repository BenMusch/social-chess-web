import traceback

from flask import render_template, flash
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, ModelRestApi, SimpleFormView, BaseView, expose
from wtforms import fields, validators

from . import appbuilder, db, chess_adapters
from app.models import Player, Tournament, Schedule, Round, Draw, Game
from app.forms import ScheduleForm, get_enum_field
from app.index import MyIndexView
import chessnouns

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
    list_columns = ['id', 'round_number', 'first_player', 'second_player', 'outcome']

    _result_choices = [
        (chessnouns.NO_RESULT, 'No result'),
        (chessnouns.WHITE_WINS, 'White wins'),
        (chessnouns.BLACK_WINS, 'Black wins'),
        (chessnouns.DRAW, 'Draw')
    ]
    _result_field = get_enum_field(_result_choices, chessnouns.NO_RESULT)

    show_fieldsets = [
        (
            'Summary',
            {'fields': ['first_player', 'second_player', 'outcome']}
        ),
    ]

    _color_code_choices = [
        (chessnouns.PLAYER_ONE_IS_WHITE, 'Player 1 is white'),
        (chessnouns.PLAYER_ONE_IS_BLACK, 'Player 1 is black'),
        (chessnouns.NO_COLOR_SELECTED, 'No color selected')
    ]
    _color_code_field = get_enum_field(_color_code_choices)

    edit_form_extra_fields = {'result': _result_field, 'color_code': _color_code_field}
    add_form_extra_fields = {'result': _result_field, 'color_code': _color_code_field}


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


class LeaderboardView(BaseView):
    route_base = "/leaderboardview"

    @expose('/current/<int:schedule_identifier>')
    def current(self, schedule_identifier):

        number_rounds = chessnouns.DEFAULT_NUMBER_OF_ROUNDS

        # So now we need to get the scheduled rounds
        current_round, current_round_dict, next_round_dict = chess_adapters.get_rounds_for_leaderboard(schedule_identifier)

        if current_round < number_rounds:
            next_round = current_round + 1
        else:
            next_round = current_round

        # Now we need two dictionaries
        # [board] [game string]

        current_round_time = ""
        next_round_time = ""

        if (current_round == 1):
            current_round_time = "6:00 pm"
            next_round_time = "6:15 pm"
        elif (current_round == 2):
            current_round_time = "6:15 pm"
            next_round_time = "6:30 pm"
        elif (current_round == 3):
            current_round_time = "6:30 pm"
            next_round_time = "6:45 pm"
        elif (current_round == 4):
            current_round_time = "6:45 pm"
            next_round_time = "7:00 pm"
        elif (current_round == 5):
            current_round_time = "7:00 pm"
            next_round_time = "7:15 pm"
        elif (current_round == 6):
            current_round_time = "7:15 pm"
            next_round_time = "7:30 pm"
        elif (current_round == 7):
            current_round_time = "7:30 pm"
            next_round_time = "7:45 pm"
        else:
            current_round_time = "7:45 pm"
            next_round_time = "8:00 pm"

        slot_list = chess_adapters.get_slots_for_leaderboard(schedule_identifier)
        return self.render_template("board.html", slot_list=slot_list, current_round=current_round,
                                    next_round=next_round,current_round_dict=current_round_dict,
                                    next_round_dict=next_round_dict, current_round_time=current_round_time,
                                    next_round_time=next_round_time)


@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )


db.create_all()

appbuilder.add_view_no_menu(LeaderboardView())

appbuilder.add_view(
    PlayerView,
    "Players",
    icon="fa-folder-open-o",
    category="Menu"
)

appbuilder.add_view(
    TournamentView,
    "Tournaments",
    icon="fa-folder-open-o",
    category="Menu"
)

appbuilder.add_view(
    ScheduleView,
    "Schedules",
    icon="fa-folder-open-o",
    category="Menu"
)

appbuilder.add_view(
    RoundView,
    "Rounds",
    icon="fa-folder-open-o",
    category="Menu"
)

appbuilder.add_view(
    GameView,
    "Games",
    icon="fa-folder-open-o",
    category="Menu"
)

appbuilder.add_view(
    DrawView,
    "Draws",
    icon="fa-folder-open-o",
    category="Menu"
)

appbuilder.add_view(
    CreateScheduleView,
    "Schedule Generator",
    icon="fa-plus",
    category="Menu"
)
