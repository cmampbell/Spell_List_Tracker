'''Spell list views tests'''

import os
from unittest import TestCase

from models import db, User, Character, Stats, Char_Class, Spell

os.environ['DATABASE_URL'] = 'postgresql:///spell-tracker-test'

from app import app

app.app_context().push()

#disable WTForms csrf for testing
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True

test_password = 'HASHED_PASSWORD'

class SpellListViewsTestCase(TestCase):
    '''Testing the character model methods'''
    def setUp(self):
        Character.query.delete()
        User.query.delete()
        Spell.query.delete()

        self.client = app.test_client()

        self.user = User.signup(
            username='test_user',
            password= test_password,
            email='test@hotmail.com'
        )

        db.session.commit()

        self.stats = Stats(            
            HP=10,
            STR=10,
            DEX=10,
            CON=10,
            INT=10,
            WIS=10,
            CHA=10
        )

        self.char = Character(
            name='TestChar',
        )

        self.user.characters.append(self.char)

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

            #do we get an ok status code
            self.assertEqual(resp.status_code, 200)

            self.assertIn('Cure Wounds', html)
            self.assertIn('Guidance', html)
            self.assertIn(f'<option value="{self.spell1.id}"', html)

    # def test_new_spell_list_post(self):
    #     '''Does the new spell list post route work as intended'''
    #     with self.client as client:
    #         login = {'username': self.user.username, 'password':test_password}
    #         client.post('/login', data=login)

    #         resp
