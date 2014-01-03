#!/usr/bin/env python

# Helper script that imports trades from csv after model changes

from app import db, models
import csv

with open('db_backup.txt', 'rb') as f:
    csvreader = csv.reader(f)
    for row in csvreader:
        u = models.User.query.get(int(row[0]))
        t = models.Trade(
            owner=u,
            dex_no=row[1],
            species=row[2],
            gender=row[3],
            count=row[4],
            nature=row[5],
            ability=row[6],
            iv_hp=row[7],
            iv_atk=row[8],
            iv_def=row[9],
            iv_spa=row[10],
            iv_spd=row[11],
            iv_spe=row[12],
            move1=row[13],
            move2=row[14],
            move3=row[15],
            move4=row[16],
        )
        db.session.add(t)

db.session.commit()
