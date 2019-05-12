from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from . import appbuilder, db

"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""


class Player(db.Model):
    """
    The player class doesn't reference any other tables. It is liked
    to other tables through join tables. But you can't jump from
    player to anywhere else.
    """
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    affiliation = db.Column(db.String(120), unique=True, nullable=True)
    level = db.Column(db.Integer)
    vip = db.Column(db.Boolean)

    def __repr__(self):
        return "<Player {}>".format(self.name)
