'''User model tests'''

import os
from unittest import TestCase

from models import db, User
from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = 'postgresql:///spell-tracker-test'

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    '''Test user model'''

    def setUp(self):
        '''Create test client'''

        User.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        '''Does basic user model work?'''

        user = User(
            email="test@hotmail.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(user)
        db.session.commit()

        #User should have test data
        self.assertEqual(user.email,"test@hotmail.com")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.password, "HASHED_PASSWORD")

        #User __repr__ method returns correct value
        self.assertIn(str(user.id), user.__repr__())
        self.assertIn(user.email, user.__repr__())
        self.assertIn(user.username, user.__repr__())