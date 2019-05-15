import argparse
import csv

from app import db
from app.models import Player

parser = argparse.ArgumentParser(description='Import players as csv of first,last,level')
parser.add_argument('file', type=str)

args = parser.parse_args()

with open(args.file) as f:
    reader = csv.reader(f)
    for row in reader:
        first, last, level = row
        name = "%s %s" % (first, last)
        query = db.session.query(Player).filter_by(name=name)
        if query.first():
            player = query.first()
            if player.level != int(level):
                print("Updating %s from %s to %s" % (name, player.level, level))
                player.level = int(level)
                db.session.add(player)
                db.session.commit()
            else:
                print("Player %s is unchanged" % name)
        else:
            player = Player(name=name, level=int(level))
            print("Creating %s with level %s" % (name, level))
            db.session.add(player)
            db.session.commit()
print("Done!")
