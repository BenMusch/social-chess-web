from flask_appbuilder import Model
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from . import appbuilder, db

"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""

class Tournament(db.Model):
    """
    A tournament is the top-level object
    """
    id = db.Column(db.Integer, primary_key=True)
    schedule = relationship("Schedule", uselist=False, back_populates="tournament")
    playoff_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    winner_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    title = db.Column(db.String(80), unique=True, nullable=False)


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
        return "<Player {}>".format(self.name)


class Game(db.Model):
    """
    The game class is the heart of the system. Many other
    tables refer to it.
    """
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.Integer, default=0)
    player_one_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    player_one_draw_id = db.Column(db.Integer, db.ForeignKey('draw.id'))
    player_two_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    player_two_draw_id = db.Column(db.Integer, db.ForeignKey('draw.id'))
    color_code = db.Column(db.Integer, default=0)
    bye = db.Column(db.Boolean, default=False)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'))

    def __repr__(self):
        return "<Game: {} vs {} Result: {} >".format(self.player_one_id, self.player_two_id, self.result)


class Schedule(db.Model):
    """
    A schedule is just a collection of rounds
    who have games
    """
    tournament = relationship("Tournament", uselist=False, back_populates="schedule")
    tournament_id = db.Column(Integer, ForeignKey('tournament.id'))
    id = db.Column(db.Integer, primary_key=True)
    rounds = db.relationship('Round', backref='schedule')


class Round(db.Model):
    """
    A Round is just a collection of games in a tournament
    and it's kept simple
    """
    id = db.Column(db.Integer, primary_key=True)
    round_number = db.Column(db.Integer, default=1)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'))
    games = relationship("Game", backref='schedule')

    def __repr__(self):
        return "<Round: {} For Schedule {}>".format(self.round_number, self.schedule_id)


class Draw(db.Model):
    """
    A draw is just a shortcut table that has
    the player's games for a particular tournament
    """
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))


db.create_all()
