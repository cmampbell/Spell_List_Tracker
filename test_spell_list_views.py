'''Spell list views tests'''

import os
from unittest import TestCase

from models import db, User, Character, Stats, Char_Class, Spell, SpellList

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
        SpellList.query.delete()

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

    def test_new_spell_list_post(self):
        '''Does the new spell list post route work as intended'''
        with self.client as client:
            login = {'username': self.user.username, 'password':test_password}
            client.post('/login', data=login)

            data = {'spells': [self.spell1.id, self.spell2.id], 'name': 'test_spell_list'}

            resp = client.post(f'/char/{self.char.id}/spell_list/new', data=data)

            spell_list = self.char.spell_lists

            #check that we get redirect
            self.assertEqual(resp.status_code, 302)

            #check that a new spell list was added to the character
            self.assertIsNotNone(spell_list)
            self.assertEqual(len(self.char.spell_lists), 1)
            self.assertEqual(self.char.id, spell_list[0].char_id)

            spells = [spell.id for spell in spell_list[0].spells]

            #check that the spells are in the list
            self.assertIn(self.spell1.id, spells)
            self.assertIn(self.spell2.id, spells)

    def add_spell_list_to_char(self):
        '''Add spell lists to self.character'''
        spell_list = SpellList(char_id=self.char.id, name='Test Spell List')
        db.session.add(spell_list)
        db.session.commit()

        spells = Spell.query.all()

        [spell_list.spells.append(spell) for spell in spells]
        db.session.commit()

    def test_show_spell_list_details(self):
        '''Does the show spell list view show the correct list?'''
        self.add_spell_list_to_char()
        with self.client as client:
            login = {'username': self.user.username, 'password':test_password}
            client.post('/login', data=login)

            resp = client.get(f'/char/{self.char.id}/spell_list/{self.char.spell_lists[0].id}')
            html = resp.get_data(as_text=True)

            spell_list = self.char.spell_lists[0]

            #check that we get an ok status code
            self.assertEqual(resp.status_code, 200)

            #check that the char is mentioned on the page
            self.assertIn(self.char.name, html)

            #check that the spell list name is mentioned
            self.assertIn(spell_list.name, html)

            #check that the spells are on the page
            self.assertIn(spell_list.spells[0].name, html)
            self.assertIn(spell_list.spells[1].name, html)

    def test_delete_spell_list(self):
        '''Does the delete spell list view delete a spell list?'''
        self.add_spell_list_to_char()
        with self.client as client:
            login = {'username': self.user.username, 'password':test_password}
            client.post('/login', data=login)

            resp = client.post(f'/spell_list/{self.char.spell_lists[0].id}/delete')

            #check that we get a redirect status code
            self.assertEqual(resp.status_code, 302)

            #check that chars spell list is length 0
            self.assertEqual(len(self.char.spell_lists), 0)