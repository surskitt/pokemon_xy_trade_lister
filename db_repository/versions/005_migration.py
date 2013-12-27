from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
trade = Table('trade', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('dex_no', Integer),
    Column('species', String(length=30)),
    Column('gender', String(length=6)),
    Column('count', Integer),
    Column('nature', String(length=30)),
    Column('ability', String(length=30)),
    Column('iv_hp', Integer),
    Column('iv_atk', Integer),
    Column('iv_def', Integer),
    Column('iv_spa', Integer),
    Column('iv_spd', Integer),
    Column('iv_spe', Integer),
    Column('move1', String(length=30)),
    Column('move2', String(length=30)),
    Column('move3', String(length=30)),
    Column('move4', String(length=30)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['trade'].columns['gender'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['trade'].columns['gender'].drop()
