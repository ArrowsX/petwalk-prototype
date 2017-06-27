from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, MetaData

engine = create_engine('sqlite:///petwalk.db')

metadata = MetaData()

users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String),
    Column('user_type', String),
    Column('first_name', String),
    Column('last_name', String),
    Column('photo_id', String),
    Column('photo_url', String),
    Column('age', Integer),
    Column('gender', String),
    Column('approved', Boolean, default=False),
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

walker_requests = Table('walker_requests', metadata,
    Column('id', Integer, primary_key=True),
    Column('owner_id', Integer),
    Column('walker_id', ForeignKey('users.id')),
    Column('dog_id', ForeignKey('dogs.id')),
)

metadata.create_all(engine)
