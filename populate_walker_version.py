from database import engine, metadata, users, dogs, walker_requests

walker_id = 200360257

metadata.drop_all(engine)
metadata.create_all(engine)

engine.execute(users.insert().values(
    id=walker_id,
    username='TafarelYan',
    user_type='passeador',
    first_name='Tafarel',
    last_name='Yan',
    age=22,
    gender='Masculino',
    approved=True,
))

engine.execute(users.insert().values(
    id=123,
    username='DonaldDuck',
    user_type='dono',
    first_name='Donald',
    last_name='Duck',
    age=18,
    gender='Masculino',
    approved=True,
))

engine.execute(users.insert().values(
    id=1234,
    username='MinnieMouse',
    user_type='dono',
    first_name='Minnie',
    last_name='Mouse',
    age=19,
    gender='Feminino',
    approved=True,
))

engine.execute(dogs.insert().values(
    name='Tykows',
    breed='Golden Retriever',
    owner_id=123,
    age=5,
))

engine.execute(dogs.insert().values(
    name='Zeus',
    breed='Corgui',
    owner_id=1234,
    age=2,
))

engine.execute(walker_requests.insert().values(
    owner_id=123,
    walker_id=200360257,
    dog_id=1,
))

engine.execute(walker_requests.insert().values(
    owner_id=1234,
    walker_id=200360257,
    dog_id=2,
))
