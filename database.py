from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, MetaData

engine = create_engine('sqlite:///petwalk.sqlite')

metadata = MetaData()

users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String),
    Column('first_name', String),
    Column('last_name', String),
    Column('is_owner', Boolean),
    Column('is_walker', Boolean),
    Column('photo_url', String),
    Column('age', Integer),
    Column('gender', String),
    Column('approved', Boolean),
)

dogs = Table('dogs', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('breed', String),
    Column('photo_url', String),
    Column('owner_id', ForeignKey('users.id')),
    Column('age', String),
)

tracking = Table('tracking', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String),
)

metadata.create_all(engine)
