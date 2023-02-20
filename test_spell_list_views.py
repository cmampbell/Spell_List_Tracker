'''Spell list views tests'''

import os
from unittest import TestCase

from models import db, User, Character, Stats, Char_Class, Spell

os.environ['DATABASE_URL'] = 'postgresql:///spell-tracker-test'

from app import app

test_password = 'HASHED_PASSWORD'

class SpellListViewsTestCase(TestCase):
    '''Testing the character model methods'''
    def setUp(self):
        Character.query.delete()
        User.query.delete()
        Spell.query.delete()

        self.user = User(
            email="test@hotmail.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        self.stats = Stats(            
            HP=10,
            STR=10,
            DEX=10,
            CON=10,
            INT=10,
            WIS=10,
            CHA=10
        )

        db.session.add(self.user)
        db.session.commit()

        self.char = Character(
            name='TestChar',
            user_id=self.user.id
        )

        char_class = Char_Class(class_id=4, level=4)

        self.char.classes.append(char_class)
        self.char.stats = self.stats

        self.spell1 = Spell(index='cure-wounds', name='Cure Wounds', level=1)
        self.spell2 = Spell(index='guidance', name='Guidance', level=0)
        db.session.add(self.spell1)
        db.session.add(self.spell2)
        db.session.add(self.char)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_new_spell_list_get(self):
        '''Does the new spell list view function return correct info'''
        with self.client as client:
            login = {'username': self.user.username, 'password':test_password}
            client.post('/login', data=login)

            resp = client.get(f'/char/{self.char.id}/spell_list/new')
            html = resp.get_data(as_text=True)

            self.assertIn('Cure Wounds', html)
            self.assertIn('Guidance', html)
