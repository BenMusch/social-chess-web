from flask_appbuilder import Model
import chessnouns
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from . import appbuilder, db


class Tournament(db.Model):
    """
    A tournament is the top-level object
    """
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'))
    playoff_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    winner_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    title = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return "<Tournament {}>".format(self.title)


class Player(db.Model):
    """
    The player class doesn't reference any other tables. It is liked
    to other tables through join tables. But you can't jump from
    player to anywhere else.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    affiliation = db.Column(db.String(120), unique=False, nullable=True)
    level = db.Column(db.Integer, default=1)
    vip = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return str(self.name)


class Game(db.Model):
    """
    The game class is the heart of the system. Many other
    tables refer to it.
    """
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.Integer, default=0)
    player_one_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    player_one = relationship("Player", foreign_keys=[player_one_id])
    player_one_draw_id = db.Column(db.Integer, db.ForeignKey('draw.id'))
    player_two_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    player_two = relationship("Player", foreign_keys=[player_two_id])
    player_two_draw_id = db.Column(db.Integer, db.ForeignKey('draw.id'))
    color_code = db.Column(db.Integer, default=0)
    bye = db.Column(db.Boolean, default=False)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'))

    def outcome(self):

        # First test for bye

        if self.result == chessnouns.NO_RESULT:
            return "No result"
        elif self.result == chessnouns.WHITE_WINS:
            return "White wins"
        elif self.result == chessnouns.BLACK_WINS:
            return "Black wins"
        else:
            return "Draw"

    def round_number(self):
        current_round = db.session.query(Round).get(self.round_id)
        return str(current_round.round_number)

    def first_player(self):
        """
        This method is here to add the color code to the player name
        if we have it. It just returns the name if we do not, but the color
        letter appended if we do have it
        """
        first_player = db.session.query(Player).get(self.player_one_id)
        if not first_player:
            return "Bye"
        name_string = first_player.name

        if self.color_code == chessnouns.NO_COLOR_SELECTED:
            return name_string
        elif self.color_code == chessnouns.PLAYER_ONE_IS_WHITE:
            return name_string + " (White)"
        else:
            return name_string + " (Black)"

    def second_player(self):
        """
        This method is here to add the color code to the player name
        if we have it. It just returns the name if we do not, but the color
        letter appended if we do have it
        """

        if self.player_two_id is None:
            return "Bye"
        second_player = db.session.query(Player).get(self.player_two_id)

        name_string = second_player.name

        if self.color_code == chessnouns.NO_COLOR_SELECTED:
            return name_string
        elif self.color_code == chessnouns.PLAYER_ONE_IS_BLACK:
            return name_string + " (White)"
        else:
            return name_string + " (Black)"


    def __repr__(self):
        return "<Game: {} vs {} Result: {} >".format(self.first_player, self.second_player(), self.outcome())


class Schedule(db.Model):
    """
    A schedule is just a collection of rounds
    who have games
    """
    tournament_id = db.Column(Integer, ForeignKey('tournament.id'))
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    rounds = relationship('Round', backref='schedule')

    def __repr__(self):
        return "Schedule {}".format(self.title)


class Round(db.Model):
    """
    A Round is just a collection of games in a tournament
    and it's kept simple. We don't need a base class
    """
    id = db.Column(db.Integer, primary_key=True)
    round_number = db.Column(db.Integer, default=1)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'))
    games = relationship("Game", backref='schedule')

    def __repr__(self):
        schedule = db.session.query(Schedule).get(self.schedule_id)
        title = "No schedule"
        if schedule:
            title = schedule.title

        return "R: {} In {}".format(self.round_number, title)


class Draw(db.Model):
    """
    A draw is just a shortcut table that has
    the player's games for a particular tournament
    """
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))


db.create_all()
