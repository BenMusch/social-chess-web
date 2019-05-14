from flask_appbuilder.forms import DynamicForm
from wtforms import widgets, fields

from app.models import Player
from app import db


class MultiCheckboxField(fields.SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.

    Taken from: https://wtforms.readthedocs.io/en/stable/specific_problems.html#specialty-field-tricks
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


def _get_player_choices():
    """
    Return id + name tuples to format them as WTForm-style choices in a multi-select
    input
    """
    return [ (player.id, player.name) for player in db.session.query(Player).all() ]


class ScheduleForm(DynamicForm):
    """
    Custom form to create a schedule with a given selection of players
    """
    players = MultiCheckboxField(choices=_get_player_choices(), coerce=int)

    def __init__(self, *args, **kwargs):
        """
        Overried __init__ to re-initialize the players field with all of the current
        players. Otherwise, it only loads players when the app first runs
        """
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.players.choices = _get_player_choices()
