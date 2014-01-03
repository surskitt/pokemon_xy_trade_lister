#!/usr/bin/env python

# Helper script that exports trades to csv before model changes

from app import models


def strOrBlank(m):
    if m is None:
        return ''
    else:
        return m

with open("db_backup.txt", "w") as f:
    for t in models.Trade.query.all():
        f.write(
            str(t.owner.id) + ',' +
            str(t.dex_no) + ',' +
            str(t.species) + ',' +
            str(t.gender) + ',' +
            str(t.count) + ',' +
            str(t.nature) + ',' +
            str(t.ability) + ',' +
            str(t.iv_hp) + ',' +
            str(t.iv_atk) + ',' +
            str(t.iv_def) + ',' +
            str(t.iv_spa) + ',' +
            str(t.iv_spd) + ',' +
            str(t.iv_spe) + ',' +
            strOrBlank(t.move1) + ',' +
            strOrBlank(t.move2) + ',' +
            strOrBlank(t.move3) + ',' +
            strOrBlank(t.move4) + '\n'
        )
