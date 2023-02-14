'''User view function tests'''
#test with python -m unittest test_user_views.py

import os
from unittest import TestCase
from flask import session

from models import db, User

os.environ['DATABASE_URL'] = 'postgresql:///spell-tracker-test'

from app import app, CURR_USER_KEY

app.app_context().push()

db.create_all()

#disable WTForms csrf for testing
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True

test_password = 'HASHED_PASSWORD'

class UserViewTestCase(TestCase):
    '''Test views for users'''

    def setUp(self):
        '''Create test client, add sample data'''
        User.query.delete()

        self.client = app.test_client()
        user = User.signup(
            username='test_user',
            password= test_password,
            email='test@hotmail.com'
        )
        db.session.commit()

        self.user = user

    def tearDown(self) -> None:
        db.session.rollback()
    
    def test_user_signup(self):
        '''Does the sign-up route work as intended?'''
        with self.client as client:
            data = {
                'username': 'testuser2', 
                'email':'test2@hotmail.com', 
                'password': test_password,
                'confirm': 'HASHED_PASSWORD'
                }
                
            resp = client.post("/signup", data=data)

            # check that status code is redirect
            self.assertEqual(resp.status_code, 302)

            # check that user has been added to database and session
            self.assertIsNotNone(session.get(CURR_USER_KEY))
            self.assertEqual(len(User.query.all()), 2)

            testuser = db.session.get(User, session[CURR_USER_KEY])

            self.assertEqual(testuser.username, data['username'])

    def test_user_login(self):
        '''Does the user log in method work?'''

        with self.client as client:
            data={
                'username': self.user.username,
                'password': test_password
                }
            resp = client.post('/login', data=data)

            #check status code is redirect
            self.assertEqual(resp.status_code, 302)

            #check that current user in session matched our user id
            self.assertEqual(session.get(CURR_USER_KEY), self.user.id)

    def test_user_logout(self):
        '''Test user logout method'''

        with self.client as client:
            # do login
            # session_transaction seemed to work on a seperate session
            # do_logout() did not see session_transaction session
            data={
                'username': self.user.username,
                'password': test_password
                }
            client.post('/login', data=data)
        
            resp = client.get('/logout')

            #check that we get ok status code
            self.assertEqual(resp.status_code, 302)

            #check that current user is removed from session
            self.assertIsNone(session.get(CURR_USER_KEY))


