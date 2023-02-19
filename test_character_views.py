'''Character views tests'''

import os
from unittest import TestCase
from flask import session

from models import db, User, Character, Stats, Char_Class
from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = 'postgresql:///spell-tracker-test'

from app import app, CURR_USER_KEY, add_user_to_g, g
# from seed import seed_db_classes

app.app_context().push()

# only needed to seed initial db
# db.drop_all()
# db.create_all()
# seed_db_classes()

#disable WTForms csrf for testing
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True

test_password = 'HASHED_PASSWORD'

class CharacterCreationViewsTestCase(TestCase):
    '''Tests for character view functions'''

    def setUp(self):
        User.query.delete()
        Character.query.delete()

        self.client = app.test_client()

        self.user = User.signup(
            username='test_user',
            password= test_password,
            email='test@hotmail.com'
        )

        db.session.add(self.user)
        db.session.commit()


    def test_new_char_form(self):
        '''Does show character form render correct fields'''
        with self.client as client:
            login = {'username': self.user.username, 'password':test_password}
            client.post('/login', data=login)

            resp = client.get('/characters/new')

            #check that we get an ok response code
            self.assertEqual(resp.status_code, 200)

    def test_new_char_form_submit(self):
        '''Is a new character created and attached to the current user
        after a post request?'''
        with self.client as client:
                
            login = {'username': self.user.username, 'password':test_password}
            client.post('/login', data=login)

            data = { 'name': 'test_char', 'HP': 5, 'STR': 5, 'DEX': 5,
                    'CON': 5, 'INT': 5, 'WIS': 5, 'CHA': 5, 
                    'class_id': 3, 'level': 2 }

            resp = client.post('/characters/new', data=data)

            #check that we get an ok status code
            self.assertEqual(resp.status_code, 302)

            #check that only one character was added to the user
            self.assertEqual(len(self.user.characters), 1)

            char =  db.session.get(Character, self.user.characters[0].id)

            #check that the character name is equal to the data attribute
            self.assertEqual(char.name, 'test_char')

            #check that character user id is equal to user id session
            self.assertEqual(session[CURR_USER_KEY], char.user_id)

    def create_test_character(self):
        '''Create a chracter to use in details and edit tests'''
        char_data = { 'name': 'test_char' } 
        stat_data = { 'HP': 5, 'STR': 5, 'DEX': 5, 'CON': 5, 'INT': 5, 'WIS': 5, 'CHA': 5} 
        class_data= { 'class_id': 3, 'level': 2 }
        char = Character(**char_data)
        stats = Stats(**stat_data)
        char_class = Char_Class(**class_data)

        char.stats = stats
        char.classes.append(char_class)
        
        self.user.characters.append(char)
        db.session.commit()

        return char

    def test_show_char_details(self):
        '''Do character details show properly?'''
        char = self.create_test_character()

        with self.client as client:
            resp = client.get(f'/char/{char.id}')
            html = resp.get_data(as_text=True)

            #check to see we get an ok status code
            self.assertEqual(resp.status_code, 200)

            #check to see if the stats are on the page
            self.assertIn(char.name, html)
            self.assertIn(str(char.stats.HP), html)
            self.assertIn(char.classes[0].class_name.name, html)

    def test_char_edit_form(self):
        '''Does the edit form edit the character?'''

        char = self.create_test_character()

        data = { 'name': 'edit_test', 'HP': 10, 'STR': 5, 'DEX': 5,
                'CON': 5, 'INT': 5, 'WIS': 5, 'CHA': 5, 
                'class_name': 'Wizard', 'subclass_name': '', 'level': 2 }

        with self.client as client:
            login = {'username': self.user.username, 'password':test_password}
            client.post('/login', data=login)

            resp = client.post(f'/char/{char.id}/edit', data=data)

            #check that we get a redirect
            self.assertEqual(resp.status_code, 302)

            #check that the char is edited with new values
            self.assertEqual(char.name, 'edit_test')
            self.assertEqual(char.stats.HP, 10)

    def test_char_delete(self):
        '''Does delete character view delete the character?'''
        char = self.create_test_character()

        with self.client as client:
            login = {'username': self.user.username, 'password':test_password}
            client.post('/login', data=login)

            resp = client.post(f'/char/{char.id}/delete')

            #check that we got a redirect
            self.assertEqual(resp.status_code, 302)

            #check that user doesn't have a character anymore
            self.assertEqual(len(self.user.characters), 0)