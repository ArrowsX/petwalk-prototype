from pony.orm import *

db = Database()

class User(db.Entity):
    first_name = Required(str)
    last_name = Required(str)
    is_owner = Required(int)
    is_walker = Required(int)
    photo_url = Required(str)
    region = Required(str)
    age = Required(int)
    gender = Required(str)
    email = Required(str)
    approved = Required(int)

class Dog(db.Entity):
    name = Required(str)
    breed = Required(str)
    photo_url = Required(str)
    owner_id = Required(int)
    age = Required(int)

db.bind('sqlite', 'petwalk.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

@db_session
def test_data():
    u1 = User(id=123, first_name='Mickey', last_name='Mouse', is_owner=1,
              is_walker=0, photo_url='http://i.imgur.com/89ywcp7.jpg',
              region='Disney', age=18, gender='m', email='mickey@mouse.com',
              approved=1)
    d1 = Dog(name='Pluto', breed='BloodHound', owner_id=u1.id, age=8,
             photo_url='http://i.imgur.com/z6mz1In.png')
    u2 = User(id=321, first_name='Donald', last_name='Duck', is_owner=0,
              is_walker=1, photo_url='http://i.imgur.com/Z2YTT5T.jpg',
              region='Disney', age=18, gender='m', email='donald@duck.com',
              approved=1)
