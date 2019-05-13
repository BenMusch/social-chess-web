from flask import render_template
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, ModelRestApi
from . import appbuilder, db
from app.models import Player, Tournament, Schedule, Round, Draw, Game

"""
    Create your Model based REST API::

    class MyModelApi(ModelRestApi):
        datamodel = SQLAInterface(MyModel)

    appbuilder.add_api(MyModelApi)


    Create your Views::


    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)


    Next, register your Views::


    appbuilder.add_view(
        MyModelView,
        "My View",
        icon="fa-folder-open-o",
        category="My Category",
        category_icon='fa-envelope'
    )
"""

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