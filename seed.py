import requests
from sqlalchemy import insert

import pdb

from app import db
from models import Classes, Subclasses, Spell

db.drop_all()
db.create_all()

def seed_db_classes():
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

def seed_db_spells():
    # classes = db.session.query(Classes).all()

    #get the list of spells from the API
    resp = requests.get('https://www.dnd5eapi.co/api/spells')

    #returns an array of dicts with spell names and url for individual request
    all_spells = resp.json()['results']

    #we will use this to store the spells from our loop
    spell_list = []

    for url in [spell['url'] for spell in all_spells]:
        resp = requests.get(f'https://www.dnd5eapi.co{url}').json()

        if 'damage' in resp.keys():
            spell = Spell(index=resp['index'], name=resp['name'], range=resp['range'],
                    duration=resp['duration'], concentration=resp['concentration'], casting_time=resp['casting_time'],
                    level=resp['level'], damaging=True, healing=False, school=resp['school']['name'])
        elif 'heal_at_slot_level' in resp.keys():
            spell = Spell(index=resp['index'], name=resp['name'], range=resp['range'],
                    duration=resp['duration'], concentration=resp['concentration'], casting_time=resp['casting_time'],
                    level=resp['level'], healing=True, damaging=False, school=resp['school']['name'])
        else:
            spell = Spell(index=resp['index'], name=resp['name'], range=resp['range'],
                    duration=resp['duration'], concentration=resp['concentration'], casting_time=resp['casting_time'],
                    healing=False, damaging=False, level=resp['level'], school=resp['school']['name'])
        
        spell_list.append(spell)

    db.session.add_all(spell_list)
    db.session.commit()

seed_db_classes()
seed_db_spells()