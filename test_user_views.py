'''User view function tests'''

import os
from unittest import TestCase
from flask import session

from models import db, connect_db, User

os.environ['DATABASE_URL'] = 'postgresql:///spell-tracker-test'

from app import app, CURR_USER_KEY

db.create_all()

#disable WTForms csrf for testing
app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    '''Test views for users'''

    def setUp(self):
        '''Create test client, add sample data'''
        User.query.delete()

        self.client = app.test_client()

    def test_user_signup(self):
        '''Does the sign-up route work as intended?'''
        with self.client as client:
            d = {
                'username': 'testuser', 
                'email':'test@hotmail.com', 
                'password': 'HASHED_PASSWORD',
                'confirm': 'HASHED_PASSWORD'}
            resp = client.post(f"/signup", data=d, follow_redirects=True)

            #check that status code is ok
            self.assertEqual(resp.status_code, 200)

            #check that user has been added to database and session
            self.assertIsNotNone(session.get('curr_user'))
            self.assertEqual(len(User.query.all()), 1)


