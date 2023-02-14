import requests
from sqlalchemy import insert

from app import db
from models import Classes, Subclasses

db.drop_all()
db.create_all()

resp = requests.get('https://www.dnd5eapi.co/api/classes')

class_list = resp.json()['results']
subclass_list = []
i = 0
for _class in class_list:
    resp = requests.get(f'https://www.dnd5eapi.co/api/classes/{_class["index"]}/subclasses')
    subclass_list.append(resp.json()['results'][0])
    subclass_list[i]['parent_class'] = _class['index']
    i += 1

db.session.execute(insert(Classes), class_list)
db.session.execute(insert(Subclasses), subclass_list)
db.session.commit()