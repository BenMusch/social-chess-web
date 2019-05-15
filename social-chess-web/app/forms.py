from flask_appbuilder.forms import DynamicForm
from wtforms import widgets, fields, validators

from app.models import Player, Tournament
from app import db
import chessnouns


class MultiCheckboxField(fields.SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.

    Taken from: https://wtforms.readthedocs.io/en/stable/specific_problems.html#specialty-field-tricks
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


def _get_choices(model_type, get_label=lambda obj: obj.name):
    """
    Return id + name tuples to format them as WTForm-style choices in a multi-select
    input
    """
    return [ (obj.id, get_label(obj)) for obj in db.session.query(model_type).all() ]


def get_enum_field(enum_choices, default=None):
    return fields.SelectField(
        choices=enum_choices,
        coerce=int,
        default=default,
        validators=[validators.required()]
    )


class ScheduleForm(DynamicForm):
    """
    Custom form to create a schedule with a given selection of players
    """
    tournament = fields.SelectField(
        choices=_get_choices(Tournament, lambda t: t.title),
        coerce=int,
        validators=[validators.required()]
    )
    name = fields.StringField(u"Schedule name:", [validators.required()])
    num_rounds = fields.IntegerField(
        u"Number of rounds:",
        [validators.required()],
        default=chessnouns.DEFAULT_NUMBER_OF_ROUNDS
    )
    players = MultiCheckboxField(choices=_get_choices(Player), coerce=int)


    def __init__(self, *args, **kwargs):
        """
        Overried __init__ to re-initialize the players field with all of the current
        players. Otherwise, it only loads choices when the app first runs
        """
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.players.choices = _get_choices(Player)
        self.tournament.choices = _get_choices(Tournament, lambda t: t.title)
