'''Character model tests'''

import os
from unittest import TestCase

from models import db, User, Character, Stats
from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = 'postgresql:///spell-tracker-test'

from app import app

db.create_all()

class CharacterModelTestCase(TestCase):
    '''Test Character Model'''
    def setUp(self):
        User.query.delete()
        Character.query.delete()

        self.client = app.test_client()

        self.user = User(
            email="test@hotmail.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(self.user)
        db.session.commit()

    def test_new_character(self):
        '''Does the character model work as intended?'''

        char = Character(
            name='TestChar',
            user_id=self.user.id
        )

        db.session.add(char)
        db.session.commit()

        #check that char object name is correct
        self.assertEqual(char.name, 'TestChar')

        #check that char is assigned an id
        self.assertIsNotNone(char.id)

        #check that user id is correct
        self.assertEqual(char.user_id, self.user.id)

    def test_character_user_integration(self):
        '''Do the chracter and user classes work as intended?'''

        char = Character(
            name='TestChar',
            user_id=self.user.id
        )

        self.user.characters.append(char)

        #check that the character is in user.characters
        self.assertEqual(len(self.user.characters), 1)
        self.assertIn(char, self.user.characters)

        #check that get_classes returns None when the character has no classes
        self.assertIsNone(char.get_classes())



class StatsModelTestCase(TestCase):
    '''Testing Stats Model'''

    def setUp(self):
        User.query.delete()
        Character.query.delete()

        self.client = app.test_client()

        self.user = User(
            email="test@hotmail.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        self.char = Character(
            name='TestChar',
            user_id=self.user.id
        )

        db.session.add(self.user)
        db.session.commit()

    def test_stats_model(self):
        '''Testing the stats model'''

        stats = Stats(            
            HP=10,
            STR=10,
            DEX=10,
            CON=10,
            INT=10,
            WIS=10,
            CHA=10
        )

        self.char.stats = stats
        db.session.commit()

        #check that the character has stats
        self.assertIsNotNone(self.char.stats)

        #check that serialize stats returns a dict
        self.assertTrue(isinstance(stats.serialize_stats(), dict))

        stat_dict = stats.serialize_stats()
        #check that serialize stats contains all field needed
        self.assertIn('HP', stat_dict)
        self.assertIn('STR', stat_dict)
        self.assertIn('DEX', stat_dict)
        self.assertIn('CON', stat_dict)
        self.assertIn('INT', stat_dict)
        self.assertIn('WIS', stat_dict)
        self.assertIn('CHA', stat_dict)