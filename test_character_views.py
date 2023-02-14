'''Character views tests'''

import os
from unittest import TestCase

from models import db, User, Character
from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = 'postgresql:///spell-tracker-test'

from app import app, CURR_USER_KEY

app.app_context().push()

db.create_all()

#disable WTForms csrf for testing
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True

test_password = 'HASHED_PASSWORD'

class CharacterViewsTestCase(TestCase):
    '''Tests for character view functions'''

    def setUp(self):
        User.query.delete()

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
            # with client.session_transaction() as session:
            login = {'username': 'testuser', 'password':'HASHED_PASSWORD'}
            client.post('/login', data=login)

            resp = client.get('/characters/new')

            #check that we get an ok response code
            self.assertEqual(resp.status_code, 200)

            data = { 'name': 'test_char', 'HP': '5', 'STR': 5,
                    'CON': 5, 'INT': 5, 'WIS': 5, 'CHA': 5, 
                    'class_name': 'Druid', 'subclass_name': 'Land', 'level': 2 }

            resp = client.post('/characters/new', data=data)

            #check that we get an ok status code
            self.assertEqual(resp.status_code, 302)

            #check that only one character was added to the user
            self.assertEqual(len(self.user.characters), 1)

            char =  db.session.get(Character, self.user.characters[0].id)

            #check that the character name is equal to the data attribute
            self.assertEqual(char.name, 'test_char')

            #check that character user id is equal to user id session
            # self.assertEqual(session[CURR_USER_KEY], char.user_id)



            
