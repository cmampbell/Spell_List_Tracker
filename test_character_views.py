'''Character views tests'''

import os
from unittest import TestCase

from models import db, User, Character
from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = 'postgresql:///spell-tracker-test'

from app import app

db.create_all()

class CharacterViewsTestCase(TestCase):
    '''Tests for character view functions'''

    def setUp(self):
        User.query.delete()

        self.client = app.test_client()

        self.user = User(
            email="test@hotmail.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(self.user)
        db.session.commit()